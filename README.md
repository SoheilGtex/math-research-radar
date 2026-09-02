# 🧭 Math Research Radar

An automated, full-stack Research Intelligence Platform designed to track, extract, deduplicate, and categorize the latest mathematics research papers from multiple global academic sources (arXiv, Crossref, OpenAlex, Semantic Scholar). 

Transitioned from a static scraper into a robust, event-driven ETL architecture, this platform ensures high performance, scalability, and maintainability for monitoring mathematical literature.

## ✨ Key Features
* **Automated ETL Pipelines:** Background workers continuously fetch, clean, and deduplicate research papers.
* **Modern Stack:** RESTful API built with **FastAPI** and a responsive dashboard powered by **Next.js**.
* **Asynchronous Task Queue:** **Celery** and **Redis** handle heavy data extraction tasks without blocking the main thread.
* **Relational Database:** Persistent storage and advanced querying using **PostgreSQL**.
* **Containerized Architecture:** Fully orchestrated multi-container environment using **Docker Compose**.
* **CI/CD Integration:** Automated linting, testing, and Docker image publishing to GitHub Container Registry (GHCR) via GitHub Actions.

## 🏗️ Architecture
The project follows a Monorepo structure, encapsulating five core services:
1. **API Service:** FastAPI backend serving research data and statistics.
2. **Web Frontend:** Next.js application for data visualization and reading.
3. **Worker:** Celery workers executing scheduled scraping tasks.
4. **Message Broker:** Redis for task queuing and caching.
5. **Database:** PostgreSQL for persistent state and data warehousing.

## 🚀 Quick Start (Local Deployment)

Since the system is fully containerized, you can launch the entire stack on your local machine with a single command.

### Prerequisites
* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)

### Installation

1. **Clone the repository:**
```bash
git clone [https://github.com/SoheilGtex/math-research-radar.git](https://github.com/SoheilGtex/math-research-radar.git)
cd math-research-radar
```

2. **Start the platform:**
```bash
docker compose up -d --build
```

3. **Access the services:**
* Frontend Dashboard: `http://localhost:3000`
* API Interactive Docs (Swagger): `http://localhost:8000/docs`

## 🛠️ Tech Stack
* **Language:** Python 3.12, TypeScript
* **Backend:** FastAPI, SQLAlchemy, Pydantic
* **Frontend:** Next.js, React, Tailwind CSS
* **Task Queue:** Celery, Redis
* **Database:** PostgreSQL
* **DevOps:** Docker, GitHub Actions, Ruff, Pytest

## 📬 Contact & Author
Developed and maintained by **Soheil Salmani Safarpour** (Data Engineer / Analytics Engineer).
* **Email:** [soheilsalmanisafarpour@gmail.com](mailto:soheilsalmanisafarpour@gmail.com)
* **LinkedIn:** [Soheil Salmani](https://www.linkedin.com/in/soheil-salmani-822b89232/)

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.