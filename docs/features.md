# Features

## Private chat

- Scans forwarded messages, pasted URLs (inline or standalone), and uploaded files of any type.
- Reads text out of screenshots via OCR before running it through the same detection pipeline.
- Casual, non-forwarded messages with no link get a gentle nudge to forward the suspicious content instead of being scanned outright.
- Persistent per-user language preference (Khmer/English), with a bilingual fallback when none is set yet.
- A reply-keyboard menu mirrors the slash commands (`/help`, `/use`, `/secure`, `/password`, `/addgroup`, `/donate`, `/language`).

## Group chat

- Only messages with a link or a document are inspected; everything else is ignored to keep the group quiet.
- Risky-but-unconfirmed content gets a brief warning reply; when VirusTotal confirms a file or link is malicious, the bot deletes the message instead and posts a short warning.
- Defaults to Khmer, switchable per-group via `/language`.

## Telegram Business secretary

- Scans URLs and files received through a connected Telegram Business account; ordinary chat text is ignored.
- Uses VirusTotal directly for Business file/URL verdicts and skips the unused AI explanation call, reducing latency and AI credit use without changing risk decisions.
- Skips a message containing only one well-known trusted URL, using the same trusted-domain policy as private and group scanning; trusted links mixed with other text are still inspected.
- Leaves clean content unchanged and posts no scanning message. For VirusTotal-confirmed malicious content, asks the connected account owner to delete or keep the original message and includes VirusTotal detection details plus a false-positive disclaimer.
- Verifies the person pressing Delete or Keep against the live Telegram Business connection; the other chat participant cannot act.
- Removes the completed action notice after five seconds. Failed actions remain visible so the owner can read the error.
- Uses the business owner's saved bot language, defaulting to Khmer.
- Stores threat indicators with anonymous user/chat IDs, never stores Business chat text, and removes temporary file downloads after scanning.

## Detection pipeline

- AI intent classification (Telegram impersonation, banking scams, fake recruitment, fake government notices, investment/crypto scams, credential theft, malware delivery, urgency tactics), any provider selectable via `AI_PROVIDER`.
- VirusTotal file-hash and URL lookups with a sliding-window rate limiter tuned to the free tier (4/min, 500/day, 15.5K/month) and a scan-history cache to avoid redundant lookups.
- Strict URL validation rejects incomplete domains, email addresses, bare IPs, and incidental dotted text (log lines, module paths) so only genuine domains get scanned.
- A trusted-domain allowlist (major tech companies, banks, Cambodian government sites) skips scanning a lone trusted link entirely, while still catching look-alike and suffix-attack domains.
- A per-user (private) / per-chat (group) limit of 2 scans per rolling 24 hours protects the shared VirusTotal quota.

## Safety by design

- Photos and videos are never scanned as media directly — only a link in the caption, if present.
- VirusTotal's verdict always wins over the AI's when both are available.
- Every scan — URL, domain, SHA-256, VirusTotal verdict, AI verdict, timestamp, language, category — is persisted for future threat-intelligence use.
