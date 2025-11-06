# app.py - Giao diện UI cho Hallucination Detection Research
# REQUIRE: pip install streamlit pandas plotly

import streamlit as st
import pandas as pd
import os
import json
import subprocess
import time
import importlib.util
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
sys.path.append(os.path.join(parent_dir, 'configs'))
sys.path.append(os.path.join(parent_dir, 'src'))
sys.path.append(os.path.join(parent_dir, 'ui'))

try:
    # Dynamic import cho config manager
    configs_path = os.path.join(parent_dir, 'configs', 'config_manager.py')
    spec = importlib.util.spec_from_file_location("config_manager", configs_path)
    config_manager_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_manager_module)
    ConfigManager = config_manager_module.ConfigManager
    
    # Import từ ui folder  
    from experiment_runner import ExperimentRunner  
    from components.analytics import create_metrics_comparison, create_hallucination_trend
    from components.enhanced_analytics import (
        load_all_existing_results, 
        create_api_comparison_chart,
        extract_hallucination_cases,
        create_hallucination_analysis_chart,
        create_detailed_metrics_table
    )
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Import config manager
# Remove duplicate import - already imported above
# from config_manager import ConfigManager, show_config_editor

# Configuration - Fix paths to work from UI directory  
DATA_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "data"
RESULTS_DIR = DATA_DIR / "results"
DATASETS_DIR = DATA_DIR

# API configurations
API_CONFIGS = {
    "OpenAI": {
        "script": "openai_run.py",
        "env_key": "OPENAI_API_KEY",
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        "color": "#00A67E"
    },
    "DeepSeek": {
        "script": "deepseek_run.py", 
        "env_key": "DEEPSEEK_API_KEY",
        "models": ["deepseek-chat", "deepseek-coder"],
        "color": "#FF6B6B"
    },
    "Gemini": {
        "script": "gemini_run.py",
        "env_key": "GOOGLE_API_KEY", 
        "models": ["gemini-1.5-flash", "gemini-1.5-pro"],
        "color": "#4285F4"
    },
    "Ollama": {
        "script": "run_ollama_eval.py",
        "env_key": None,  # Local, no API key needed
        "models": ["llama3.2", "qwen2", "mistral", "phi3"],
        "color": "#000000"
    }
}

def init_session_state():
    """Initialize session state variables"""
    if 'experiment_running' not in st.session_state:
        st.session_state.experiment_running = False
    if 'experiment_results' not in st.session_state:
        st.session_state.experiment_results = {}
    if 'selected_apis' not in st.session_state:
        st.session_state.selected_apis = []
    if 'selected_datasets' not in st.session_state:
        st.session_state.selected_datasets = []

