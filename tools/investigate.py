"""Run every query in tools/queries.sql against a loaded log database and print the results.

Usage: python -m tools.investigate logs.db
"""
import argparse
import sqlite3
from pathlib import Path

QUERIES_FILE = Path(__file__).with_name("queries.sql")


def load_queries(path=QUERIES_FILE):
    """Split queries.sql into {name: sql} using '-- name:' markers."""
    queries, name, lines = {}, None, []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("-- name:"):
            if name:
                queries[name] = "\n".join(lines).strip()
            name, lines = line.split(":", 1)[1].strip(), []
        elif not line.startswith("--"):
            lines.append(line)
    if name:
        queries[name] = "\n".join(lines).strip()
    return queries


def run(db_path):
    with sqlite3.connect(db_path) as conn:
        return {name: conn.execute(sql).fetchall() for name, sql in load_queries().items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("db_path")
    args = parser.parse_args()
    for name, rows in run(args.db_path).items():
        print(f"\n== {name} ({len(rows)} rows)")
        for row in rows:
            print("  ", row)


if __name__ == "__main__":
    main()
