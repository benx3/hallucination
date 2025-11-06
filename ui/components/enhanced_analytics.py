"""
Enhanced analytics components for comprehensive dashboard display
Includes API comparison, hallucination analysis, and result loading
"""

import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict, List, Tuple
import glob

# Import default prompt templates so we can reconstruct prompts for display
try:
    from src.api_runner import DEFAULT_DIRECT_PROMPT, DEFAULT_SELFCRIT_PROMPT
except Exception:
    # Fallback templates if import fails for any reason
    DEFAULT_DIRECT_PROMPT = (
        "Bạn là trợ lý chính xác về sự kiện. Trả lời ngắn gọn một đoạn. "
        "Nếu không chắc chắn, hãy nói 'không chắc'.\n"
        "Câu hỏi: {q}"
    )

    DEFAULT_SELFCRIT_PROMPT = (
        "Nhiệm vụ: Trả lời rồi tự kiểm tra tính chính xác và sửa lại nếu cần.\n"
        "Bước 1 — Nháp: trả lời ngắn.\n"
        "Bước 2 — Tự kiểm: liệt kê điểm có thể sai hoặc thiếu.\n"
        "Bước 3 — Cuối cùng: đưa đáp án cuối cùng. Nếu không chắc, hãy nói rõ không chắc.\n"
        "Câu hỏi: {q}"
    )

def load_all_existing_results(results_dir=None):
    """Load all existing results from all API providers"""
    import os
    from pathlib import Path
    
    results_data = {}
    
    # Use absolute path like in UI app.py
    if results_dir is None:
        # Get the project root directory (parent of ui directory)
        current_file = os.path.abspath(__file__)
        ui_components_dir = os.path.dirname(current_file)  # components/
        ui_dir = os.path.dirname(ui_components_dir)        # ui/
        project_root = os.path.dirname(ui_dir)             # project root
        results_dir = os.path.join(project_root, "data", "results")
    
    results_path = Path(results_dir)
    if not results_path.exists():
        if 'st' in globals():
            st.info(f"""
            📊 **Welcome to Enhanced Hallucination Detection Dashboard!**
            
            This dashboard analyzes LLM hallucination patterns across 4 models.
            
            **To get started:**
            1. Run experiments using the main application 
            2. Results will appear in: `{results_dir}`
            3. Return here to view comprehensive analytics
            
            **Currently showing demo mode** - the directory structure is ready for your experiments!
            """)
        else:
            print(f"Results directory not found: {results_dir}")
        return results_data
    
    # Define API directories
    api_dirs = ["openai", "deepseek", "gemini", "ollama"]
    
    for api in api_dirs:
        api_path = results_path / api
        if api_path.exists():
            # Find all results files
            graded_files = list(api_path.glob("*graded*.csv"))
            metrics_files = list(api_path.glob("metrics*.json"))
            
            for graded_file in graded_files:
                # Extract dataset name from filename
                filename = graded_file.name
                if "questions_50_hard" in filename:
                    dataset = "questions_50_hard"
                elif "scientific_facts_basic" in filename:
                    dataset = "scientific_facts_basic"
                elif "astronomy_hard" in filename:
                    dataset = "astronomy_hard"
                elif "mathematics_hard" in filename:
                    dataset = "mathematics_hard"
                elif "test_results" in filename:
                    dataset = "test"
                else:
                    # General fallback for any other datasets
                    dataset = filename.replace("results_graded_", "").replace(".csv", "")
                
                # Load graded results
                try:
                    graded_df = pd.read_csv(graded_file)
                    
                    # Find corresponding metrics file
                    metrics_file = None
                    for mf in metrics_files:
                        if dataset in mf.name:
                            metrics_file = mf
                            break
                    
                    metrics = {}
                    if metrics_file and metrics_file.exists():
                        with open(metrics_file, 'r', encoding='utf-8') as f:
                            metrics = json.load(f)
                    
                    results_data[(api, dataset)] = {
                        "graded_data": graded_df,
                        "metrics": metrics,
                        "dataset": dataset,
                        "api": api,
                        "file_path": str(graded_file)
                    }
                    
                except Exception as e:
                    st.warning(f"Error loading {graded_file}: {e}")
    
    return results_data

