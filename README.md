# 🔭 Math Research Radar

An automated Research Intelligence Platform that extracts, deduplicates, and aggregates mathematical research papers from primary global sources (arXiv, Crossref, OpenAlex, Semantic Scholar) into a centralized PostgreSQL database.

## Architecture Highlights
- **Data Engineering:** Object-Oriented Fetchers with robust retry mechanisms.
- **Storage:** Idempotent PostgreSQL database integration via SQLAlchemy.
- **DevOps:** Fully containerized with Multi-stage Docker builds and Docker Compose orchestration.
- **Analytics:** Automated daily aggregation of category statistics.
- **Presentation:** Static dashboard generation for data visualization.

## Quick Start (Docker)
```bash
docker compose up --build