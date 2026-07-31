# Features

## Private chat

- Scans forwarded messages, pasted URLs (inline or standalone), and uploaded files of any type.
- Reads text out of screenshots via OCR before running it through the same detection pipeline.
- Casual, non-forwarded messages with no link get a gentle nudge to forward the suspicious content instead of being scanned outright.
- Persistent per-user language preference (Khmer/English), with a bilingual fallback when none is set yet.
- A reply-keyboard provides quick access to common help, security, donation, group, and language actions; `/email` is available from Telegram's slash-command menu.

## Email breach checks

- `/email you@example.com` checks the address against known breaches through XposedOrNot.
- Reports breach names, dates, exposed data types, and risky-password warnings, followed by password and 2FA safety advice.
- Works in private and group chats with Khmer, English, or bilingual responses.
- Does not persist the submitted email address in Broryat's database.

## Group chat

- Only messages with a link or a document are inspected; everything else is ignored to keep the group quiet.
- Risky-but-unconfirmed content gets a brief warning reply; when VirusTotal confirms a file or link is malicious, the bot deletes the message instead and posts a short warning.
- Defaults to Khmer, switchable per-group via `/language`.

## Chat Automation

Add Broryat to Telegram Chat Automation to scan files and links received in your private chats:

- Incoming URLs and supported files are checked by VirusTotal; ordinary conversation is ignored.
- Confirmed malicious content shows owner-only **Delete** and **Keep** controls with detection details and a false-positive disclaimer.
- The action notice disappears five seconds after a successful choice.
- Scan records use anonymous user/chat IDs and never store private-chat text.

## Detection pipeline

- AI intent classification (Telegram impersonation, banking scams, fake recruitment, fake government notices, investment/crypto scams, credential theft, malware delivery, urgency tactics), any provider selectable via `AI_PROVIDER`.
- Direct file/URL scans stop waiting for an unavailable AI explanation after 10 seconds and return the localized VirusTotal verdict, detection names, and safety advice instead.
- VirusTotal file-hash and URL lookups with a sliding-window rate limiter tuned to the free tier (4/min, 500/day, 15.5K/month) and a scan-history cache to avoid redundant lookups.
- Strict URL validation rejects incomplete domains, email addresses, bare IPs, and incidental dotted text (log lines, module paths) so only genuine domains get scanned.
- A trusted-domain allowlist (major tech companies, banks, Cambodian government sites) skips scanning a lone trusted link entirely, while still catching look-alike and suffix-attack domains.
- A per-user (private) / per-chat (group) limit of 3 scans per rolling 24 hours protects the shared VirusTotal quota.

## Safety by design

- Photos and videos are never scanned as media directly — only a link in the caption, if present.
- VirusTotal's verdict always wins over the AI's when both are available.
- Every scan — URL, domain, SHA-256, VirusTotal verdict, AI verdict, timestamp, language, category — is persisted for future threat-intelligence use.