def create_api_comparison_chart(results_data):
    """Create comprehensive API comparison chart"""
    if not results_data:
        return None
    
    # Prepare comparison data
    comparison_data = []
    
    for (api, dataset), result in results_data.items():
        if "metrics" in result and result["metrics"]:
            metrics = result["metrics"]
            
            # Handle different metrics formats
            direct_metrics = metrics.get("direct", {})
            selfcrit_metrics = metrics.get("selfcrit", {})
            
            comparison_data.append({
                "API": api.upper(),
                "Dataset": dataset,
                "Direct_Correct": direct_metrics.get("correct_rate", 0) * 100,
                "Direct_Uncertain": direct_metrics.get("uncertainty_rate", 0) * 100,
                "Direct_Hallucination": direct_metrics.get("hallucination_rate", 0) * 100,
                "SelfCrit_Correct": selfcrit_metrics.get("correct_rate", 0) * 100,
                "SelfCrit_Uncertain": selfcrit_metrics.get("uncertainty_rate", 0) * 100,
                "SelfCrit_Hallucination": selfcrit_metrics.get("hallucination_rate", 0) * 100,
                "Total_Questions": metrics.get("total_questions", 0)
            })
    
    if not comparison_data:
        return None
    
    df = pd.DataFrame(comparison_data)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Correct Rate", "Uncertainty Rate", "Hallucination Rate", "Improvement Analysis"),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Correct Rate Comparison
    fig.add_trace(
        go.Bar(name="Direct", x=df["API"], y=df["Direct_Correct"], 
               marker_color="lightblue", showlegend=True),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name="Self-Critique", x=df["API"], y=df["SelfCrit_Correct"], 
               marker_color="orange", showlegend=False),
        row=1, col=1
    )
    
    # Uncertainty Rate
    fig.add_trace(
        go.Bar(name="Direct", x=df["API"], y=df["Direct_Uncertain"], 
               marker_color="lightblue", showlegend=False),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(name="Self-Critique", x=df["API"], y=df["SelfCrit_Uncertain"], 
               marker_color="orange", showlegend=False),
        row=1, col=2
    )
    
    # Hallucination Rate
    fig.add_trace(
        go.Bar(name="Direct", x=df["API"], y=df["Direct_Hallucination"], 
               marker_color="red", showlegend=False),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(name="Self-Critique", x=df["API"], y=df["SelfCrit_Hallucination"], 
               marker_color="darkred", showlegend=False),
        row=2, col=1
    )
    
    # Improvement (Correct Rate Self-Critique - Direct)
    improvement = df["SelfCrit_Correct"] - df["Direct_Correct"]
    fig.add_trace(
        go.Bar(name="Improvement", x=df["API"], y=improvement, 
               marker_color="green", showlegend=False),
        row=2, col=2
    )
    
    fig.update_layout(
        title="API Performance Comparison Across Models",
        height=800,
        showlegend=True
    )
    
    # Update y-axis labels
    fig.update_yaxes(title_text="Correct Rate (%)", row=1, col=1)
    fig.update_yaxes(title_text="Uncertainty Rate (%)", row=1, col=2)
    fig.update_yaxes(title_text="Hallucination Rate (%)", row=2, col=1)
    fig.update_yaxes(title_text="Improvement (%)", row=2, col=2)
    
    return fig

