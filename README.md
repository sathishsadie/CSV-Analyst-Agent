# 📊 AI-Powered CSV Analyst

### *Ask questions about your CSV data using AI (CrewAI + Gemini) with a clean Streamlit UI.*

This project lets you upload any CSV file and interact with it using **natural language**.
You can ask the system to analyze, visualize, and interpret your data — automatically.

The backend uses:

* **CrewAI Agents** for reasoning & code execution
* **Gemini Flash Lite 2.5** as the LLM
* **Streamlit** as the interface
* **MVC-style structure** for clean architecture

---

# 🚀 Features

✔ Upload any CSV file
✔ Automatic dataset understanding
✔ Auto-generated smart questions
✔ Ask natural-language queries
✔ LLM-created Python code analysis
✔ Auto-generated charts (matplotlib)
✔ Clean and simple UI
✔ No technical knowledge needed

---

# 📂 Project Structure

```
📁 AI-CSV-Analyst
│── model.py          # AI logic, CrewAI agents, code interpreter
│── controller.py     # Connects UI with backend
│── view.py           # Streamlit app (UX/UI)
│── requirements.txt
│── README.md
│── .env.example
│── images/
│    └── system_setup.png   # optional
```

### ✔ **Model (`model.py`)**

* Builds CrewAI agents
* Runs Gemini for dataset insights
* Executes Python code safely
* Generates graphs

### ✔ **Controller (`controller.py`)**

* Passes data between view ↔ model
* Handles file uploads
* Manages responses & errors

### ✔ **View (`view.py`)**

* Streamlit interface
* File uploader
* Shows insights, charts, explanations

---

# 🛠️ Installation

## 1️⃣ Clone the project

```bash
git clone https://github.com/sathishsadie/CSV-Analyst-Agent.git
cd CSV-Analyst-Agent
```

## 2️⃣ Create virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

## 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

## 4️⃣ Create `.env` file

```
GOOGLE_API_KEY=your_api_key_here
```

(You can create a `.env.example` for others.)

## 5️⃣ Run the Streamlit app

```bash
streamlit run view.py
```

The app runs at:
👉 [http://localhost:8501/](http://localhost:8501/)

---
```markdown
![System Overview](https://github.com/sathishsadie/CSV-Analyst-Agent/blob/main/images/image.png)
```

---
