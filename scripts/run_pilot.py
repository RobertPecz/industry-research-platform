import json
from pathlib import Path

import yaml

from industry_research.analysis import classify, report
from industry_research.collect import collect
from industry_research.db import connect

with connect("data/research.sqlite") as db:
    counts = collect(db, yaml.safe_load(Path("config/sources.yaml").read_text()), 30)
    classify(db)
    Path("reports/collection_summary.json").write_text(json.dumps(counts, indent=2))
    Path("reports/pilot_report.md").write_text(report(db))
    print(counts)
