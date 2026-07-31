# Security Policy

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Instead, report it privately via
[GitHub Security Advisories](https://github.com/COPPSARY/broryat-bot/security/advisories/new)
for this repository. This lets us assess and fix the issue before it's
publicly disclosed.

Include as much of the following as you can:

- A description of the vulnerability and its potential impact.
- Steps to reproduce, or a proof of concept.
- The affected file(s) or component(s), if known.
- Any suggested remediation.

We'll acknowledge your report as soon as possible and keep you updated as we
work on a fix. Please give us a reasonable amount of time to address the
issue before any public disclosure.

## Scope

This project handles security-sensitive data by design — it downloads and
hashes user-submitted files (including potential malware) and processes
VirusTotal/AI provider API keys, bot tokens, and a Postgres connection
string. Reports of particular interest include:

- Anything that lets a Telegram user trigger unsafe handling of a submitted
  file (e.g. path traversal from a filename, unsanitized file writes, SSRF
  via URL scanning).
- Leakage of secrets (`.env` values, API keys, tokens) through logs, error
  messages, or responses.
- Bypasses of the VirusTotal rate limiter that could exhaust the shared free
  quota.
- Injection issues in database queries or in messages sent back to Telegram.

## Supported Versions

This project does not yet maintain multiple release branches — security
fixes are applied to `main` only. Run the latest commit to stay current.

## Non-Security Bugs

For bugs that aren't security-sensitive, please use the normal
[issue tracker](https://github.com/COPPSARY/broryat-bot/issues) instead — see
[CONTRIBUTING.md](CONTRIBUTING.md).
