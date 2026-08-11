import csv
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from config import TARGET_COMPANIES, PR_DAYS_LOOKBACK, OUTPUT_DIR, OUTPUT_CSV
from github_client import get_org_pr_stats, get_repo_ci_signals
from claude_client import generate_pitch

console = Console()


def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def save_to_csv(records):
    ensure_output_dir()

    fieldnames = [
        "company", "prs_merged_30d", "avg_merge_time_hours",
        "unique_contributors", "top_repos", "top_contributors",
        "ci_signal", "pain_point", "icebreaker", "talking_points",
        "generated_at"
    ]

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    console.print(f"\n[green]CSV saved to {OUTPUT_CSV}[/green]")


def display_record(record):
    table = Table(title=f"\nAviator Intelligence: {record['company']}", show_header=False)
    table.add_column("Field", style="cyan", width=20)
    table.add_column("Value", style="white")

    table.add_row("PRs Merged (30d)", str(record["prs_merged_30d"]))
    table.add_row("Avg Merge Time", f"{record['avg_merge_time_hours']} hours")
    table.add_row("Unique Contributors", str(record["unique_contributors"]))
    table.add_row("Top Repos", record["top_repos"])
    table.add_row("Top Contributors", record["top_contributors"])
    table.add_row("CI Signal", record["ci_signal"])
    table.add_row("", "")
    table.add_row("Pain Point Hypothesis", record["pain_point"])
    table.add_row("", "")

    console.print(table)

    console.print(Panel(
        record["icebreaker"],
        title="Email Icebreaker",
        border_style="green"
    ))

    console.print("\n[bold yellow]Discovery Call Talking Points:[/bold yellow]")
    for point in record.get("talking_points", "").split("•"):
        point = point.strip()
        if point:
            console.print(f"  • {point}")


def main():
    console.print(Panel.fit(
        "[bold blue]Aviator Intelligence Agent[/bold blue]\n"
        "GitHub Signal -> Claude Intelligence -> CRM-Ready Output",
        border_style="blue"
    ))

    all_records = []

    for company in TARGET_COMPANIES:
        name = company["name"]
        org = company["github_org"]

        console.print(f"\n[bold]Processing {name}...[/bold]")

        stats = get_org_pr_stats(org, days_back=PR_DAYS_LOOKBACK)

        if not stats:
            console.print(f"  [red]Failed to fetch data for {name} - skipping[/red]")
            continue

        console.print(
            f"  {stats['total_prs_merged']} merged PRs, "
            f"{stats['avg_merge_time_hours']}h avg merge time, "
            f"{stats['unique_contributors']} contributors"
        )

        top_repo = stats["top_repos"][0] if stats["top_repos"] else ""
        ci_data = (
            get_repo_ci_signals(org, top_repo)
            if top_repo
            else {"ci_signal": "Unknown"}
        )

        console.print("  Generating Claude intelligence...")
        intelligence = generate_pitch(name, stats, ci_data.get("ci_signal", "Unknown"))

        record = {
            "company": name,
            "prs_merged_30d": stats["total_prs_merged"],
            "avg_merge_time_hours": stats["avg_merge_time_hours"],
            "unique_contributors": stats["unique_contributors"],
            "top_repos": ", ".join(stats["top_repos"]),
            "top_contributors": ", ".join(stats["top_contributors"]),
            "ci_signal": ci_data.get("ci_signal", "Unknown"),
            "pain_point": intelligence.get("pain_point_hypothesis", ""),
            "icebreaker": intelligence.get("icebreaker", ""),
            "talking_points": " • ".join(
                intelligence.get("suggested_talking_points", [])
            ),
            "generated_at": datetime.utcnow().isoformat(),
        }

        all_records.append(record)
        display_record(record)
        console.print("\n" + "-" * 60)

    if all_records:
        save_to_csv(all_records)
        console.print(
            f"\n[bold green]Done. Processed {len(all_records)}/{len(TARGET_COMPANIES)} companies.[/bold green]"
        )
    else:
        console.print("[red]No companies processed.[/red]")


if __name__ == "__main__":
    main()