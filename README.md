\# MergePulse Intelligence Agent



Signal-based enrichment engine that identifies companies with high PR throughput and merge bottlenecks, the exact DevEx pain points Aviator's MergeQueue solves.



\## What it does



1\. Queries GitHub's GraphQL API to pull merged PR stats across an org's top 50 repos in a single call

2\. Extracts signals: PR velocity, average merge time, contributor count, active repos

3\. Feeds those signals to Claude to generate account-specific sales intelligence

4\. Outputs CRM-ready CSV with pain point hypotheses, email icebreakers, and discovery call talking points



\## Setup



pip install -r requirements.txt



Add your API keys to `.env`:

GITHUB\_TOKEN=ghp\_xxx

ANTHROPIC\_API\_KEY=sk-ant-api03-xxx



\## Run

python main.py



Output lands in `output/aviator\_enrichment.csv`





WHY THIS ACTUALLY MATTERS?


Instead of generic outreach, this pipeline finds accounts where the data says they have the problem. 1000+ PRs/month, 25+ hour merge times, 150+ contributors hitting the same repos, those are MergeQueue conversations waiting to happen.

