"""
Enhanced Hallucination Detection Dashboard for Streamlit Cloud
Streamlit Cloud entry point optimized for cloud deployment
"""
import streamlit as st
import sys
import os
from pathlib import Path

# Add project paths to Python path
current_dir = Path(__file__).parent
ui_dir = current_dir / "ui"
sys.path.append(str(current_dir))
sys.path.append(str(ui_dir))

# Now import the main app
try:
    from ui.app import main, setup_paths
    
    # Setup paths for cloud environment
    setup_paths()
    
    # Set page config
    st.set_page_config(
        page_title="🔍 Enhanced Hallucination Detection Dashboard",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Run main app
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    st.error(f"""
    **Import Error**: {str(e)}
    
    This appears to be an issue with the app structure. 
    Please check that all required files are present:
    - ui/app.py
    - ui/components/enhanced_analytics.py
    
    **For local development**: Run `streamlit run ui/app.py` instead
    """)
    
except Exception as e:
    st.error(f"""
    **Application Error**: {str(e)}
    
    There was an unexpected error starting the application.
    Please check the logs for more details.
    """)