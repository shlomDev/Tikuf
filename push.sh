#!/bin/sh
# needs GitHub CLI logged in: gh auth login
gh repo create shlomDev/gap-counter --private --source . --remote origin --push
