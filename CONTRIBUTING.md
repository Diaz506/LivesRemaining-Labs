# Contributing to Lives Remaining Labs

Thanks for your interest! This is a teaching reference for an end-to-end
**Azure Databricks** data + ML platform built around the fictional **Lives
Remaining Labs** game studio. Here's how you can help:

## 🐛 Found a Bug?

Open an issue describing the problem, which lab it affects, and steps to
reproduce.

## 💡 Suggesting Improvements?

Open an issue with the `enhancement` label. Describe what you'd change and why.

## 🔧 Submitting a PR?

1. Fork the repo
2. Create a feature branch (`git checkout -b fix/lab-2-typo`)
3. Make your changes
4. Ensure the data generator still runs: `python scripts/generate_events.py --count 1000`
5. Submit a PR with a clear description

## 📝 Style Guide

- Lab guides use **second person** ("You will create...") for instructions
- Each lab opens with a short **Mission Briefing** narrative in a blockquote
  (in-world voice — Maya Chen / Dev Rao / the Player Intelligence team)
- Steps are **numbered and concrete**: real commands, exact table names
  (`labs.bronze/silver/gold.*`), and verification SQL
- Code blocks include the language identifier (` ```python `, ` ```sql `, ` ```bash `)
- Every lab ends with a **✅ Done when** checklist and a **🧯 Troubleshooting** table

## 🌟 Code of Conduct

Be kind, constructive, and inclusive. We're all here to learn.
