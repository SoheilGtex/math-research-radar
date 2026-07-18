import subprocess
import logging
import sys

# Configure logging for the orchestrator
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pipeline")


def run_script(script_path: str) -> None:
    """
    Run a python script as a subprocess and check for errors.
    """
    logger.info(f"🚀 Starting {script_path}...")
    try:
        # sys.executable ensures we use the exact same Python interpreter (the virtual environment)
        subprocess.run([sys.executable, script_path], check=True)
        logger.info(f"✅ Finished {script_path} successfully.\n")
    except subprocess.CalledProcessError:
        logger.error(f"❌ Pipeline failed! Error occurred while running {script_path}.")
        # Exit with error code to fail the CI/CD pipeline in GitHub Actions
        sys.exit(1)


def main():
    logger.info("Starting the Math Research Radar pipeline...")

    # The strict order of execution
    pipeline_steps = [
        "scripts/fetch.py",
        "scripts/update_stats.py",
        "scripts/update_readme.py",
    ]

    for step in pipeline_steps:
        run_script(step)

    logger.info("🎉 Entire pipeline executed successfully!")


if __name__ == "__main__":
    main()
