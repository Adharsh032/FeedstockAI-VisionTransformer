import io
import csv
from typing import Dict, Any, List

def generate_csv_report(history: List[Dict[str, Any]]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Inspection ID",
        "Timestamp",
        "Source File",
        "Defect Detected",
        "Class ID",
        "Class Name",
        "Quality Grade",
        "Quality Score",
        "Defect Area %",
        "Defect Regions Count",
        "Final Verdict"
    ])

    for h in history:
        writer.writerow([
            h.get("inspection_id", ""),
            h.get("timestamp", ""),
            h.get("source_filename", ""),
            "YES" if h.get("is_defective") else "NO",
            h.get("class_id", 0),
            h.get("class_name", ""),
            h.get("quality_grade", ""),
            h.get("quality_score", 0.0),
            f"{h.get('defect_area_pct', 0.0)}%",
            h.get("regions_count", 0),
            h.get("verdict", "")
        ])

    return output.getvalue()


def generate_html_certificate(data: Dict[str, Any]) -> str:
    """Generates a professional, printable Industry 4.0 Certificate of Quality Inspection."""
    insp_id = data.get("inspection_id", "INSP-001")
    ts = data.get("timestamp", "2026-10-12 17:00:00")
    source = data.get("source_filename", "feedstock_sample.jpg")
    verdict = data.get("verdict", "APPROVED")
    grade = data.get("quality_grade", "Grade A (Prime)")
    score = data.get("quality_score", 98.5)
    class_name = data.get("class_name", "Prime Material")
    area_pct = data.get("defect_area_pct", 0.0)
    meta = data.get("class_metadata", {})
    action = meta.get("recommended_action", "Proceed with standard production.")

    badge_color = "#2ecc71" if "APPROVED" in verdict else ("#f39c12" if "CONDITIONAL" in verdict else "#e74c3c")

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Quality Inspection Certificate - {insp_id}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0b0f19; color: #f1f5f9; padding: 40px; margin: 0; }}
        .cert-container {{ max-width: 800px; margin: 0 auto; background: #131b2e; border: 1px solid #1e293b; border-radius: 12px; padding: 36px; box-shadow: 0 20px 40px rgba(0,0,0,0.6); }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #334155; padding-bottom: 20px; }}
        .header h1 {{ margin: 0; font-size: 22px; color: #38bdf8; text-transform: uppercase; letter-spacing: 1px; }}
        .header p {{ margin: 4px 0 0 0; color: #94a3b8; font-size: 13px; }}
        .verdict-banner {{ margin: 24px 0; padding: 18px; border-radius: 8px; text-align: center; font-size: 20px; font-weight: 700; letter-spacing: 1.5px; background: rgba(255,255,255,0.05); border: 2px solid {badge_color}; color: {badge_color}; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 24px 0; }}
        .field {{ background: #0f172a; padding: 14px 18px; border-radius: 8px; border: 1px solid #1e293b; }}
        .field-label {{ font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 4px; }}
        .field-value {{ font-size: 16px; color: #f8fafc; font-weight: 600; }}
        .section-title {{ font-size: 14px; text-transform: uppercase; color: #38bdf8; font-weight: 700; letter-spacing: 1px; margin: 28px 0 12px; }}
        .action-box {{ background: #1e1b4b; border-left: 4px solid #818cf8; padding: 16px; border-radius: 0 8px 8px 0; color: #e0e7ff; font-size: 14px; line-height: 1.5; }}
        .footer {{ margin-top: 36px; padding-top: 20px; border-top: 1px solid #334155; display: flex; justify-content: space-between; font-size: 11px; color: #64748b; }}
        @media print {{ body {{ background: #fff; color: #000; }} .cert-container {{ background: #fff; border: 1px solid #ccc; color: #000; }} }}
    </style>
</head>
<body>
    <div class="cert-container">
        <div class="header">
            <div>
                <h1>Certificate of Quality Inspection</h1>
                <p>Industry 4.0 Intelligent Vision Transformer System</p>
            </div>
            <div style="text-align: right;">
                <div style="font-weight: 700; color: #38bdf8;">{insp_id}</div>
                <div style="font-size: 12px; color: #94a3b8;">{ts}</div>
            </div>
        </div>

        <div class="verdict-banner">
            {verdict}
        </div>

        <div class="grid">
            <div class="field">
                <div class="field-label">Feedstock Sample / Batch</div>
                <div class="field-value">{source}</div>
            </div>
            <div class="field">
                <div class="field-label">Assessed Quality Grade</div>
                <div class="field-value">{grade}</div>
            </div>
            <div class="field">
                <div class="field-label">Quality Score</div>
                <div class="field-value">{score} / 100</div>
            </div>
            <div class="field">
                <div class="field-label">Identified Classification</div>
                <div class="field-value">{class_name}</div>
            </div>
            <div class="field">
                <div class="field-label">Defect Area Affected</div>
                <div class="field-value">{area_pct}%</div>
            </div>
            <div class="field">
                <div class="field-label">Inspection Engine</div>
                <div class="field-value">ViT-Patch16 Transformer</div>
            </div>
        </div>

        <div class="section-title">Industrial Process Action Directive</div>
        <div class="action-box">
            {action}
        </div>

        <div class="footer">
            <div>Verified by Automated AI Quality Station #04</div>
            <div>Pondicherry University &bull; AIML Dept. &bull; Patent Ref #FeedStock-ViT-2026</div>
        </div>
    </div>
</body>
</html>"""
    return html
