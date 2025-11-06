# components/analytics.py - Advanced analytics components for the UI
# REQUIRE: pip install streamlit pandas plotly

import streamlit as st
import pandas as pd
import json
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

def create_metrics_comparison(metrics_data):
    """Create metrics comparison chart"""
    if not metrics_data:
        return None
    
    # Create comparison bar chart
    fig = go.Figure()
    
    categories = ['Correct Rate', 'Uncertainty Rate', 'Hallucination Rate']
    direct_values = [
        metrics_data.get('direct', {}).get('correct_rate', 0),
        metrics_data.get('direct', {}).get('uncertainty_rate', 0),
        metrics_data.get('direct', {}).get('hallucination_rate', 0)
    ]
    selfcrit_values = [
        metrics_data.get('selfcrit', {}).get('correct_rate', 0),
        metrics_data.get('selfcrit', {}).get('uncertainty_rate', 0),
        metrics_data.get('selfcrit', {}).get('hallucination_rate', 0)
    ]
    
    fig.add_trace(go.Bar(
        name='Direct Prompt',
        x=categories,
        y=direct_values,
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        name='Self-Critique',
        x=categories,
        y=selfcrit_values,
        marker_color='orange'
    ))
    
    fig.update_layout(
        title='Prompting Strategy Comparison',
        xaxis_title='Metrics',
        yaxis_title='Rate',
        barmode='group',
        height=400
    )
    
    return fig

def create_hallucination_trend(results_data):
    """Create hallucination trend analysis"""
    if not results_data:
        return None
    
    # Simple trend chart
    fig = go.Figure()
    
    categories = ['Direct', 'Self-Critique']
    values = [
        results_data.get('direct', {}).get('hallucination_rate', 0),
        results_data.get('selfcrit', {}).get('hallucination_rate', 0)
    ]
    
    fig.add_trace(go.Scatter(
        x=categories,
        y=values,
        mode='lines+markers',
        name='Hallucination Rate',
        line=dict(color='red', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title='Hallucination Rate Trend',
        xaxis_title='Prompting Strategy',
        yaxis_title='Hallucination Rate',
        height=300
    )
    
    return fig

def create_api_comparison_chart(results_data):
    """Create detailed API comparison chart"""
    if not results_data:
        return None
    
    # Prepare data
    metrics_data = []
    for (api, dataset), result in results_data.items():
        if "metrics" in result:
            metrics = result["metrics"]
            metrics_data.append({
                "API": api,
                "Dataset": dataset,
                "accuracy_direct": metrics.get("accuracy_direct", 0),
                "accuracy_selfcrit": metrics.get("accuracy_selfcrit", 0),
                "hallu_rate_direct": metrics.get("hallu_rate_direct", 0),
                "hallu_rate_selfcrit": metrics.get("hallu_rate_selfcrit", 0),
                "improvement": metrics.get("accuracy_gain", 0),
                "reduction": metrics.get("hallu_reduction", 0)
            })
    
    if not metrics_data:
        return None
    
    df = pd.DataFrame(metrics_data)
    
    # Create radar chart for each API
    apis = df["API"].unique()
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[f"{api} Performance" for api in apis[:4]],
        specs=[[{"type": "polar"}, {"type": "polar"}],
               [{"type": "polar"}, {"type": "polar"}]]
    )
    
    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
    
    for i, api in enumerate(apis[:4]):
        api_data = df[df["API"] == api]
        avg_metrics = {
            "Accuracy (Direct)": api_data["accuracy_direct"].mean(),
            "Accuracy (Self-Critique)": api_data["accuracy_selfcrit"].mean(),
            "Low Hallucination (Direct)": 1 - api_data["hallu_rate_direct"].mean(),
            "Low Hallucination (Self-Critique)": 1 - api_data["hallu_rate_selfcrit"].mean(),
            "Improvement": max(0, api_data["improvement"].mean()),
            "Reduction": max(0, api_data["reduction"].mean())
        }
        
        categories = list(avg_metrics.keys())
        values = list(avg_metrics.values())
        
        row = (i // 2) + 1
        col = (i % 2) + 1
        
        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=api,
                line_color=colors[i % len(colors)]
            ),
            row=row, col=col
        )
    
    fig.update_layout(height=600, title_text="API Performance Radar Charts")
    return fig

