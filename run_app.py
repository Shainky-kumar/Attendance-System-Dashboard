import os
import sys

# Set working directory to where this script is located
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Launch your Streamlit app
os.system('streamlit run "app1.py"')
