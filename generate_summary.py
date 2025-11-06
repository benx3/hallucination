"""
Generate a comprehensive summary of all experiment results
"""

import pandas as pd
import json
from pathlib import Path

def generate_summary():
    print("📊 COMPREHENSIVE EXPERIMENT RESULTS SUMMARY")
    print("=" * 50)
    
    results_dir = Path("data/results")
    apis = ["openai", "deepseek", "gemini", "ollama"]
    
    summary_data = []
    
    for api in apis:
        api_dir = results_dir / api
        metrics_file = api_dir / "metrics_scientific_facts.json"
        
        if metrics_file.exists():
            with open(metrics_file, 'r', encoding='utf-8') as f:
                metrics = json.load(f)
            
            direct = metrics.get("direct", {})
            selfcrit = metrics.get("selfcrit", {})
            improvement = metrics.get("improvement", {})
            
            summary_data.append({
                "API": api.upper(),
                "Total Questions": metrics.get("total_questions", 0),
                "Direct Correct": f"{direct.get('correct_rate', 0)*100:.1f}%",
                "Direct Hallucination": f"{direct.get('hallucination_rate', 0)*100:.1f}%",
                "SelfCrit Correct": f"{selfcrit.get('correct_rate', 0)*100:.1f}%", 
                "SelfCrit Hallucination": f"{selfcrit.get('hallucination_rate', 0)*100:.1f}%",
                "Accuracy Improvement": f"{improvement.get('correct_delta', 0)*100:+.1f}%",
                "Hallucination Reduction": f"{improvement.get('hallucination_delta', 0)*100:+.1f}%"
            })
            
            print(f"\n🤖 {api.upper()} Results:")
            print(f"   Direct Prompting: {direct.get('correct_rate', 0)*100:.1f}% correct, {direct.get('hallucination_rate', 0)*100:.1f}% hallucination")
            print(f"   Self-Critique: {selfcrit.get('correct_rate', 0)*100:.1f}% correct, {selfcrit.get('hallucination_rate', 0)*100:.1f}% hallucination")
            print(f"   Improvement: {improvement.get('correct_delta', 0)*100:+.1f}% accuracy, {improvement.get('hallucination_delta', 0)*100:+.1f}% hallucination reduction")
    
    if summary_data:
        print("\n📈 COMPARISON TABLE:")
        print("-" * 120)
        df = pd.DataFrame(summary_data)
        print(df.to_string(index=False))
        
        print("\n🏆 KEY INSIGHTS:")
        
        # Find best performing API
        best_direct = max(summary_data, key=lambda x: float(x["Direct Correct"].rstrip('%')))
        best_selfcrit = max(summary_data, key=lambda x: float(x["SelfCrit Correct"].rstrip('%')))
        
        print(f"• Best Direct Prompting: {best_direct['API']} ({best_direct['Direct Correct']} correct)")
        print(f"• Best Self-Critique: {best_selfcrit['API']} ({best_selfcrit['SelfCrit Correct']} correct)")
        
        # Find biggest improvement
        improvements = [float(x["Accuracy Improvement"].rstrip('%+')) for x in summary_data]
        if max(improvements) > 0:
            best_improvement = summary_data[improvements.index(max(improvements))]
            print(f"• Biggest Improvement: {best_improvement['API']} ({best_improvement['Accuracy Improvement']} accuracy gain)")
        
        # Find lowest hallucination
        hallu_rates = [float(x["SelfCrit Hallucination"].rstrip('%')) for x in summary_data]
        lowest_hallu = summary_data[hallu_rates.index(min(hallu_rates))]
        print(f"• Lowest Hallucination (Self-Critique): {lowest_hallu['API']} ({lowest_hallu['SelfCrit Hallucination']})")
    
    print(f"\n📄 Reports generated:")
    for api in apis:
        report_file = results_dir / api / "report_scientific_facts.docx"
        if report_file.exists():
            print(f"   • {api.upper()}: {report_file}")
    
    print(f"\n🌐 Dashboard: http://localhost:8501")
    print("   View comprehensive analysis, API comparisons, and hallucination cases")

if __name__ == "__main__":
    generate_summary()