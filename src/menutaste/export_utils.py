from __future__ import annotations

import json
from .models import AgentReport


def report_to_json(report: AgentReport) -> str:
    return json.dumps(report.model_dump(), indent=2, ensure_ascii=False)
