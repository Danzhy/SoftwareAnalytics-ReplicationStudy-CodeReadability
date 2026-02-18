#!/usr/bin/env python3
"""
Parse CountOccurrences.java output and produce a formatted table.

Usage:
  java -cp replication_scripts/RQ2 CountOccurrences | python3 replication_scripts/RQ2/parseOutput.py

Or with a saved output file:
  python3 replication_scripts/RQ2/parseOutput.py < output.txt
"""

import csv
import os
import re
import sys

# SonarQube rule descriptions (readability-related rules from the "yes" set in CountOccurrences.java)
RULE_DESCRIPTIONS = {
    "java:S1124": "Floating point numbers should not be tested for equality",
    "java:S1141": "Use a lambda or method reference instead of an anonymous class",
    "java:S1192": "Define a constant instead of duplicating string literals",
    "java:S1066": "Use the opposite operator",
    "java:S3776": "Cognitive Complexity of methods should not be too high",
    "java:S1197": "Use the opposite operator",
    "java:S125": "Remove commented-out code",
    "java:S1155": "Use the opposite operator",
    "java:S1117": "Local variable and method parameter names should comply with naming convention",
    "java:S1450": "Use the opposite operator",
    "java:S1604": "Use the opposite operator",
    "java:S120": "Field names should comply with naming convention",
    "java:S2093": "Try-with-resources should be used",
    "java:S117": "Static non-final field names should comply with naming convention",
    "java:S1602": "Use the opposite operator",
    "java:S1611": "Remove redundant parentheses",
    "java:S135": "Loops should not contain more than one break or continue",
    "java:S1301": "Use the opposite operator",
    "java:S100": "Method names should comply with naming convention",
    "java:S1612": "Replace lambda with method reference",
    "java:S1144": "Use the opposite operator",
    "java:S106": "Replace System.out/err by a logger",
    "java:S1659": "Use the opposite operator",
    "java:S2293": "Use diamond operator",
    "java:S1199": "Use the opposite operator",
    "java:S116": "Overloaded methods should be grouped together",
    "java:S4201": "Use the opposite operator",
    "java:S3358": "Extract nested ternary into independent statement",
    "java:S3008": "Use the opposite operator",
    "java:S1125": "Remove unnecessary boolean literal",
    "java:S1126": "Replace if-then-else by single return",
    "java:S127": "Use the opposite operator",
    "java:S1116": "Use the opposite operator",
    "java:S2147": "Use the opposite operator",
    "java:S1871": "Use the opposite operator",
    "java:S3878": "Use the opposite operator",
    "java:S1161": "Use the opposite operator",
    "java:S6213": "Use the opposite operator",
    "java:S1700": "Use the opposite operator",
    "java:S1121": "Use the opposite operator",
    "java:S3824": "Use the opposite operator",
    "java:S6353": "Use the opposite operator",
    "java:S1153": "Use the opposite operator",
    "java:S3012": "Use the opposite operator",
    "java:S1119": "Use the opposite operator",
    "java:S5261": "Use the opposite operator",
    "java:S119": "Generic names should comply with naming convention",
    "java:S1940": "Use the opposite operator",
    "java:S1905": "Use the opposite operator",
    "java:S3972": "Use the opposite operator",
    "java:S1264": "Use the opposite operator",
}


def parse_java_map(line: str) -> dict[str, int]:
    """Parse a Java HashMap toString like {java:S3776=132, java:S1192=108, ...}"""
    result = {}
    for match in re.finditer(r"(java:S\d+)=(\d+)", line):
        key, value = match.group(1), int(match.group(2))
        result[key] = value
    return result


def parse_input(text: str) -> tuple[dict, dict, dict, dict]:
    """Parse CountOccurrences output into four dicts: before_classes, after_classes, before_instances, after_instances."""
    lines = text.split("\n")
    before_classes = {}
    after_classes = {}
    before_instances = {}
    after_instances = {}

    i = 0
    while i < len(lines):
        line = lines[i]
        if "Quantidade total before" in line and i + 1 < len(lines):
            before_classes = parse_java_map(lines[i + 1])
            i += 2
        elif "Quantidade total after" in line and i + 1 < len(lines):
            after_classes = parse_java_map(lines[i + 1])
            i += 2
        elif "Quantidade instancias before" in line and i + 1 < len(lines):
            before_instances = parse_java_map(lines[i + 1])
            i += 2
        elif "Quantidade instancias after" in line and i + 1 < len(lines):
            after_instances = parse_java_map(lines[i + 1])
            i += 2
        else:
            i += 1

    return before_classes, after_classes, before_instances, after_instances


