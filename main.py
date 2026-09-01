import logging
from radar.db import Base, engine
from radar.fetchers.arxiv import run_arxiv_pipeline
from radar.fetchers.crossref import run_crossref_pipeline
from radar.fetchers.openalex import run_openalex_pipeline
from radar.fetchers.semantic_scholar import run_semantic_scholar_pipeline
from radar.analytics.stats import generate_statistics
from radar.reporting.readme import generate_readme

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("pipeline")

def main():
    logger.info("Starting the Math Research Radar pipeline...")
    logger.info("⚙️ Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables verified/created successfully.\n")

    logger.info("🚀 Running Module: arXiv Fetcher...")
    run_arxiv_pipeline()
    logger.info("✅ Finished arXiv Fetcher successfully.\n")

    logger.info("🚀 Running Module: Crossref Fetcher...")
    run_crossref_pipeline()
    logger.info("✅ Finished Crossref Fetcher successfully.\n")

    logger.info("🚀 Running Module: OpenAlex Fetcher...")
    run_openalex_pipeline()
    logger.info("✅ Finished OpenAlex Fetcher successfully.\n")

    logger.info("🚀 Running Module: Semantic Scholar Fetcher...")
    run_semantic_scholar_pipeline()
    logger.info("✅ Finished Semantic Scholar Fetcher successfully.\n")

    logger.info("🚀 Running Module: Analytics Generator...")
    generate_statistics()
    logger.info("✅ Finished Analytics Generator successfully.\n")

    logger.info("🚀 Running Module: README Generator...")
    generate_readme()
    logger.info("✅ Finished README Generator successfully.\n")

    logger.info("🎉 Entire pipeline executed successfully!")

if __name__ == "__main__":
    main()