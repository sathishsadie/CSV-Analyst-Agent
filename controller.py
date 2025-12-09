import pandas as pd
from pathlib import Path
import model  # Import the model logic

def handle_file_upload(uploaded_file):
    """
    Loads a file into a DataFrame and gets initial insights.
    """
    if uploaded_file is None:
        return None, None
        
    try:
        df = pd.read_csv(uploaded_file)
        suggestions = model.get_dataset_explanation(df)
        return df, suggestions
    except Exception as e:
        raise ValueError(f"Error loading CSV: {str(e)}")

def handle_analysis_request(df: pd.DataFrame, query: str):
    """
    Passes the analysis request to the model.
    """
    if not query.strip():
        raise ValueError("Query cannot be empty.")
        
    if df is None:
        raise ValueError("DataFrame not loaded.")
        
    results = model.get_data_analysis(df, query)
    return results

def cleanup_temp_files(plot_paths: list):
    """
    Removes temporary plot files after they have been displayed.
    """
    for path in plot_paths:
        try:
            Path(path).unlink()
        except Exception as e:
            print(f"Warning: Could not delete temp file {path}: {e}")