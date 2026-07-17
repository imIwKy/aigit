import json

from scripts.security_report import load_pip_audit_findings


def test_load_pip_audit_findings_reads_dependencies_object(tmp_path) -> None:
    report_path = tmp_path / "pip-audit.json"
    report_path.write_text(
        json.dumps(
            {
                "dependencies": [
                    {
                        "name": "setuptools",
                        "version": "79.0.1",
                        "vulns": [
                            {
                                "id": "PYSEC-2026-3447",
                                "aliases": ["CVE-2026-59890"],
                                "fix_versions": ["83.0.0"],
                                "description": "Example vulnerability",
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    findings = load_pip_audit_findings(report_path)

    assert len(findings) == 1
    assert findings[0].source == "pip-audit"
    assert findings[0].identifier == "CVE-2026-59890"
    assert findings[0].location == "setuptools 79.0.1"
    assert findings[0].fix == "83.0.0"
