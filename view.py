import streamlit as st
import pandas as pd
import controller  # Import the controller logic

# --- Page Configuration ---
st.set_page_config(page_title="AI CSV Analyst", page_icon="📊", layout="centered")

st.title("🤖 AI-Powered Data Analyst")
st.write("Upload your CSV to get insights and ask natural questions about your data.")

# --- File Uploader ---
uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

# --- Main Application Logic ---
if uploaded_file:
    # On new file upload, clear old state and process new file
    if 'current_file_name' not in st.session_state or st.session_state.current_file_name != uploaded_file.name:
        st.session_state.clear() # Clear all session state
        st.session_state.current_file_name = uploaded_file.name
        
        try:
            with st.spinner("Analyzing your dataset..."):
                df, suggestions = controller.handle_file_upload(uploaded_file)
                st.session_state.df = df
                st.session_state.suggestions = suggestions
            st.success("✅ CSV uploaded successfully!")
        
        except Exception as e:
            st.error(f"❌ {e}")
            st.stop()

    # --- Display Data Preview and Suggestions ---
    if 'df' in st.session_state:
        df = st.session_state.df
        
        with st.expander("📋 Data Preview", expanded=False):
            st.dataframe(df.head(10))
            st.write(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
            st.write(f"**Columns:** {', '.join(df.columns.tolist())}")

        st.subheader("🧠 AI Insights & Suggested Questions")
        st.markdown(st.session_state.suggestions)

        # --- User Query Input ---
        st.subheader("💬 Ask a Question About Your Data")
        user_query = st.text_area(
            "Type one of the suggested questions or your own:",
            height=100,
            placeholder="Example: Which industries have seen the biggest increase in profit?"
        )

        if st.button("🔍 Analyze Data", type="primary"):
            if user_query.strip():
                st.divider()
                st.subheader("📈 Analysis Results")
                
                with st.spinner("🔄 Executing analysis... Please wait."):
                    try:
                        results = controller.handle_analysis_request(df, user_query)
                        # Store results in session state to persist
                        st.session_state.last_results = results 
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")
            else:
                st.warning("⚠️ Please enter a question to analyze your data.")

    # --- Display Results (if they exist in session state) ---
    if 'last_results' in st.session_state:
        results = st.session_state.last_results
        
        # Display text
        st.markdown(results["text_result"])
        
        # Display plots
        if results["plot_paths"]:
            st.markdown("**Visualization(s):**")
            for path in results["plot_paths"]:
                try:
                    st.image(path)
                except Exception as e:
                    st.warning(f"Could not display plot {path}: {e}")
            
            # Clean up plots after displaying
            controller.cleanup_temp_files(results["plot_paths"])
            # Clear plots from state to avoid re-displaying
            st.session_state.last_results["plot_paths"] = [] 

else:
    st.info("👆 Please upload a CSV file to begin analysis.")
    # Reset session state if file is removed
    if 'current_file_name' in st.session_state:
        st.session_state.clear()