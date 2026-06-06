"""
Pretty-print all tables in dev.db using Rich.
Usage:  python view_db.py [table_name] [--limit N]
        python view_db.py              -> shows all tables
        python view_db.py alerts       -> shows only alerts
        python view_db.py readings --limit 20
"""

import sqlite3
import sys
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.text import Text

DB_PATH = "dev.db"

SEVERITY_COLORS = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}
STATUS_COLORS   = {"OPEN": "red", "RESOLVED": "green", "ACKNOWLEDGED": "yellow"}
METER_STATUS    = {"active": "green", "inactive": "dim"}

console = Console()


def col_style(table_name: str, col: str, value: str) -> str:
    if value is None:
        return "dim"
    if table_name == "alerts":
        if col == "severity":
            return SEVERITY_COLORS.get(str(value), "")
        if col == "status":
            return STATUS_COLORS.get(str(value), "")
    if table_name == "smart_meters" and col == "status":
        return METER_STATUS.get(str(value), "")
    return ""


def fmt(value, col: str = "") -> str:
    if value is None:
        return "[dim]NULL[/dim]"
    if col in ("energy_consumed_kwh",):
        return f"{float(value):.4f} kWh"
    if col == "voltage":
        return f"{float(value):.1f} V"
    if col == "current":
        return f"{float(value):.3f} A"
    if col == "power_factor":
        return f"{float(value):.3f}"
    return str(value)


def show_table(conn: sqlite3.Connection, table_name: str, limit: int) -> None:
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    total = cur.fetchone()[0]

    cur.execute(f"SELECT * FROM {table_name} ORDER BY rowid DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    if not rows:
        console.print(f"[dim]{table_name}[/dim] — [yellow]empty[/yellow]\n")
        return

    cols = rows[0].keys()

    rich_table = Table(
        title=f"[bold cyan]{table_name}[/bold cyan]  "
              f"[dim](showing {len(rows)} of {total} rows, newest first)[/dim]",
        box=box.ROUNDED,
        header_style="bold white on dark_blue",
        show_lines=True,
        expand=False,
    )

    for col in cols:
        rich_table.add_column(col, overflow="fold", no_wrap=False)

    for row in rows:
        cells = []
        for col in cols:
            raw = row[col]
            style = col_style(table_name, col, raw)
            text = fmt(raw, col)
            if style:
                cells.append(f"[{style}]{text}[/{style}]")
            else:
                cells.append(text)
        rich_table.add_row(*cells)

    console.print(rich_table)
    console.print()


def summary(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]

    lines = []
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        lines.append(f"  [cyan]{t:<18}[/cyan] {cur.fetchone()[0]:>5} rows")

    console.print(Panel("\n".join(lines), title="[bold]Database Summary[/bold]", expand=False))
    console.print()


def main() -> None:
    args = sys.argv[1:]
    limit = 50
    filter_table = None

    if "--limit" in args:
        idx = args.index("--limit")
        limit = int(args[idx + 1])
        args = [a for i, a in enumerate(args) if i not in (idx, idx + 1)]

    if args:
        filter_table = args[0].lower()

    TABLE_ORDER = ["households", "smart_meters", "meter_readings", "alerts", "tariff_config"]

    with sqlite3.connect(DB_PATH) as conn:
        summary(conn)
        for t in TABLE_ORDER:
            if filter_table and t != filter_table:
                continue
            show_table(conn, t, limit)


if __name__ == "__main__":
    main()
