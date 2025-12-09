import os
import re
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
from crewai import LLM, Agent, Task, Crew
from crewai_tools import CodeInterpreterTool

# --- Initialization ---

# Suppress warnings
os.environ['PYTHONWARNINGS'] = 'ignore'
load_dotenv()

# Initialize LLM
llm = LLM(
    model="gemini/gemini-2.5-flash-lite", 
    temperature=0.3,
    api_key=os.getenv("GOOGLE_API_KEY")
)

# Initialize Code Interpreter Tool
code_interpreter = CodeInterpreterTool()

# --- Agent Definitions ---

# Agent 1 — Explains data & suggests questions
insight_agent = Agent(
    role="Data Insight Analyst",
    goal="Understand datasets and propose clear, natural-language questions to interpret and find insights. Avoid Common Terms, Only Suggest the questions in plain English. With the Features in the Dataset",
    backstory="A professional data analyst skilled at explaining data contextually & Expert in exlaining data to students where easy to ask questions & to find insights in the Data.",
    llm=llm,
    verbose=False
)

# Agent 2 — Generates and executes code
code_analyst_agent = Agent(
    role="Senior Data Analyst & Python Developer",
    goal=(
        "Write and execute Python code to analyze datasets and answer user questions. "
        "Generate clear, executable code and interpret results meaningfully."
    ),
    backstory=(
        "You are an expert data analyst with deep knowledge of pandas, matplotlib, and seaborn. "
        "You write clean, efficient Python code and always explain your findings clearly. "
        "You use the CodeInterpreterTool to execute code and analyze real data."
    ),
    llm=llm,
    verbose=True,
    tools=[code_interpreter],
    allow_code_execution=True
)

# --- Model Functions ---

def get_dataset_explanation(df: pd.DataFrame) -> str:
    """
    Generate dataset explanation and suggested questions.
    """
    # Create a small, representative sample for the agent
    sample_frac = min(0.3, 1000 / len(df))
    sample = df.sample(frac=sample_frac, random_state=42)
    columns = ", ".join(sample.columns)
    desc = f"The dataset contains columns: {columns}."

    task = Task(
        description=(
            f"{desc}\n\n"
            "Based on the columns and data sample, explain briefly what the dataset represents "
            "and generate 8–10 plain English questions a user can ask to gain insights. "
            "Avoid SQL or technical terms."
        ),
        agent=insight_agent,
        expected_output="Explanation of the dataset and a list of insightful natural-language questions."
    )

    crew = Crew(agents=[insight_agent], tasks=[task], verbose=False)
    result = crew.kickoff()
    return result.raw if hasattr(result, "raw") else str(result)


def get_data_analysis(df: pd.DataFrame, query: str) -> dict:
    """
    Analyze query using CodeInterpreterTool.
    Returns a dictionary with text results and paths to plot files.
    """
    csv_path = "analysis_data.csv"
    df.to_csv(csv_path, index=False)
    
    # Get dataset context
    columns_list = df.columns.tolist()
    dtypes_info = {col: str(dtype) for col, dtype in df.dtypes.items()}
    shape_info = f"{df.shape[0]} rows × {df.shape[1]} columns"
    sample_data = df.head(5).to_string()
    
    # Create detailed task description
    task_description = f"""
USER QUESTION: {query}

DATASET CONTEXT:
- File: {csv_path}
- Shape: {shape_info}
- Columns: {columns_list}
- Data types: {dtypes_info}
- Sample data (first 5 rows):
{sample_data}

YOUR INSTRUCTIONS:
1. First, load the data: 
   import pandas as pd
   import matplotlib.pyplot as plt
   import seaborn as sns
   df = pd.read_csv('{csv_path}')

2. Write Python code to answer the question:
   - Use actual column names from the list above
   - Include print() statements to show key findings
   - Create visualizations if they help answer the question (use plt/sns)
   - **CRITICAL: Save any plots as PNG files (e.g., plt.savefig('plot_1.png'))**

3. Execute your code using the CodeInterpreterTool.

4. After execution, interpret the results:
   - Explain what the numbers/charts show
   - Answer the original question clearly

Now, write and execute the analysis code, then provide your interpretation.
"""

    task = Task(
        description=task_description,
        agent=code_analyst_agent,
        expected_output=(
            "Complete analysis including: "
            "(1) Python code executed, "
            "(2) Printed output/results, "
            "(3) Clear interpretation of findings answering the user's question."
        )
    )

    crew = Crew(
        agents=[code_analyst_agent],
        tasks=[task],
        verbose=True
    )
    
    # Execute analysis
    result = crew.kickoff()
    output_text = result.raw if hasattr(result, "raw") else str(result)
    
    # --- Process Results ---
    
    # Find all generated plot files
    plot_files = list(Path('.').glob('*.png'))
    plot_paths = [str(p) for p in plot_files]
    
    # Extract code blocks
    code_pattern = r'```(?:python)?\s*(.*?)```'
    code_blocks = re.findall(code_pattern, output_text, re.DOTALL)
    
    # Build a clean text response
    response_text = "### ✅ Analysis Complete\n\n"
    
    if code_blocks:
        response_text += "**Code Executed:**\n"
        for code in code_blocks:
            # Avoid adding the initial data loading code
            if f"pd.read_csv('{csv_path}')" not in code:
                response_text += f"```python\n{code.strip()}\n```\n\n"
    
    # Clean the output to get just the explanation
    interpretation = output_text
    interpretation = re.sub(code_pattern, '', interpretation, flags=re.DOTALL)
    interpretation = re.sub(r'(Action|Tool|Thought|Observation):.*?\n', '', interpretation, flags=re.DOTALL)
    interpretation = re.sub(r'\[.*?\]', '', interpretation)
    interpretation = re.sub(r'\n{3,}', '\n\n', interpretation)
    interpretation = interpretation.strip()

    if interpretation:
        response_text += "**AI Interpretation:**\n\n"
        response_text += interpretation

    # Clean up temp CSV
    try:
        if Path(csv_path).exists():
            Path(csv_path).unlink()
    except Exception as e:
        print(f"Warning: Could not delete temp file {csv_path}: {e}")
    
    return {
        "text_result": response_text,
        "plot_paths": plot_paths
    }