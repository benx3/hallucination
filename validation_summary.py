#!/usr/bin/env python3
"""
Validation script to demonstrate comprehensive analysis features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def show_analysis_summary():
    """Show summary of the comprehensive analysis"""
    
    print("🔍 COMPREHENSIVE HALLUCINATION ANALYSIS SUMMARY")
    print("=" * 60)
    
    # Load results
    from ui.components.enhanced_analytics import load_all_existing_results
    results_data = load_all_existing_results()
    
    if not results_data:
        print("❌ No results found")
        return
    
    print(f"📊 Found {len(results_data)} result sets:")
    for (api, dataset), result in results_data.items():
        metrics = result.get('metrics', {})
        if metrics:
            direct_hallu = metrics.get('direct', {}).get('hallucination_rate', 0) * 100
            selfcrit_hallu = metrics.get('selfcrit', {}).get('hallucination_rate', 0) * 100
            print(f"   • {api.upper()} - {dataset}: {direct_hallu:.1f}% → {selfcrit_hallu:.1f}% hallucination")
    
    # Import analyzer
    from comprehensive_hallucination_analysis import HallucinationPatternAnalyzer
    
    analyzer = HallucinationPatternAnalyzer()
    analyzer.analyze_all_results(results_data)
    stats = analyzer.get_pattern_statistics()
    
    print(f"\n📈 QUESTION TYPE ANALYSIS:")
    print(f"Found {len(stats)} question types with hallucinations:")
    
    # Sort by frequency
    sorted_types = sorted(stats.items(), key=lambda x: x[1]['total_hallucinations'], reverse=True)
    
    for q_type, data in sorted_types:
        print(f"\n🔸 {q_type}:")
        print(f"   Total cases: {data['total_hallucinations']}")
        print(f"   APIs affected: {', '.join(data['api_distribution'].keys())}")
        print(f"   Common keywords: {', '.join(data['common_keywords'][:3])}")
        print(f"   Sample: {data['sample_questions'][0][:80]}..." if data['sample_questions'] else "")
    
    # Generate recommendations
    recommendations = analyzer.generate_recommendations(stats)
    
    print(f"\n💡 KEY RECOMMENDATIONS:")
    high_risk_types = [q_type for q_type, rec in recommendations.items() if rec['risk_level'] == 'Cao']
    
    if high_risk_types:
        print(f"High-risk question types: {', '.join(high_risk_types)}")
        
        # Show sample recommendations for highest risk type
        if high_risk_types:
            highest_risk = high_risk_types[0]
            print(f"\nRecommendations for '{highest_risk}':")
            for rec in recommendations[highest_risk]['recommendations'][:2]:
                print(f"   ✓ {rec}")
    
    print(f"\n📄 GENERATED REPORTS:")
    report_files = [
        "comprehensive_hallucination_analysis.docx",
        "data/results/openai/report_scientific_facts.docx",
        "data/results/deepseek/report_scientific_facts.docx", 
        "data/results/gemini/report_scientific_facts.docx",
        "data/results/ollama/report_scientific_facts.docx"
    ]
    
    for file in report_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (not found)")
    
    print(f"\n🌐 DASHBOARD ACCESS:")
    print(f"   Main dashboard: http://localhost:8501")
    print(f"   Updated dashboard: http://localhost:8502")
    print(f"   Features:")
    print(f"   • API comparison charts")
    print(f"   • Hallucination case browser")
    print(f"   • Comprehensive analysis generator")
    print(f"   • Enhanced Word reports")

if __name__ == "__main__":
    show_analysis_summary()