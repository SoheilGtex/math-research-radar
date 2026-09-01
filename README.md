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

<!-- LATEST_PAPERS_START -->
### 📄 Latest Discovered Papers

1. **[Pharmacodynamic modeling of colistin and imipenem against in vitro Pseudomonas aeruginosa biofilms.](https://doi.org/10.1016/j.bioflm.2026.100387)**
   - *Category: math.CA | Source: openalex | Published: 2026-12-01*
1. **[Interpol review of gunshot residue, 2022 to 2024.](https://doi.org/10.1016/j.fsisyn.2026.100719)**
   - *Category: math.CA | Source: openalex | Published: 2026-12-01*
1. **[Understanding How Location Analytics Is Implemented in Information Systems and Business Education](https://doi.org/10.62273/mopz1492)**
   - *Category: math.CA | Source: openalex | Published: 2026-09-15*
1. **[Copies, Collaborations, and Gifts: Artistic Production Practices and Pricing in the Chinese Art Market](https://openalex.org/W7204671484)**
   - *Category: math.CA | Source: openalex | Published: 2026-09-04*
1. **[A novel demand response framework for the optimal design of hydrogen–ammonia hybrid microgrids](https://openalex.org/W7162220708)**
   - *Category: math.CA | Source: openalex | Published: 2026-09-15*

<!-- LATEST_PAPERS_END -->
