"""Local-only, self-contained report renderer."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "web" / "report.html"


def render_html(report: dict[str, Any] | None) -> str:
    template = TEMPLATE.read_text(encoding="utf-8")
    if report is None:
        content = "null"
    else:
        content = json.dumps(report, ensure_ascii=False, separators=(",", ":"))
        # This data appears inside a script tag. Do not permit tag termination.
        content = content.replace("<", "\\u003c").replace(">", "\\u003e")
        content = content.replace("&", "\\u0026").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return template.replace("/*__REPORT_DATA__*/", content)