def create_dataset_difficulty_analysis(results_data):
    """Analyze dataset difficulty across models"""
    if not results_data:
        return None
    
    # Calculate difficulty score for each dataset
    dataset_scores = {}
    
    for (api, dataset), result in results_data.items():
        if "metrics" in result:
            metrics = result["metrics"]
            difficulty = (
                metrics.get("hallu_rate_direct", 0) + 
                metrics.get("hallu_rate_selfcrit", 0)
            ) / 2
            
            if dataset not in dataset_scores:
                dataset_scores[dataset] = []
            dataset_scores[dataset].append(difficulty)
    
    # Calculate average difficulty per dataset
    avg_difficulty = {
        dataset: sum(scores) / len(scores) 
        for dataset, scores in dataset_scores.items()
    }
    
    # Create bar chart
    fig = px.bar(
        x=list(avg_difficulty.keys()),
        y=list(avg_difficulty.values()),
        title="Dataset Difficulty Analysis (Higher = More Difficult)",
        labels={"x": "Dataset", "y": "Average Hallucination Rate"}
    )
    
    fig.update_layout(showlegend=False)
    return fig

def show_question_level_analysis(results_data):
    """Show detailed question-level analysis"""
    if not results_data:
        st.info("No data available for question-level analysis")
        return
    
    st.subheader("🔍 Question-Level Analysis")
    
    # Combine all question data
    all_questions = []
    for (api, dataset), result in results_data.items():
        if "graded_data" in result and not result["graded_data"].empty:
            df = result["graded_data"].copy()
            df["api"] = api
            df["dataset"] = dataset
            all_questions.append(df)
    
    if not all_questions:
        st.info("No graded data available")
        return
    
    combined_df = pd.concat(all_questions, ignore_index=True)
    
    # Most difficult questions (high hallucination rate across models)
    question_stats = combined_df.groupby("question").agg({
        "direct_hallucination": "mean",
        "selfcrit_hallucination": "mean",
        "api": "count"
    }).rename(columns={"api": "tested_models"})
    
    question_stats["avg_hallucination"] = (
        question_stats["direct_hallucination"] + 
        question_stats["selfcrit_hallucination"]
    ) / 2
    
    # Filter questions tested on multiple models
    multi_model_questions = question_stats[question_stats["tested_models"] >= 2]
    
    if not multi_model_questions.empty:
        # Most difficult questions
        difficult_questions = multi_model_questions.nlargest(10, "avg_hallucination")
        
        st.write("**Top 10 Most Difficult Questions:**")
        for idx, (question, stats) in enumerate(difficult_questions.iterrows(), 1):
            with st.expander(f"{idx}. Difficulty Score: {stats['avg_hallucination']:.3f}"):
                st.write(f"**Question:** {question}")
                st.write(f"**Tested on {int(stats['tested_models'])} models**")
                st.write(f"- Direct hallucination rate: {stats['direct_hallucination']:.3f}")
                st.write(f"- Self-critique hallucination rate: {stats['selfcrit_hallucination']:.3f}")
                
                # Show per-model results for this question
                question_results = combined_df[combined_df["question"] == question]
                if not question_results.empty:
                    st.write("**Per-model results:**")
                    for _, row in question_results.iterrows():
                        direct_status = "✅" if row["direct_correct"] else ("❓" if row["direct_uncertain"] else "❌")
                        selfcrit_status = "✅" if row["selfcrit_correct"] else ("❓" if row["selfcrit_uncertain"] else "❌")
                        st.write(f"- {row['api']}: Direct {direct_status} | Self-Critique {selfcrit_status}")

