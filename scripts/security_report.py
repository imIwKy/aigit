import argparse
import json
from dataclasses import dataclass
from pathlib import Path

SEVERITIES = ("Critical", "High", "Medium", "Low", "Unknown")


@dataclass
class Finding:
    source: str
    identifier: str
    severity: str
    location: str
    description: str
    fix: str = ""


def normalize_severity(value: object) -> str:
    if not isinstance(value, str):
        return "Unknown"

    severity = value.strip().capitalize()

    if severity in SEVERITIES:
        return severity

    return "Unknown"


def load_bandit_findings(path: Path) -> list[Finding]:
    data = json.loads(path.read_text(encoding="utf-8"))
    findings: list[Finding] = []

    for result in data.get("results", []):
        findings.append(
            Finding(
                source="Bandit",
                identifier=result.get("test_id", "Unknown"),
                severity=normalize_severity(result.get("issue_severity")),
                location=(
                    f"{result.get('filename', 'Unknown')}:"
                    f"{result.get('line_number', '?')}"
                ),
                description=result.get(
                    "issue_text",
                    "No description provided.",
                ),
            )
        )

    return findings


def load_pip_audit_findings(path: Path) -> list[Finding]:
    data = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(data, dict):
        packages = data.get("dependencies", [])
    elif isinstance(data, list):
        # Supports older or alternate pip-audit output formats.
        packages = data
    else:
        packages = []

    findings: list[Finding] = []

    for package in packages:
        if not isinstance(package, dict):
            continue

        package_name = package.get("name", "Unknown")
        package_version = package.get("version", "Unknown")

        for vulnerability in package.get("vulns", []):
            if not isinstance(vulnerability, dict):
                continue

            aliases = vulnerability.get("aliases", [])
            identifier = aliases[0] if aliases else vulnerability.get("id", "Unknown")

            fix_versions = vulnerability.get("fix_versions", [])

            findings.append(
                Finding(
                    source="pip-audit",
                    identifier=identifier,
                    severity=normalize_severity(vulnerability.get("severity")),
                    location=f"{package_name} {package_version}",
                    description=vulnerability.get(
                        "description",
                        "No description provided.",
                    ),
                    fix=", ".join(fix_versions),
                )
            )

    return findings


def escape_markdown(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def build_report(findings: list[Finding]) -> str:
    counts = {severity: 0 for severity in SEVERITIES}

    for finding in findings:
        counts[finding.severity] += 1

    lines = [
        "# Security Vulnerability Report",
        "",
        "## Summary",
        "",
        "| Severity | Count |",
        "|---|---:|",
    ]

    for severity in SEVERITIES:
        lines.append(f"| {severity} | {counts[severity]} |")

    lines.extend(
        [
            "",
            "## Findings",
            "",
            "| Source | ID | Severity | Location | Description | Fix |",
            "|---|---|---|---|---|---|",
        ]
    )

    if not findings:
        lines.append("| - | - | - | - | No vulnerabilities found. | - |")
    else:
        for finding in findings:
            lines.append(
                "| "
                f"{escape_markdown(finding.source)} | "
                f"{escape_markdown(finding.identifier)} | "
                f"{escape_markdown(finding.severity)} | "
                f"{escape_markdown(finding.location)} | "
                f"{escape_markdown(finding.description)} | "
                f"{escape_markdown(finding.fix)} |"
            )

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate Bandit and pip-audit reports."
    )
    parser.add_argument(
        "--bandit",
        type=Path,
        default=Path("bandit-report.json"),
    )
    parser.add_argument(
        "--pip-audit",
        type=Path,
        default=Path("pip-audit-report.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("security-report.md"),
    )

    args = parser.parse_args()
    findings: list[Finding] = []

    if args.bandit.exists():
        findings.extend(load_bandit_findings(args.bandit))

    if args.pip_audit.exists():
        findings.extend(load_pip_audit_findings(args.pip_audit))

    args.output.write_text(
        build_report(findings),
        encoding="utf-8",
    )

    print(f"Security report written to {args.output}")


if __name__ == "__main__":
    main()