def extract_hallucination_cases(results_data, max_per_api=10):
    """Extract hallucination cases from results with detailed evaluation info"""
    hallucination_cases = []
    
    for (api, dataset), result in results_data.items():
        if "graded_data" in result:
            df = result["graded_data"]
            
            # Find hallucination cases
            direct_hallu = df[df['direct_hallucination'] == True]
            selfcrit_hallu = df[df['selfcrit_hallucination'] == True]
            
            # Sample random cases
            if len(direct_hallu) > 0:
                sample_direct = direct_hallu.sample(min(max_per_api//2, len(direct_hallu)))
                for _, row in sample_direct.iterrows():
                    # Try to get prompt from CSV first, fallback to reconstruction
                    direct_prompt = row.get('direct_prompt', '') or DEFAULT_DIRECT_PROMPT.format(q=row['question']) if row.get('question') is not None else ""
                    
                    hallucination_cases.append({
                        "API": api.upper(),
                        "Dataset": dataset,
                        "Question": row['question'],
                        "Correct_Answer": row['gold_answer'],
                        "LLM_Answer": row.get('direct_answer', ''),
                        "Full_Answer": row.get('direct_answer', ''),
                        "Prompt_Type": "Direct",
                        "Hallucination_Type": "Confident but Wrong",
                        "Model": row.get('model', 'Unknown'),
                        # Use prompt from CSV if available, otherwise reconstruct
                        "Direct_Prompt": direct_prompt,
                        "Evaluation_Details": {
                            "is_correct": row['direct_correct'],
                            "is_uncertain": row['direct_uncertain'], 
                            "is_hallucination": row['direct_hallucination'],
                            "calculation_steps": f"Correct={row['direct_correct']}, Uncertain={row['direct_uncertain']} → Hallucination={row['direct_hallucination']} (Confident but Wrong)",
                            "reasoning": "Hallucination = NOT correct AND NOT uncertain (confident wrong answer)"
                        }
                    })
            
            if len(selfcrit_hallu) > 0:
                sample_selfcrit = selfcrit_hallu.sample(min(max_per_api//2, len(selfcrit_hallu)))
                for _, row in sample_selfcrit.iterrows():
                    # Try to get prompt from CSV first, fallback to reconstruction
                    selfcrit_prompt = row.get('selfcrit_prompt', '') or DEFAULT_SELFCRIT_PROMPT.format(q=row['question']) if row.get('question') is not None else ""
                    
                    hallucination_cases.append({
                        "API": api.upper(),
                        "Dataset": dataset,
                        "Question": row['question'],
                        "Correct_Answer": row['gold_answer'],
                        "LLM_Answer": row.get('selfcrit_final_span', ''),
                        "Full_Answer": row.get('selfcrit_answer', ''),
                        "Prompt_Type": "Self-Critique",
                        "Hallucination_Type": "Confident but Wrong",
                        "Model": row.get('model', 'Unknown'),
                        # Use prompt from CSV if available, otherwise reconstruct
                        "SelfCrit_Prompt": selfcrit_prompt,
                        "SelfCrit_Steps": row.get('selfcrit_answer', ''),
                        "Evaluation_Details": {
                            "is_correct": row['selfcrit_correct'],
                            "is_uncertain": row['selfcrit_uncertain'],
                            "is_hallucination": row['selfcrit_hallucination'],
                            "calculation_steps": f"Correct={row['selfcrit_correct']}, Uncertain={row['selfcrit_uncertain']} → Hallucination={row['selfcrit_hallucination']} (Confident but Wrong)",
                            "reasoning": "Hallucination = NOT correct AND NOT uncertain (confident wrong answer)"
                        }
                    })
    
    return hallucination_cases

def create_hallucination_analysis_chart(results_data):
    """Create detailed hallucination analysis"""
    if not results_data:
        return None
    
    # Count hallucinations by API and type
    hallu_data = []
    
    for (api, dataset), result in results_data.items():
        if "graded_data" in result:
            df = result["graded_data"]
            
            total_questions = len(df)
            direct_hallu_count = len(df[df['direct_hallucination'] == True])
            selfcrit_hallu_count = len(df[df['selfcrit_hallucination'] == True])
            
            hallu_data.append({
                "API": api.upper(),
                "Dataset": dataset,
                "Direct_Hallucinations": direct_hallu_count,
                "SelfCrit_Hallucinations": selfcrit_hallu_count,
                "Total_Questions": total_questions,
                "Direct_Rate": (direct_hallu_count / total_questions) * 100 if total_questions > 0 else 0,
                "SelfCrit_Rate": (selfcrit_hallu_count / total_questions) * 100 if total_questions > 0 else 0
            })
    
    if not hallu_data:
        return None
    
    df = pd.DataFrame(hallu_data)
    
    # Create heatmap for hallucination rates
    fig = go.Figure()
    
    # Add traces for direct and self-critique
    fig.add_trace(go.Bar(
        name="Direct Prompting",
        x=df["API"], 
        y=df["Direct_Rate"],
        marker_color="lightcoral"
    ))
    
    fig.add_trace(go.Bar(
        name="Self-Critique",
        x=df["API"], 
        y=df["SelfCrit_Rate"],
        marker_color="darkred"
    ))
    
    fig.update_layout(
        title="Hallucination Rates by API and Prompting Strategy",
        xaxis_title="API Provider",
        yaxis_title="Hallucination Rate (%)",
        barmode="group",
        height=400
    )
    
    return fig

def create_detailed_metrics_table(results_data):
    """Create detailed metrics table for display"""
    table_data = []
    
    for (api, dataset), result in results_data.items():
        if "metrics" in result and result["metrics"]:
            metrics = result["metrics"]
            direct = metrics.get("direct", {})
            selfcrit = metrics.get("selfcrit", {})
            improvement = metrics.get("improvement", {})
            
            table_data.append({
                "API": api.upper(),
                "Dataset": dataset,
                "Total Questions": metrics.get("total_questions", 0),
                "Direct Correct %": f"{direct.get('correct_rate', 0)*100:.1f}%",
                "Direct Uncertain %": f"{direct.get('uncertainty_rate', 0)*100:.1f}%", 
                "Direct Hallucination %": f"{direct.get('hallucination_rate', 0)*100:.1f}%",
                "SelfCrit Correct %": f"{selfcrit.get('correct_rate', 0)*100:.1f}%",
                "SelfCrit Uncertain %": f"{selfcrit.get('uncertainty_rate', 0)*100:.1f}%",
                "SelfCrit Hallucination %": f"{selfcrit.get('hallucination_rate', 0)*100:.1f}%",
                "Improvement (Correct)": f"{improvement.get('correct_delta', 0)*100:+.1f}%",
                "Improvement (Hallucination)": f"{-improvement.get('hallucination_delta', 0)*100:+.1f}%"
            })
    
    return pd.DataFrame(table_data) if table_data else None