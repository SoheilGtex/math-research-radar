import os
import json
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DOCS_DIR = "docs"
STATS_FILE = "stats/categories.json"
HTML_PATH = os.path.join(DOCS_DIR, "index.html")

def build_dashboard() -> None:
    """Generate a static HTML dashboard using Chart.js based on daily statistics."""
    logger.info("Starting dashboard generation...")
    
    os.makedirs(DOCS_DIR, exist_ok=True)
    
    categories = []
    counts = []
    
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                stats = json.load(f)
                for cat, count in sorted(stats.items()):
                    categories.append(cat)
                    counts.append(count)
        except Exception as e:
            logger.error(f"Failed to read stats: {e}")
            
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Math Research Radar Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f6f8fa; margin: 0; padding: 20px; color: #24292f; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }}
        h1 {{ text-align: center; color: #0969da; }}
        .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #57606a; }}
        canvas {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📡 Math Research Radar</h1>
        <p style="text-align: center;">Automated daily tracker for arXiv mathematics papers.</p>
        
        <canvas id="categoryChart"></canvas>
        
        <div class="footer">
            Last updated: {now_utc}
        </div>
    </div>

    <script>
        const ctx = document.getElementById('categoryChart').getContext('2d');
        const categoryChart = new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(categories)},
                datasets: [{{
                    label: 'Number of Papers Tracked',
                    data: {json.dumps(counts)},
                    backgroundColor: 'rgba(9, 105, 218, 0.6)',
                    borderColor: 'rgba(9, 105, 218, 1)',
                    borderWidth: 1,
                    borderRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: true, ticks: {{ precision: 0 }} }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    logger.info(f"Successfully generated dashboard at {HTML_PATH}")

if __name__ == "__main__":
    build_dashboard()