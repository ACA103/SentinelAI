import os
import subprocess
import sys

def main():
    os.environ["STREAMLIT_CONFIG_DIR"] = os.path.join(os.getcwd(), ".streamlit")
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    os.environ["STREAMLIT_HEADLESS"] = "true"
    os.environ["PYTHONPATH"] = os.getcwd()
    print("Starting SentinelAI Application via Hugging Face Entrypoint...")
    
    # 1. Run Pipeline Orchestrator if data doesn't exist
    if not os.path.exists("data/predictions/explanations.parquet"):
        print("Running pipeline to generate data...")
        subprocess.run([sys.executable, "-m", "src.runtime.orchestrator"], check=True)
        
    # 2. Launch Streamlit
    print("Launching Streamlit Dashboard...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "src/ui/app.py", "--server.port=7860", "--server.address=0.0.0.0", "--browser.gatherUsageStats=false", "--server.headless=true"])

if __name__ == "__main__":
    main()
