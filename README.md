# 📡 Math Research Radar

An automated data pipeline to track, store, and analyze new Mathematics papers from arXiv.
Built with Python, Data Engineering best practices, and orchestrated by GitHub Actions.

## 🚀 How It Works
This repository uses a Python pipeline to daily fetch the latest mathematics research papers based on the categories defined in `config.json`. The data is deduplicated, stored in daily JSON logs, and statistical summaries are generated automatically.

### Running Locally
To set up this pipeline on your local macOS environment:

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Execute the full pipeline (Fetch -> Aggregate -> Update README)
python main.py