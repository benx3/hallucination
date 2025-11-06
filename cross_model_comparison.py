#!/usr/bin/env python3
"""
Wrapper script for cross_model_comparison.py
Redirects to scripts/cross_model_comparison.py for backward compatibility
"""

import sys
import os
from pathlib import Path

# Add scripts directory to path
project_root = Path(__file__).parent
scripts_dir = project_root / "scripts"
sys.path.insert(0, str(scripts_dir))

# Change working directory to project root
os.chdir(project_root)

# Import and run the actual script
if __name__ == "__main__":
    try:
        # Import the actual cross_model_comparison module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "cross_model_comparison", 
            scripts_dir / "cross_model_comparison.py"
        )
        cross_model_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cross_model_module)
        
        # Run main function if exists
        if hasattr(cross_model_module, 'main'):
            cross_model_module.main()
        elif hasattr(cross_model_module, 'run_analysis'):
            cross_model_module.run_analysis()
        else:
            print("✅ Cross-model comparison script executed")
            
    except Exception as e:
        print(f"❌ Error running cross-model comparison: {e}")
        sys.exit(1)