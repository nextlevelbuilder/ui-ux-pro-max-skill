# Security Policy

## Supported Versions

Only the latest released version of `ui-ux-pro-max-cli` and the latest `main` branch of this skill receive security fixes.

| Version | Supported |
|---------|-----------|
| Latest release | ✅ |
| Older releases | ❌ |

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Instead, report it privately using [GitHub's private vulnerability reporting](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/security/advisories/new) (Security tab → "Report a vulnerability").

Include as much of the following as possible:

- A description of the vulnerability and its potential impact
- Steps to reproduce (command, prompt, or CLI flags used)
- The version of `ui-ux-pro-max-cli` and the AI assistant/platform involved
- Any relevant logs or output

We aim to acknowledge reports within 5 business days and to provide a fix or mitigation timeline within 14 days for confirmed issues.

## Scope

This project is a design-system generation skill: a Python search/CLI tool and static data (CSV/JSON) consumed by AI coding assistants. In-scope concerns include:

- Arbitrary code execution via the CLI installer or search scripts
- Path traversal or unsafe file writes when running `uipro init` / `uipro uninstall`
- Supply-chain issues in the `ui-ux-pro-max-cli` npm package or its release pipeline

Out of scope: the design output itself (colors, fonts, UI recommendations) is not a security surface.