def build_rows(
    before_classes: dict,
    after_classes: dict,
    before_instances: dict,
    after_instances: dict,
) -> list[dict]:
    """Build rows with Rule, Description, and the four count columns."""
    all_rules = set(before_classes) | set(after_classes) | set(before_instances) | set(after_instances)
    all_rules = sorted(all_rules)

    rows = []
    for rule in all_rules:
        desc = RULE_DESCRIPTIONS.get(rule, "")
        total = before_instances.get(rule, 0) + after_instances.get(rule, 0)
        rows.append({
            "rule": rule,
            "desc": desc,
            "before_classes": before_classes.get(rule, 0),
            "before_instances": before_instances.get(rule, 0),
            "after_classes": after_classes.get(rule, 0),
            "after_instances": after_instances.get(rule, 0),
            "_sort": total,
        })

    rows.sort(key=lambda r: r["_sort"], reverse=True)
    for r in rows:
        del r["_sort"]
    return rows


def format_table(rows: list[dict]) -> str:
    """Format rows as an aligned text table."""
    if not rows:
        return ""

    col_widths = {
        "rule": max(len("Rule"), max(len(r["rule"]) for r in rows)),
        "desc": max(len("SonarQube Description"), min(55, max(len(r["desc"]) for r in rows) if rows else 0)),
        "before_classes": max(len("Classes"), max(len(str(r["before_classes"])) for r in rows)),
        "before_instances": max(len("Instances"), max(len(str(r["before_instances"])) for r in rows)),
        "after_classes": max(len("Classes"), max(len(str(r["after_classes"])) for r in rows)),
        "after_instances": max(len("Instances"), max(len(str(r["after_instances"])) for r in rows)),
    }
    desc_w = 55  # Cap description width for readability
    rule_w = col_widths["rule"]
    num_w = max(col_widths["before_classes"], col_widths["before_instances"], col_widths["after_classes"], col_widths["after_instances"], 8)

    lines = []
    # Header
    h1 = f"{'Rule':<{rule_w}}  {'SonarQube Description':<{desc_w}}  "
    h1 += f"{'Issues Before Commit':^{num_w * 2 + 1}}  "
    h1 += f"{'Issues After Commit':^{num_w * 2 + 1}}"
    lines.append(h1)
    h2 = f"{'':<{rule_w}}  {'':<{desc_w}}  "
    h2 += f"{'Classes':^{num_w}} {'Instances':^{num_w}}  "
    h2 += f"{'Classes':^{num_w}} {'Instances':^{num_w}}"
    lines.append(h2)
    lines.append("-" * (rule_w + desc_w + 4 * num_w + 10))

    for r in rows:
        desc_short = (r["desc"][: desc_w - 3] + "...") if len(r["desc"]) > desc_w else r["desc"]
        line = f"{r['rule']:<{rule_w}}  {desc_short:<{desc_w}}  "
        line += f"{r['before_classes']:>{num_w}} {r['before_instances']:>{num_w}}  "
        line += f"{r['after_classes']:>{num_w}} {r['after_instances']:>{num_w}}"
        lines.append(line)

    return "\n".join(lines)


def main():
    text = sys.stdin.read()
    before_classes, after_classes, before_instances, after_instances = parse_input(text)
    rows = build_rows(before_classes, after_classes, before_instances, after_instances)

    print()
    print("=" * 120)
    print("RQ2: SonarQube Readability Issues — Before vs After Commit")
    print("=" * 120)
    print()
    print(format_table(rows))
    print()
    print("=" * 120)

    # Save to CSV (same directory as this script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_csv = os.path.join(script_dir, "rq2_readability_issues.csv")
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["rule", "desc", "before_classes", "before_instances", "after_classes", "after_instances"],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved to {output_csv}")


if __name__ == "__main__":
    main()
