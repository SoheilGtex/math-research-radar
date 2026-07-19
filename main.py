import logging
import subprocess
import sys

from radar.analytics.stats import generate_statistics
from radar.fetchers.arxiv import run_arxiv_pipeline
from radar.reporting.readme import generate_readme

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("pipeline")

def run_legacy_script(script_path: str) -> None:
    """Run a legacy python script as a subprocess."""
    logger.info(f"🚀 Starting legacy script: {script_path}...")
    try:
        subprocess.run([sys.executable, script_path], check=True)
        logger.info(f"✅ Finished {script_path} successfully.\n")
    except subprocess.CalledProcessError:
        logger.error(f"❌ Pipeline failed! Error occurred while running {script_path}.")
        sys.exit(1)

def main():
    logger.info("Starting the Math Research Radar pipeline...")
    
    # 1. Execute Native Modules
    logger.info("🚀 Running Native Module: arXiv Fetcher...")
    try:
        run_arxiv_pipeline()
        logger.info("✅ Finished arXiv Fetcher successfully.\n")
    except Exception as e:
        logger.error(f"❌ Pipeline failed during arXiv fetch: {e}")
        sys.exit(1)
        
    logger.info("🚀 Running Native Module: Analytics Generator...")
    try:
        generate_statistics()
        logger.info("✅ Finished Analytics Generator successfully.\n")
    except Exception as e:
        logger.error(f"❌ Pipeline failed during analytics generation: {e}")
        sys.exit(1)

    logger.info("🚀 Running Native Module: README Generator...")
    try:
        generate_readme()
        logger.info("✅ Finished README Generator successfully.\n")
    except Exception as e:
        logger.error(f"❌ Pipeline failed during README generation: {e}")
        sys.exit(1)
    
    # 2. Execute Legacy Scripts
    legacy_steps = [
        "scripts/generate_dashboard.py"
    ]
    
    for step in legacy_steps:
        run_legacy_script(step)
        
    logger.info("🎉 Entire pipeline executed successfully!")

if __name__ == "__main__":
    main()