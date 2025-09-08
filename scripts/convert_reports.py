#!/usr/bin/env python3
import os, sys, json
import xml.etree.ElementTree as ET
from datetime import datetime

def make_testcase(name, status, suite, severity="medium", message=""):
    now = int(datetime.now().timestamp() * 1000)
    return {
        "name": name,
        "status": status,
        "labels": [
            {"name": "suite", "value": suite},
            {"name": "severity", "value": severity}
        ],
        "start": now,
        "stop": now,
        "statusDetails": {"message": message}
    }

def handle_codeql(report_dir, out_dir):
    if not os.path.isdir(report_dir):
        return
    for f in os.listdir(report_dir):
        if f.endswith(".json"):
            data = json.load(open(os.path.join(report_dir, f)))
            note = data.get("note", "CodeQL Analysis")
            tc = make_testcase(note, "failed", "SAST", "critical",
                               "Voir GitHub Security tab pour détails")
            with open(os.path.join(out_dir, f"codeql-{f}.json"), "w") as out:
                json.dump(tc, out)

def handle_trivy(report_file, out_dir, suite):
    if not os.path.isfile(report_file):
        return
    data = json.load(open(report_file))
    for i, result in enumerate(data.get("Results", [])):
        for vuln in result.get("Vulnerabilities", []):
            sev = vuln.get("Severity", "MEDIUM").lower()
            tc = make_testcase(
                vuln.get("VulnerabilityID", f"{suite}-{i}"),
                "failed", suite, sev,
                vuln.get("Description", "")
            )
            name = f"{suite}-{i}-{vuln.get('VulnerabilityID','vuln')}.json"
            with open(os.path.join(out_dir, name), "w") as out:
                json.dump(tc, out)

def handle_zap(report_file, out_dir):
    if not os.path.isfile(report_file):
        return
    tree = ET.parse(report_file)
    root = tree.getroot()
    for i, alert in enumerate(root.findall(".//alertitem")):
        name = alert.findtext("alert") or f"zap-{i}"
        desc = alert.findtext("desc") or ""
        risk = (alert.findtext("riskdesc") or "medium").split()[0].lower()
        tc = make_testcase(name, "failed", "DAST", risk, desc)
        with open(os.path.join(out_dir, f"zap-{i}-{name}.json"), "w") as out:
            json.dump(tc, out)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: convert_reports.py <reports_dir> <out_dir>")
        sys.exit(1)

    reports_dir, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    handle_codeql(os.path.join(reports_dir, "codeql-report"), out_dir)
    handle_trivy(os.path.join(reports_dir, "trivy-sca.json"), out_dir, "SCA")
    handle_trivy(os.path.join(reports_dir, "trivy-image.json"), out_dir, "ImageScan")
    handle_zap(os.path.join(reports_dir, "zap-report.xml"), out_dir)

    print(f"[+] Conversion terminée. Résultats Allure dans {out_dir}")
