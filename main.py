"""
Main entry point for Hallucination Detection Research Project
"""

import sys
import os

def main():
    """Main menu for the research project"""
    print("🧠 Hallucination Detection Research Project")
    print("=" * 50)
    print()
    print("Choose an option:")
    print("1. 🖥️  Launch Web UI")
    print("2. 🚀 Run Complete Experiment")
    print("3. 📊 Run Single API Experiment")
    print("4. 📈 Generate Reports Only")
    print("5. 📚 View Documentation")
    print("0. ❌ Exit")
    print()
    
    choice = input("Enter your choice (0-5): ").strip()
    
    if choice == "1":
        launch_ui()
    elif choice == "2":
        run_complete_experiment()
    elif choice == "3":
        run_single_experiment()
    elif choice == "4":
        generate_reports()
    elif choice == "5":
        show_docs()
    elif choice == "0":
        print("Goodbye! 👋")
        sys.exit(0)
    else:
        print("❌ Invalid choice. Please try again.")
        main()

def launch_ui():
    """Launch the Streamlit web UI"""
    print("🖥️  Launching Web UI...")
    print("📍 URL: http://localhost:8501")
    print("💡 Tip: Copy configs/config.example.json to configs/config.json first")
    print()
    
    try:
        import subprocess
        # Use the virtual environment Python
        venv_python = r"E:\ThacSi\NLP\week5\halu2\.venv\Scripts\python.exe"
        subprocess.run([
            venv_python, "-m", "streamlit", "run", "ui/app.py"
        ])
    except KeyboardInterrupt:
        print("\n🛑 UI stopped by user")
    except Exception as e:
        print(f"❌ Error launching UI: {e}")

def run_complete_experiment():
    """Run experiments across all APIs"""
    print("🚀 Running Complete Experiment...")
    print("📋 This will test all APIs with all datasets")
    print()
    
    confirm = input("Continue? (y/N): ").strip().lower()
    if confirm != 'y':
        print("⏸️  Cancelled")
        return
    
    try:
        from run_experiment import run_complete_experiment
        run_complete_experiment()
    except Exception as e:
        print(f"❌ Error running experiment: {e}")

def run_single_experiment():
    """Run experiment with single API"""
    print("📊 Single API Experiment")
    print()
    
    print("Available APIs:")
    apis = ["openai", "deepseek", "gemini", "ollama"]
    for i, api in enumerate(apis, 1):
        print(f"{i}. {api.title()}")
    
    choice = input("Choose API (1-4): ").strip()
    try:
        api_index = int(choice) - 1
        if 0 <= api_index < len(apis):
            selected_api = apis[api_index]
            print(f"🎯 Selected: {selected_api}")
            
            # Run single API experiment
            os.environ["API_PROVIDER"] = selected_api
            
            try:
                sys.path.append('src')
                from src.api_runner import main as run_api
                run_api()
            except Exception as e:
                print(f"❌ Error running {selected_api}: {e}")
        else:
            print("❌ Invalid choice")
    except ValueError:
        print("❌ Please enter a number")

def generate_reports():
    """Generate evaluation reports"""
    print("📈 Generating Reports...")
    
    try:
        sys.path.append('src')
        from src.evaluator import main as run_evaluator
        run_evaluator()
    except Exception as e:
        print(f"❌ Error generating reports: {e}")

def show_docs():
    """Show documentation"""
    print("📚 Documentation")
    print("=" * 30)
    print()
    print("Available documents:")
    print("• docs/QUICK_START.md - Quick start guide")
    print("• docs/README_UI.md - UI user guide")
    print("• docs/README_COMPLETE_EXPERIMENT.md - Experiment guide")
    print("• .github/copilot-instructions.md - Technical architecture")
    print()
    print("💡 Open these files in your text editor or VS Code")

if __name__ == "__main__":
    main()