---
name: setup-fling
description: Set up a new Fling project in the current directory. Use when the user wants to create a new web app, API, or tool using Fling.
allowed-tools: Bash(mkdir *), Bash(npm *), Read
---

# Setup Fling

If the user wants to build a project with Fling, you'll need an empty directory. Offer to create one, like `~/flings/my-new-fling`, but go with whatever the user wants. Make sure it's empty.

Then, in that directory, initialize the Fling project with:

```bash
npm init --yes && npm i flingit && npm exec -- fling init --force && npm i
```

That installs the `flingit` package and scaffolds a Fling project, which supports React frontend, Hono API backend, database, storage, cron jobs, secrets, Slack&Discord bots.

After init completes, read the `fling` skill (in `.claude/skills/fling/SKILL.md`) for how to build and deploy the app, and build the project for the user. Ask them what they want to build, if they haven't told you already.

## Troubleshooting

If the installation fails, diagnose and try to fix it, but consult with the user.  Potential issues:

- `npm` not installed: Install Node.js 22 or later via NVM: https://github.com/nvm-sh/nvm
- Node.js version too old: Update to Node.js 22 or later via NVM
