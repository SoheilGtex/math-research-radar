import sys

from radar.logger import setup_global_logger
from radar.fetchers.arxiv import run_arxiv_pipeline
from radar.fetchers.crossref import run_crossref_pipeline
from radar.analytics.stats import generate_statistics
from radar.reporting.readme import generate_readme
from radar.dashboard.generator import build_dashboard

# Initialize enterprise logging
logger = setup_global_logger()

def main():
    logger.info("Starting the Math Research Radar pipeline...")
    
    # --- FETCHING STAGE ---
    logger.info("🚀 Running Module: arXiv Fetcher...")
    try:
        run_arxiv_pipeline()
        logger.info("✅ Finished arXiv Fetcher successfully.\n")
    except Exception as e:
        logger.error(f"❌ Pipeline failed during arXiv fetch: {e}")
    
    logger.info("🚀 Running Module: Crossref Fetcher...")
    try:
        run_crossref_pipeline()
        logger.info("✅ Finished Crossref Fetcher successfully.\n")
    except Exception as e:
        logger.error(f"❌ Pipeline failed during Crossref fetch: {e}")
        
    # --- ANALYTICS & REPORTING STAGE ---
    logger.info("🚀 Running Module: Analytics Generator...")
    try:
        generate_statistics()
        logger.info("✅ Finished Analytics Generator successfully.\n")
    except Exception as e:
        logger.error(f"❌ Pipeline failed during analytics generation: {e}")
        sys.exit(1)

    logger.info("🚀 Running Module: README Generator...")
    try:
        generate_readme()
        logger.info("✅ Finished README Generator successfully.\n")
    except Exception as e:
        logger.error(f"❌ Pipeline failed during README generation: {e}")
        sys.exit(1)
    
    logger.info("🚀 Running Module: Dashboard Generator...")
    try:
        build_dashboard()
        logger.info("✅ Finished Dashboard Generator successfully.\n")
    except Exception as e:
        logger.error(f"❌ Pipeline failed during Dashboard generation: {e}")
        sys.exit(1)
        
    logger.info("🎉 Entire pipeline executed successfully!")

if __name__ == "__main__":
    main()