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

1. **[Associação da atividade física na saúde materna](https://doi.org/10.47385/cedvr.2794.7.2026)**
   - *Category: math.NA | Source: crossref | Published: 2026-09-01*
1. **[Formação esportiva na infância e desenvolvimento integral](https://doi.org/10.47385/cedvr.2795.7.2026)**
   - *Category: math.NA | Source: crossref | Published: 2026-09-01*
1. **[Enhancing mathematics teachers’ contextualization of mathematics content in welding and fabrication courses using ChatGPT and Meta AI](https://doi.org/10.1007/s44217-026-02067-8)**
   - *Category: math.NA | Source: crossref | Published: 2026-09-01*
1. **[Benefícios do treinamento funcional na economia de corrida e prevenção de lesões em corredores](https://doi.org/10.47385/cedvr.2796.7.2026)**
   - *Category: math.NA | Source: crossref | Published: 2026-09-01*
1. **[IТЕРАЦIЙНИЙ ДВОСТОРОННIЙ МЕТОД РОЗВ’ЯЗУВАННЯ IНТЕГРАЛЬНИХ РIВНЯНЬ](https://doi.org/10.30970/vam.2026.36.14038)**
   - *Category: math.NA | Source: crossref | Published: 2026-09-01*

<!-- LATEST_PAPERS_END -->