def get_available_datasets():
    """Get list of available datasets from data folder"""
    datasets = []
    
    # Try to find the data directory
    data_paths = [
        DATASETS_DIR,
        Path("data"),
        Path("../data"),
        Path(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"))
    ]
    
    data_dir = None
    for path in data_paths:
        if path.exists():
            data_dir = path
            break
    
    if data_dir and data_dir.exists():
        for file in data_dir.glob("*.csv"):
            if file.stem not in ['train']:  # Exclude non-QA files
                datasets.append(file.name)
    
    return datasets

def check_api_availability():
    """Check which APIs have valid configuration using config manager"""
    config_path = os.path.join(parent_dir, "configs", "config.json")
    config_manager = ConfigManager(config_file=config_path)
    available_apis = {}
    
    # Get available APIs from config
    configured_apis = config_manager.get_available_apis()
    
    for api_name in ["openai", "deepseek", "gemini", "ollama"]:
        if api_name in configured_apis:
            available_apis[api_name.title()] = True
        else:
            available_apis[api_name.title()] = False
    
    return available_apis, config_manager

def run_experiment(api_name, model_name, dataset_name, progress_bar, status_text, config_manager):
    """Run experiment for specific API + dataset combination using unified APIRunner"""
    try:
        # Setup paths
        dataset_path = DATASETS_DIR / dataset_name
        result_dir = RESULTS_DIR / api_name.lower()
        result_dir.mkdir(parents=True, exist_ok=True)
        
        dataset_base = dataset_name.replace('.csv', '')
        raw_output = result_dir / f"results_raw_{dataset_base}.csv"
        graded_output = result_dir / f"results_graded_{dataset_base}.csv"
        metrics_output = result_dir / f"metrics_{dataset_base}.json"
        
        # Get API config
        api_config = config_manager.get_api_config(api_name.lower())
        if not api_config:
            return {"error": f"No configuration found for {api_name}"}
        
        # Step 1: Run inference using APIRunner
        status_text.text(f"🤖 Running {api_name} inference...")
        progress_bar.progress(0.3)
        
        # Import APIRunner từ src folder
        src_path = os.path.join(parent_dir, 'src', 'api_runner.py')
        spec = importlib.util.spec_from_file_location("api_runner", src_path)
        api_runner_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api_runner_module)
        APIRunner = api_runner_module.APIRunner
        
        # Initialize APIRunner
        api_key = api_config.get("api_key") if api_name.lower() != "ollama" else None
        runner = APIRunner(
            provider=api_name.lower(),
            model=model_name,
            api_key=api_key,
            base_url=api_config.get("base_url")
        )
        
        # Load dataset
        import pandas as pd
        if not dataset_path.exists():
            return {"error": f"Dataset not found: {dataset_path}"}
        
        df = pd.read_csv(dataset_path)
        
        # Detect question column (case-insensitive)
        question_col = None
        for col in df.columns:
            if col.lower() in ['question', 'q', 'query']:
                question_col = col
                break
        
        if question_col is None:
            return {"error": f"No question column found. Available columns: {list(df.columns)}"}
        
        # Detect answer column (case-insensitive)
        answer_col = None
        for col in df.columns:
            col_lower = col.lower()
            if col_lower in ["correct_answer", "ground_truth", "answer", "gold_answer", "best_answer", "best answer"]:
                answer_col = col
                break
            elif "answer" in col_lower and ("correct" in col_lower or "best" in col_lower or "gold" in col_lower):
                answer_col = col
                break
        
        if answer_col is None:
            return {"error": f"No answer column found. Available columns: {list(df.columns)}"}
        
        # Run experiments
        results = []
        total_questions = len(df)
        
        for idx, row in df.iterrows():
            question = row[question_col]
            correct_answer = row.get(answer_col, '')
            
            # Update progress
            progress = 0.3 + (idx / total_questions) * 0.4
            progress_bar.progress(progress)
            status_text.text(f"🤖 Processing question {idx+1}/{total_questions}")
            
            try:
                # Direct prompt
                direct_response = runner.run_direct_prompt(question)
                
                # Self-critique prompt  
                critique_response = runner.run_self_critique_prompt(question)
                final_answer = runner.extract_final_answer(critique_response)
                
                results.append({
                    'idx': idx + 1,  # Add index for evaluator
                    'question': question,
                    'answer': correct_answer,  # Gold answer 
                    'direct_answer': direct_response,  # Match evaluator expectation
                    'selfcrit_answer': critique_response,  # Full critique response
                    'selfcrit_final_span': final_answer,  # Extracted final answer
                    'api': api_name.lower(),
                    'model': model_name
                })
                
            except Exception as e:
                results.append({
                    'idx': idx + 1,
                    'question': question,
                    'answer': correct_answer,
                    'direct_answer': f"ERROR: {str(e)}",
                    'selfcrit_answer': f"ERROR: {str(e)}",
                    'selfcrit_final_span': f"ERROR: {str(e)}",
                    'api': api_name.lower(),
                    'model': model_name
                })
        
        # Save raw results
        results_df = pd.DataFrame(results)
        results_df.to_csv(raw_output, index=False)
        
        # Step 2: Evaluate responses
        status_text.text("📊 Evaluating responses...")
        progress_bar.progress(0.8)
        
        # Import evaluator từ src folder
        evaluator_path = os.path.join(parent_dir, 'src', 'evaluator.py')
        spec = importlib.util.spec_from_file_location("evaluator", evaluator_path)
        evaluator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(evaluator_module)
        HallucinationEvaluator = evaluator_module.HallucinationEvaluator
        
        evaluator = HallucinationEvaluator()
        
        # Evaluate and save graded results
        # Load original dataset for grading
        questions_df = pd.read_csv(dataset_path)
        
        # Grade responses
        graded_df = evaluator.grade_responses(results_df, questions_df)
        
        # Calculate metrics
        metrics = evaluator.calculate_metrics(graded_df)
        
        # Save graded results
        graded_df.to_csv(graded_output, index=False)
        
        # Save metrics
        with open(metrics_output, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Step 3: Generate report
        status_text.text("📄 Generating report...")
        progress_bar.progress(0.9)
        
        report_path = result_dir / f"report_{dataset_base}.docx"
        evaluator.generate_word_report(graded_df, metrics, str(report_path))
        
        progress_bar.progress(1.0)
        status_text.text("✅ Experiment completed!")
        
        return {
            "success": True,
            "raw_file": str(raw_output),
            "graded_file": str(graded_output),
            "metrics_file": str(metrics_output),
            "report_file": str(report_path),
            "metrics": metrics
        }
        
    except Exception as e:
        import traceback
        error_msg = f"Experiment failed: {str(e)}\n{traceback.format_exc()}"
        status_text.text(f"❌ Error: {str(e)}")
        return {"error": error_msg}

def create_metrics_chart(results_data):
    """Create comparison chart of metrics across APIs"""
    if not results_data:
        return None
    
    # Prepare data for plotting
    chart_data = []
    for (api, dataset), result in results_data.items():
        if "metrics" in result:
            metrics = result["metrics"]
            chart_data.append({
                "API": api,
                "Dataset": dataset,
                "Accuracy (Direct)": metrics.get("accuracy_direct", 0),
                "Accuracy (Self-Critique)": metrics.get("accuracy_selfcrit", 0),
                "Hallucination Rate (Direct)": metrics.get("hallu_rate_direct", 0),
                "Hallucination Rate (Self-Critique)": metrics.get("hallu_rate_selfcrit", 0),
                "Accuracy Gain": metrics.get("accuracy_gain", 0),
                "Hallucination Reduction": metrics.get("hallu_reduction", 0)
            })
    
    if not chart_data:
        return None
    
    df = pd.DataFrame(chart_data)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Accuracy Comparison", "Hallucination Rate", "Accuracy Gain", "Hallucination Reduction"),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Accuracy comparison
    for api in df["API"].unique():
        api_data = df[df["API"] == api]
        color = API_CONFIGS.get(api, {}).get("color", "#000000")
        
        fig.add_trace(
            go.Bar(name=f"{api} (Direct)", x=api_data["Dataset"], y=api_data["Accuracy (Direct)"], 
                   marker_color=color, opacity=0.7),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(name=f"{api} (Self-Critique)", x=api_data["Dataset"], y=api_data["Accuracy (Self-Critique)"], 
                   marker_color=color, opacity=1.0),
            row=1, col=1
        )
    
    # Hallucination rate
    for api in df["API"].unique():
        api_data = df[df["API"] == api]
        color = API_CONFIGS.get(api, {}).get("color", "#000000")
        
        fig.add_trace(
            go.Bar(name=f"{api} (Direct)", x=api_data["Dataset"], y=api_data["Hallucination Rate (Direct)"], 
                   marker_color=color, opacity=0.7, showlegend=False),
            row=1, col=2
        )
        fig.add_trace(
            go.Bar(name=f"{api} (Self-Critique)", x=api_data["Dataset"], y=api_data["Hallucination Rate (Self-Critique)"], 
                   marker_color=color, opacity=1.0, showlegend=False),
            row=1, col=2
        )
    
    # Accuracy gain
    for api in df["API"].unique():
        api_data = df[df["API"] == api]
        color = API_CONFIGS.get(api, {}).get("color", "#000000")
        
        fig.add_trace(
            go.Bar(name=api, x=api_data["Dataset"], y=api_data["Accuracy Gain"], 
                   marker_color=color, showlegend=False),
            row=2, col=1
        )
    
    # Hallucination reduction
    for api in df["API"].unique():
        api_data = df[df["API"] == api]
        color = API_CONFIGS.get(api, {}).get("color", "#000000")
        
        fig.add_trace(
            go.Bar(name=api, x=api_data["Dataset"], y=api_data["Hallucination Reduction"], 
                   marker_color=color, showlegend=False),
            row=2, col=2
        )
    
    fig.update_layout(height=600, title_text="Experiment Results Dashboard")
    
    return fig

def main():
    st.set_page_config(
        page_title="Hallucination Detection Research",
        page_icon="🧠",
        layout="wide"
    )
    
    init_session_state()
    
    # Header
    st.title("🧠 Hallucination Detection Research Dashboard")
    st.markdown("**Compare direct prompting vs self-critique prompting across multiple LLM APIs**")
    
    # Load existing results first
    st.header("📊 Existing Results Overview")
    
    # Try to load results with better path handling
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    existing_results = load_all_existing_results()
    
    if existing_results:
        st.success(f"Found {len(existing_results)} existing result sets")
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📈 API Comparison", "📋 Detailed Metrics", "⚠️ Hallucination Cases", "📄 Generate Reports"])
        
        with tab1:
            st.subheader("API Performance Comparison")
            comparison_chart = create_api_comparison_chart(existing_results)
            if comparison_chart:
                st.plotly_chart(comparison_chart, use_container_width=True)
            else:
                st.info("No comparison data available")
            
            # Hallucination analysis
            st.subheader("Hallucination Analysis by API")
            hallu_chart = create_hallucination_analysis_chart(existing_results)
            if hallu_chart:
                st.plotly_chart(hallu_chart, use_container_width=True)
        
        with tab2:
            st.subheader("Detailed Performance Metrics")
            metrics_table = create_detailed_metrics_table(existing_results)
            if metrics_table is not None:
                st.dataframe(metrics_table, use_container_width=True)
            else:
                st.info("No detailed metrics available")
        
        with tab3:
            st.subheader("Hallucination Cases Analysis")
            st.markdown("""
            **Hallucination Detection Logic:**
            - ✅ **Correct**: Answer matches gold standard  
            - ❓ **Uncertain**: Answer contains uncertainty expressions (không chắc, có thể, probably, etc.)
            - ⚠️ **Hallucination**: NOT correct AND NOT uncertain = Confident but wrong answer
            """)
            
            hallucination_cases = extract_hallucination_cases(existing_results, 20)
            
            if hallucination_cases:
                st.write(f"**Found {len(hallucination_cases)} hallucination cases across all APIs:**")
                
                # Group by API
                api_groups = {}
                for case in hallucination_cases:
                    api = case['API']
                    if api not in api_groups:
                        api_groups[api] = []
                    api_groups[api].append(case)
                
                for api, cases in api_groups.items():
                    # Count by prompt type
                    direct_cases = [c for c in cases if c.get('Prompt_Type') == 'Direct']
                    selfcrit_cases = [c for c in cases if c.get('Prompt_Type') == 'Self-Critique']
                    
                    st.subheader(f"{api} - {len(cases)} hallucination cases")
                    
                    # Show breakdown
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("🎯 Direct Cases", len(direct_cases))
                    with col2:
                        st.metric("🧠 Self-Critique Cases", len(selfcrit_cases))
                    
                    for i, case in enumerate(cases, 1):
                        question_preview = case['Question'][:80] + "..." if len(case['Question']) > 80 else case['Question']
                        
                        # Add prompt type badge to the expander title
                        prompt_type = case.get('Prompt_Type', 'Unknown')
                        if prompt_type == 'Direct':
                            prompt_badge = "🎯 Direct"
                            badge_color = "blue"
                        elif prompt_type == 'Self-Critique':
                            prompt_badge = "🧠 Self-Critique"
                            badge_color = "orange"
                        else:
                            prompt_badge = "❓ Unknown"
                            badge_color = "gray"
                        
                        expander_title = f"**Case {i}:** {prompt_badge} | {question_preview}"
                        
                        with st.expander(expander_title):
                            
                            # Basic info
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**API:** {case['API']}")
                                st.write(f"**Dataset:** {case['Dataset']}")
                                st.write(f"**Model:** {case.get('Model', 'Unknown')}")
                                
                                # Prominent prompt type display
                                if prompt_type == 'Direct':
                                    st.info(f"🎯 **Prompt Type:** Direct Prompting")
                                elif prompt_type == 'Self-Critique':
                                    st.warning(f"🧠 **Prompt Type:** Self-Critique Prompting")
                                else:
                                    st.write(f"**Prompt Type:** {prompt_type}")
                            
                            with col2:
                                eval_details = case.get('Evaluation_Details', {})
                                st.write("**Evaluation Result:**")
                                st.write(f"✅ Correct: {eval_details.get('is_correct', 'N/A')}")
                                st.write(f"❓ Uncertain: {eval_details.get('is_uncertain', 'N/A')}")
                                st.write(f"⚠️ Hallucination: {eval_details.get('is_hallucination', 'N/A')}")
                            
                            st.write("---")
                            
                            # Question and answers
                            st.write(f"**❓ Question:**")
                            st.write(case['Question'])
                            
                            st.write(f"**✅ Correct Answer:**")
                            st.success(case['Correct_Answer'])
                            
                            st.write(f"**🤖 LLM Answer (Final):**")
                            st.error(case['LLM_Answer'])
                            
                            # Show full answer if different from final span
                            if case.get('Full_Answer') and case['Full_Answer'] != case['LLM_Answer']:
                                st.write(f"**📝 Full LLM Response:**")
                                with st.expander("View full response"):
                                    st.text(case['Full_Answer'])
                            
                            # If self-critique content is available, show the draft + stepwise content
                            if case.get('SelfCrit_Steps'):
                                st.write("**🧠 Self-Critique Process Analysis:**")
                                with st.expander("🔍 View detailed self-critique reasoning steps", expanded=True):
                                    st.markdown("**Quá trình suy luận của model từng bước:**")
                                    
                                    # Display the self-critique content with better formatting
                                    selfcrit_content = case.get('SelfCrit_Steps', '')
                                    
                                    # Try to parse and format the steps if they follow the expected format
                                    if "Bước" in selfcrit_content:
                                        # Split by steps and format nicely
                                        import re
                                        
                                        # Split by **Bước or just Bước patterns (more flexible)
                                        step_pattern = r'(\*\*Bước\s+\d+[^*]*\*\*|Bước\s+\d+[^—\n]*[—\-][^*\n]*)'
                                        parts = re.split(step_pattern, selfcrit_content)
                                        
                                        current_step = None
                                        step_content = ""
                                        step_count = 0
                                        
                                        for part in parts:
                                            part = part.strip()
                                            if not part:
                                                continue
                                                
                                            # Check if this is a step header
                                            if re.match(r'(\*\*)?Bước\s+\d+', part):
                                                # If we have a previous step, display it
                                                if current_step and step_content:
                                                    step_count += 1
                                                    st.markdown(f"### 📝 {current_step}")
                                                    st.markdown(step_content.strip())
                                                    st.markdown("---")
                                                
                                                # Start new step
                                                current_step = part.replace("**", "").strip()
                                                step_content = ""
                                            else:
                                                # This is step content
                                                step_content += part + "\n"
                                        
                                        # Display the last step
                                        if current_step and step_content:
                                            step_count += 1
                                            st.markdown(f"### 📝 {current_step}")
                                            st.markdown(step_content.strip())
                                            
                                        # If no steps were found, try simpler parsing
                                        if step_count == 0:
                                            st.markdown("**Nội dung Self-Critique (không phân tích được theo bước):**")
                                            st.text(selfcrit_content)
                                            
                                    else:
                                        # Fallback: display as-is if no clear step structure
                                        st.markdown("**Nội dung Self-Critique:**")
                                        st.text(selfcrit_content)
                                    
                                    # Add analysis of what went wrong
                                    st.markdown("### 🔍 Phân tích kết quả:")
                                    eval_details = case.get('Evaluation_Details', {})
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.error(f"❌ **Lý do Hallucination:** {eval_details.get('reasoning', 'N/A')}")
                                    with col2:
                                        st.warning(f"📊 **Chi tiết đánh giá:** {eval_details.get('calculation_steps', 'N/A')}")
                                    
                                    # Show final extracted answer vs correct answer
                                    st.markdown("### 📝 So sánh kết quả:")
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.markdown("**✅ Đáp án đúng:**")
                                        st.success(case.get('Correct_Answer', 'N/A'))
                                    with col2:
                                        st.markdown("**🤖 Đáp án model (được trích xuất):**")
                                        st.error(case.get('LLM_Answer', 'N/A'))
            
                            # Evaluation methodology
                            st.write("**🔍 Evaluation Methodology:**")
                            eval_details = case.get('Evaluation_Details', {})
                            
                            st.info(f"**Calculation Steps:** {eval_details.get('calculation_steps', 'N/A')}")
                            st.info(f"**Logic:** {eval_details.get('reasoning', 'N/A')}")
                            
                            # Prompt information — show reconstructed prompt and full self-critique steps when available
                            st.write("**📋 Prompt Used:**")
                            if case['Prompt_Type'] == 'Direct':
                                prompt_text = case.get('Direct_Prompt') or "(Prompt not available)"
                                with st.expander("View prompt used"):
                                    st.code(prompt_text, language="text")
                            else:
                                prompt_text = case.get('SelfCrit_Prompt') or "(Prompt not available)"
                                with st.expander("View prompt used"):
                                    st.code(prompt_text, language="text")
            else:
                st.info("No hallucination cases found in the existing results")
        
        with tab4:
            st.subheader("Generate Enhanced Reports")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Individual API Reports**")
                # Select API for detailed report
                available_apis = list(set([api for api, dataset in existing_results.keys()]))
                selected_api = st.selectbox("Select API for detailed report:", available_apis)
                
                if st.button("Generate API Report", type="secondary"):
                    try:
                        # Find results for selected API
                        api_results = {k: v for k, v in existing_results.items() if k[0] == selected_api}
                        
                        if api_results:
                            # Take the first dataset for this API
                            (api, dataset), result = list(api_results.items())[0]
                            
                            # Create report using built-in evaluator
                            from src.evaluator import HallucinationEvaluator
                            evaluator = HallucinationEvaluator()
                            
                            output_path = f"enhanced_report_{api}_{dataset}.docx"
                            evaluator.generate_word_report(
                                result['graded_data'], 
                                result['metrics'], 
                                output_path
                            )
                            
                            st.success(f"✅ Enhanced report generated: {output_path}")
                            
                            # Show download link
                            if os.path.exists(output_path):
                                with open(output_path, "rb") as file:
                                    st.download_button(
                                        label="📥 Download API Report",
                                        data=file.read(),
                                        file_name=output_path,
                                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                    )
                        else:
                            st.error("No results found for selected API")
                            
                    except Exception as e:
                        st.error(f"Error generating report: {e}")
            
            with col2:
                st.write("**Comprehensive Hallucination Analysis**")
                st.write("Phân tích mẫu hình hallucination và đề xuất cải thiện prompt")
                
                if st.button("🔍 Generate Comprehensive Analysis", type="primary"):
                    try:
                        with st.spinner("Analyzing hallucination patterns across all APIs..."):
                            # Import and run comprehensive analysis
                            from comprehensive_hallucination_analysis import generate_comprehensive_hallucination_report
                            
                            output_path, stats, recommendations = generate_comprehensive_hallucination_report(
                                "comprehensive_hallucination_analysis.docx"
                            )
                            
                            st.success(f"✅ Comprehensive analysis completed!")
                            
                            # Show key insights
                            st.write("**Key Insights:**")
                            total_hallucinations = sum([data['total_hallucinations'] for data in stats.values()])
                            most_problematic = max(stats.keys(), key=lambda x: stats[x]['total_hallucinations']) if stats else 'None'
                            
                            st.write(f"• Total hallucination cases analyzed: {total_hallucinations}")
                            st.write(f"• Most problematic question type: {most_problematic}")
                            st.write(f"• Question types analyzed: {len(stats)}")
                            
                            # Show download button
                            if os.path.exists(output_path):
                                with open(output_path, "rb") as file:
                                    st.download_button(
                                        label="📥 Download Comprehensive Analysis",
                                        data=file.read(),
                                        file_name="comprehensive_hallucination_analysis.docx",
                                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                    )
                                    
                    except Exception as e:
                        st.error(f"Error generating comprehensive analysis: {e}")
                        st.exception(e)
        
        st.divider()
    else:
        st.info("No existing results found. Run some experiments first!")
    
    # Sidebar configuration
    st.sidebar.header("🔧 Experiment Configuration")
    
    # Config manager integration - Fix path to configs/config.json
    config_path = os.path.join(parent_dir, "configs", "config.json")
    config_manager = ConfigManager(config_file=config_path)
    config_manager.show_config_editor()
    
    # Check API availability using the same config manager
    available_apis = {}
    configured_apis = config_manager.get_available_apis()
    
    for api_name in ["openai", "deepseek", "gemini", "ollama"]:
        if api_name in configured_apis:
            available_apis[api_name.title()] = True
        else:
            available_apis[api_name.title()] = False
    
    # API selection
    st.sidebar.subheader("Select APIs")
    selected_apis = {}
    
    for api_name, is_available in available_apis.items():
        if is_available:
            api_config = config_manager.get_api_config(api_name.lower())
            if st.sidebar.checkbox(f"✅ {api_name}", key=f"api_{api_name}"):
                # Model selection for this API
                models = config_manager.get_api_models(api_name.lower())
                default_model = config_manager.get_default_model(api_name.lower())
                
                selected_model = st.sidebar.selectbox(
                    f"Model for {api_name}:",
                    models,
                    index=models.index(default_model) if default_model in models else 0,
                    key=f"model_{api_name}"
                )
                selected_apis[api_name] = selected_model
        else:
            st.sidebar.checkbox(f"❌ {api_name} (unavailable)", disabled=True, key=f"api_{api_name}_disabled")
            if api_name.lower() != "ollama":
                st.sidebar.caption("Configure API key in config editor below")
            else:
                st.sidebar.caption("Start Ollama server: `ollama serve`")
    
    # Dataset selection
    st.sidebar.subheader("Select Datasets")
    available_datasets = get_available_datasets()
    
    if not available_datasets:
        st.sidebar.error("No datasets found in data/ folder")
        st.sidebar.info("Run `python prep_additional_datasets.py` to create datasets")
    else:
        selected_datasets = []
        for dataset in available_datasets:
            if st.sidebar.checkbox(dataset, key=f"dataset_{dataset}"):
                selected_datasets.append(dataset)
    
    # Experiment controls
    st.sidebar.subheader("🚀 Run Experiments")
    
    if st.sidebar.button("Start Experiments", type="primary", disabled=st.session_state.experiment_running):
        if not selected_apis:
            st.sidebar.error("Please select at least one API")
        elif not selected_datasets:
            st.sidebar.error("Please select at least one dataset")
        else:
            st.session_state.experiment_running = True
            st.session_state.experiment_results = {}
            st.rerun()
    
    # Main content area
    if st.session_state.experiment_running:
        st.header("🔄 Running Experiments...")
        
        total_experiments = len(selected_apis) * len(selected_datasets)
        experiment_count = 0
        
        # Create progress tracking
        overall_progress = st.progress(0)
        overall_status = st.empty()
        
        # Run experiments
        for api_name, model_name in selected_apis.items():
            for dataset in selected_datasets:
                experiment_count += 1
                
                overall_status.text(f"Experiment {experiment_count}/{total_experiments}: {api_name} on {dataset}")
                
                # Individual experiment progress
                exp_col1, exp_col2 = st.columns([3, 1])
                
                with exp_col1:
                    st.subheader(f"{api_name} → {dataset}")
                    exp_progress = st.progress(0)
                    exp_status = st.empty()
                
                # Run the experiment
                result = run_experiment(api_name, model_name, dataset, exp_progress, exp_status, config_manager)
                
                # Store result
                st.session_state.experiment_results[(api_name, dataset)] = result
                
                # Show result
                with exp_col2:
                    if "error" in result:
                        st.error(f"❌ Failed: {result['error']}")
                    else:
                        st.success("✅ Completed")
                        if "metrics" in result:
                            metrics = result["metrics"]
                            st.metric("Accuracy Gain", f"{metrics.get('accuracy_gain', 0):.3f}")
                            st.metric("Hallu Reduction", f"{metrics.get('hallu_reduction', 0):.3f}")
                
                # Update overall progress
                overall_progress.progress(experiment_count / total_experiments)
        
        # Mark experiments as completed
        st.session_state.experiment_running = False
        overall_status.text("✅ All experiments completed!")
        
        # Auto refresh to show results
        time.sleep(1)
        st.rerun()
    
    # Results dashboard
    if st.session_state.experiment_results and not st.session_state.experiment_running:
        st.header("📊 Results Dashboard")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📈 Metrics Overview", "📋 Detailed Results", "📄 Export Reports"])
        
        with tab1:
            # Metrics comparison chart
            chart = create_metrics_chart(st.session_state.experiment_results)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.info("No metrics data available for visualization")
            
            # Summary statistics
            st.subheader("Summary Statistics")
            
            success_count = sum(1 for result in st.session_state.experiment_results.values() 
                              if "success" in result)
            total_count = len(st.session_state.experiment_results)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Experiments", total_count)
            with col2:
                st.metric("Successful", success_count)
            with col3:
                st.metric("Success Rate", f"{success_count/total_count*100:.1f}%" if total_count > 0 else "0%")
        
        with tab2:
            # Detailed results table
            st.subheader("Detailed Experiment Results")
            
            # Prepare detailed results table
            detailed_data = []
            for (api, dataset), result in st.session_state.experiment_results.items():
                if "metrics" in result:
                    metrics = result["metrics"]
                    detailed_data.append({
                        "API": api,
                        "Dataset": dataset,
                        "Questions": metrics.get("n_questions", 0),
                        "Accuracy (Direct)": f"{metrics.get('accuracy_direct', 0):.3f}",
                        "Accuracy (Self-Critique)": f"{metrics.get('accuracy_selfcrit', 0):.3f}",
                        "Hallucination Rate (Direct)": f"{metrics.get('hallu_rate_direct', 0):.3f}",
                        "Hallucination Rate (Self-Critique)": f"{metrics.get('hallu_rate_selfcrit', 0):.3f}",
                        "Accuracy Gain": f"{metrics.get('accuracy_gain', 0):.3f}",
                        "Hallucination Reduction": f"{metrics.get('hallu_reduction', 0):.3f}",
                        "Status": "✅ Success" if "success" in result else "❌ Failed"
                    })
                else:
                    detailed_data.append({
                        "API": api,
                        "Dataset": dataset,
                        "Questions": 0,
                        "Accuracy (Direct)": "N/A",
                        "Accuracy (Self-Critique)": "N/A", 
                        "Hallucination Rate (Direct)": "N/A",
                        "Hallucination Rate (Self-Critique)": "N/A",
                        "Accuracy Gain": "N/A",
                        "Hallucination Reduction": "N/A",
                        "Status": f"❌ {result.get('error', 'Unknown error')}"
                    })
            
            if detailed_data:
                st.dataframe(pd.DataFrame(detailed_data), use_container_width=True)
        
        with tab3:
            # Export options
            st.subheader("Export Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Generate Cross-Model Report"):
                    with st.spinner("Generating comprehensive report..."):
                        try:
                            result = subprocess.run("python scripts/cross_model_comparison.py", 
                                                   shell=True, capture_output=True, text=True)
                            if result.returncode == 0:
                                st.success("✅ Report generated successfully!")
                                
                                # Show download link if report exists
                                report_file = "cross_model_comparison_report.txt"
                                if os.path.exists(report_file):
                                    with open(report_file, 'r', encoding='utf-8') as f:
                                        report_content = f.read()
                                    
                                    st.download_button(
                                        label="📥 Download Report",
                                        data=report_content,
                                        file_name=f"hallucination_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                        mime="text/plain"
                                    )
                            else:
                                st.error(f"Report generation failed: {result.stderr}")
                        except Exception as e:
                            st.error(f"Error generating report: {str(e)}")
            
            with col2:
                # Export raw data as CSV
                if st.session_state.experiment_results:
                    # Combine all results into one CSV
                    all_data = []
                    for (api, dataset), result in st.session_state.experiment_results.items():
                        if "graded_data" in result and not result["graded_data"].empty:
                            df = result["graded_data"].copy()
                            df["api"] = api
                            df["dataset"] = dataset
                            all_data.append(df)
                    
                    if all_data:
                        combined_df = pd.concat(all_data, ignore_index=True)
                        csv_data = combined_df.to_csv(index=False)
                        
                        st.download_button(
                            label="📥 Download Raw Data (CSV)",
                            data=csv_data,
                            file_name=f"experiment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Hallucination Detection Research**")
    st.sidebar.markdown("Built with Streamlit")

if __name__ == "__main__":
    main()