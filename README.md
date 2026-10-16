# Mathematical Research Intelligence

An open-source, Python-based research intelligence platform for discovering, processing, validating, and monitoring mathematical research literature.

The project combines an arXiv reporting pipeline with a broader data-engineering architecture built around Python, FastAPI, Celery, Redis, PostgreSQL, Docker, and Next.js.

## Overview

Mathematical Research Intelligence has two complementary components:

1. **Automated Research Reports** — A validated, version-controlled arXiv reporting pipeline executed by GitHub Actions.
2. **Research Data Platform** — A multi-service architecture for academic paper ingestion, persistence, querying, and visualization.

The automated arXiv reporting workflow has been tested locally and on GitHub Actions. The broader multi-source ETL architecture requires further end-to-end validation.

## Verified Features

### Automated arXiv Research Reports

- Fetch mathematical research papers from configured arXiv categories.
- Normalize and deduplicate arXiv identifiers.
- Prefer the highest available explicit paper version.
- Produce deterministic JSON snapshots and Markdown digests.
- Preserve existing reports when fetching or input validation fails.
- Avoid unnecessary commits when generated reports are unchanged.
- Run through GitHub Actions, with manual dispatch also supported.

The default categories are:

| Category | Research area |
|---|---|
| `math.NA` | Numerical Analysis |
| `math.RA` | Rings and Algebras |
| `math.CA` | Classical Analysis and ODEs |
| `math.LO` | Logic |

Categories and fetch limits are configurable in `config.json`.

### Research Data Quality Monitoring

The quality-analysis module evaluates:

- Duplicate arXiv identifiers.
- Missing abstracts.
- Invalid publication dates.
- Noncanonical arXiv URLs.
- Category coverage and cross-listing.
- Earliest and latest publication dates.

Integrity checks are performed before validated reports are published.

These checks assess metadata consistency, not the scientific validity or correctness of individual papers.

### Version-Controlled Reports

The reporting pipeline maintains three files:

| File | Contents |
|---|---|
| `reports/arxiv/latest.json` | Normalized research-paper metadata |
| `reports/arxiv/latest.md` | Human-readable research digest |
| `reports/arxiv/quality.json` | Data-quality statistics and integrity checks |

Outputs are deterministic for identical input data. Files are written only when their contents change.

The three output files are not yet written as a single atomic transaction.

## Automation

The workflow `.github/workflows/research-reports.yml` provides:

- Three scheduled runs per day from Saturday through Tuesday.
- Two scheduled runs on Wednesday.
- One scheduled run per day on Thursday and Friday.
- Sixteen scheduled runs per week in total.
- Manual execution through GitHub Actions.
- Commits only when generated research reports actually change.

GitHub Actions scheduling can be delayed or skipped. Sixteen scheduled runs do not guarantee sixteen executions or sixteen commits.

The repository also contains a separate legacy heartbeat workflow, which is not a research-data update.

## Additional Data Sources

Fetcher implementations exist for:

- Crossref
- OpenAlex
- Semantic Scholar

These components are part of the broader ingestion architecture. Their complete operational integration has not yet been independently verified end-to-end.

## Architecture and Technology

| Layer | Technology |
|---|---|
| Research processing | Python |
| Data collection | arXiv API and additional fetcher modules |
| API | FastAPI |
| Background tasks | Celery |
| Message broker and cache | Redis |
| Database | PostgreSQL and SQLAlchemy |
| Dashboard | Next.js, React, TypeScript |
| Containers | Docker and Docker Compose |
| Validation | Pytest and Ruff |
| Automation | GitHub Actions |

The Docker Compose configuration defines PostgreSQL, Redis, FastAPI, Celery Worker, Celery Beat, and Next.js services.

## Running Research Reports Locally

### Requirements

- Python 3.12 recommended
- Git
- Internet access for fetching arXiv metadata

Clone the repository after its final GitHub rename:

```bash
git clone https://github.com/SoheilGtex/mathematical-research-intelligence.git
cd mathematical-research-intelligence
```

Create a Python environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Generate the reports:

```bash
python scripts/update_arxiv_report.py \
  --output reports/arxiv/latest.json
```

The runner prints `REPORT_UPDATED` if files changed or `REPORT_UNCHANGED` when the output is identical.

Run the test suite and lint checks:

```bash
python -m pytest -q
python -m ruff check .
```

## Docker Development Environment

The repository contains a Docker Compose configuration for its full-stack architecture:

```bash
docker compose up -d --build
```

This configuration is intended for local development and still requires environment-specific validation. It should not be treated as production-ready.

In particular, database and Redis ports are published, example database credentials are embedded in the Compose file, and development bind mounts and reload settings are present.

Inspect and configure these settings before starting the stack, particularly if existing containers or persistent data are present.

The scheduled arXiv reporting workflow does not require Docker, PostgreSQL, or Redis.

## Current Limitations

- Multi-source ETL functionality requires further end-to-end verification.
- Research metadata quality checks do not validate scientific claims.
- The current report focuses on configured arXiv categories and a limited number of recent records.
- GitHub Actions execution times and commit frequency are not guaranteed.
- Multi-file report publication is not transactional.
- Docker Compose is a development-oriented configuration.

## Development and CI

The project uses GitHub Actions for automated checks and container-image publishing to GitHub Container Registry.

Existing container-image identifiers are preserved until their migration and compatibility have been validated.

Contributions should include meaningful changes, appropriate tests, and reproducible validation where possible.

## Maintainer

**Soheil Salmani Safarpour**

- GitHub: https://github.com/SoheilGtex
- LinkedIn: https://www.linkedin.com/in/soheil-salmani-822b89232/
- Email: soheilsalmanisafarpour@gmail.com

## License

Licensed under the MIT License. See [LICENSE](LICENSE).
