"""Load the service's key=value logs into SQLite so failures can be investigated with SQL.

Usage: python -m tools.log_to_sqlite logs/sample.log logs.db
"""
import argparse
import re
import sqlite3

LINE = re.compile(r"^(?P<ts>\S+ \S+) (?P<level>[A-Z]+) (?P<body>.*)$")
FIELD = re.compile(r"(\w+)=(\S+)")

SCHEMA = """
CREATE TABLE events (
    line_no INTEGER PRIMARY KEY,
    ts      TEXT,
    level   TEXT,
    event   TEXT,
    user    TEXT,
    session TEXT,
    status  INTEGER,
    path    TEXT
)
"""


def parse_line(line_no, line):
    match = LINE.match(line.strip())
    if not match:
        return None
    fields = dict(FIELD.findall(match["body"]))
    return (
        line_no,
        match["ts"],
        match["level"],
        fields.get("event"),
        fields.get("user"),
        fields.get("session"),
        int(fields["status"]) if fields.get("status", "").isdigit() else None,
        fields.get("path"),
    )


def load(log_path, db_path):
    """Rebuild the events table from a log file. Returns the number of rows loaded."""
    with open(log_path, encoding="utf-8") as handle:
        rows = [row for n, line in enumerate(handle, start=1) if (row := parse_line(n, line))]
    with sqlite3.connect(db_path) as conn:
        conn.execute("DROP TABLE IF EXISTS events")
        conn.execute(SCHEMA)
        conn.executemany("INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows)
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log_path")
    parser.add_argument("db_path")
    args = parser.parse_args()
    print(f"Loaded {load(args.log_path, args.db_path)} events into {args.db_path}")


if __name__ == "__main__":
    main()