def show_improvement_analysis(results_data):
    """Analyze self-critique improvement patterns"""
    st.subheader("📈 Self-Critique Improvement Analysis")
    
    if not results_data:
        st.info("No data available for improvement analysis")
        return
    
    # Calculate improvement metrics
    improvements = []
    for (api, dataset), result in results_data.items():
        if "metrics" in result:
            metrics = result["metrics"]
            improvements.append({
                "API": api,
                "Dataset": dataset,
                "Accuracy Improvement": metrics.get("accuracy_gain", 0),
                "Hallucination Reduction": metrics.get("hallu_reduction", 0),
                "Questions": metrics.get("n_questions", 0)
            })
    
    if not improvements:
        st.info("No improvement data available")
        return
    
    df = pd.DataFrame(improvements)
    
    # Show summary statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Average Accuracy Improvement",
            f"{df['Accuracy Improvement'].mean():.3f}",
            delta=f"{df['Accuracy Improvement'].std():.3f} std"
        )
    
    with col2:
        st.metric(
            "Average Hallucination Reduction", 
            f"{df['Hallucination Reduction'].mean():.3f}",
            delta=f"{df['Hallucination Reduction'].std():.3f} std"
        )
    
    # Scatter plot: Accuracy Improvement vs Hallucination Reduction
    fig = px.scatter(
        df, 
        x="Accuracy Improvement", 
        y="Hallucination Reduction",
        color="API",
        size="Questions",
        hover_data=["Dataset"],
        title="Self-Critique Effectiveness: Accuracy vs Hallucination Improvement"
    )
    
    # Add quadrant lines
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add quadrant labels
    fig.add_annotation(x=0.02, y=0.02, text="Win-Win", showarrow=False, font=dict(color="green"))
    fig.add_annotation(x=-0.02, y=0.02, text="Reduced Hallu", showarrow=False, font=dict(color="blue"))
    fig.add_annotation(x=0.02, y=-0.02, text="Better Accuracy", showarrow=False, font=dict(color="orange"))
    fig.add_annotation(x=-0.02, y=-0.02, text="Worse", showarrow=False, font=dict(color="red"))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Best and worst performers
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Best Performers (Self-Critique):**")
        best = df.nlargest(3, "Accuracy Improvement")
        for _, row in best.iterrows():
            st.write(f"• {row['API']} on {row['Dataset']}: +{row['Accuracy Improvement']:.3f} accuracy")
    
    with col2:
        st.write("**Most Hallucination Reduction:**")
        best_hallu = df.nlargest(3, "Hallucination Reduction")
        for _, row in best_hallu.iterrows():
            st.write(f"• {row['API']} on {row['Dataset']}: -{row['Hallucination Reduction']:.3f} hallucination")

def export_detailed_report(results_data):
    """Generate detailed text report for export"""
    if not results_data:
        return "No experiment data available."
    
    report_lines = [
        "HALLUCINATION DETECTION RESEARCH - DETAILED REPORT",
        "=" * 60,
        "",
        f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total experiments: {len(results_data)}",
        ""
    ]
    
    # Summary statistics
    success_count = sum(1 for result in results_data.values() if "metrics" in result)
    report_lines.extend([
        "SUMMARY STATISTICS:",
        "-" * 20,
        f"Successful experiments: {success_count}/{len(results_data)}",
        ""
    ])
    
    # Per-experiment results
    report_lines.extend([
        "DETAILED RESULTS:",
        "-" * 20
    ])
    
    for (api, dataset), result in results_data.items():
        report_lines.append(f"\n{api} on {dataset}:")
        
        if "metrics" in result:
            metrics = result["metrics"]
            report_lines.extend([
                f"  Questions: {metrics.get('n_questions', 0)}",
                f"  Accuracy (Direct): {metrics.get('accuracy_direct', 0):.3f}",
                f"  Accuracy (Self-Critique): {metrics.get('accuracy_selfcrit', 0):.3f}",
                f"  Hallucination Rate (Direct): {metrics.get('hallu_rate_direct', 0):.3f}",
                f"  Hallucination Rate (Self-Critique): {metrics.get('hallu_rate_selfcrit', 0):.3f}",
                f"  Accuracy Gain: {metrics.get('accuracy_gain', 0):.3f}",
                f"  Hallucination Reduction: {metrics.get('hallu_reduction', 0):.3f}",
                "  Status: ✅ SUCCESS"
            ])
        else:
            error_msg = result.get("error", "Unknown error")
            report_lines.extend([
                f"  Status: ❌ FAILED",
                f"  Error: {error_msg}"
            ])
    
    return "\n".join(report_lines)