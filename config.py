# config.py
"""
Configuration for the Aviator Intelligence Agent.
Target companies and settings live here so nothing is hardcoded in the main logic.
"""

# Companies researching.
#  Format is  { "name": "CompanyName", "github_org": "their-github-org-name" }
TARGET_COMPANIES = [
    {"name": "Vercel", "github_org": "vercel"},
    {"name": "Supabase", "github_org": "supabase"},
    {"name": "Linear", "github_org": "linear"},
    {"name": "PlanetScale", "github_org": "planetscale"},
    {"name": "HashiCorp", "github_org": "hashicorp"},
]

# Git parameters 
PR_DAYS_LOOKBACK = 30  # How many days back to analyze PRs

# cld model
CLAUDE_MODEL = "claude-sonnet-4-20250514"  # Latest Sonnet

# Output settings
OUTPUT_DIR = "output"
OUTPUT_CSV = f"{OUTPUT_DIR}/aviator_enrichment.csv"