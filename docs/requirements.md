# Product Requirements Document (PRD)

# Broryat AI

**Version:** 1.0 (Draft)  
**Status:** Planning

## 1. Executive Summary

Broryat AI is an AI-powered cybersecurity platform beginning as a Telegram bot and expanding into a national community-driven threat intelligence platform.

The Telegram bot protects users by analyzing forwarded messages, uploaded files, pasted URLs, and plain text in Khmer and English. It combines AI-based social engineering detection with VirusTotal API v3 malware intelligence.

Long term, the platform will protect Telegram groups, identify phishing campaigns targeting Cambodia, build a local threat intelligence database, and assist administrators with phishing website takedowns.

## 2. Problem Statement

Telegram is widely used in Cambodia and increasingly abused for phishing, fake job recruitment, fake Telegram verification, banking scams, malware delivery, investment scams, and impersonation attacks. Many users, especially elderly and non-technical users, cannot distinguish legitimate messages from scams.

## 3. Goals

- Protect Cambodian Telegram users.
- Detect phishing, malware, impersonation and scams.
- Explain risks in simple Khmer and English.
- Build Cambodia-focused threat intelligence.
- Help identify and disrupt phishing campaigns.

## 4. Target Users

- Everyday Cambodian users
- Elderly / non-technical users
- Businesses
- NGOs
- Schools
- Universities
- Government agencies

## 5. Supported Inputs

- Forwarded Telegram messages
- Uploaded files
- Pasted URLs
- Plain text

## 6. Core Features

### AI Intent Detection

Detect:

- Telegram impersonation
- Banking scams
- Fake HR recruitment
- Fake government announcements
- Fake investment opportunities
- Cryptocurrency scams
- Social engineering
- Credential theft
- Malware delivery
- Urgency tactics

Outputs:

- Risk level
- Confidence score
- Explanation
- Recommended action

### VirusTotal Integration

Use VirusTotal API v3.

Functions:

- Upload file
- Get file report
- Scan URL
- Get URL report

VirusTotal verdict always takes priority when available.

### File Analysis

Support common formats including:

- EXE
- DLL
- ZIP
- RAR
- 7Z
- PDF
- DOCX
- XLSX
- APK
- JS
- BAT
- VBS

Calculate SHA-256 before submission.

### URL Analysis

- Extract URLs
- Normalize URLs
- Scan using VirusTotal
- Store results
- Explain findings

### Response Example

```
🛡 Risk: HIGH

AI Analysis
• Telegram impersonation
• Creates urgency

VirusTotal
• Detected by 12 vendors

Recommendation
• Do not click the link.
• Delete the message.
• Report the sender.
```

## 7. Telegram Group Protection

The bot can be added to Telegram groups.

Capabilities:

- Scan every posted URL
- Scan uploaded files
- Detect phishing messages
- Warn members
- Delete malicious messages (optional)
- Delete malicious files (optional)
- Notify admins
- Log incidents

Configurable modes:

- Warn only
- Delete malicious content
- Strict mode
- Normal mode

### Compromised Account Detection

Detect unusual behavior such as:

- Trusted user suddenly posting malware
- Multiple phishing links
- Same scam repeatedly posted
- Rapid suspicious activity

Notify admins with a confidence score.

## 8. Threat Intelligence

Every scan stores:

- URL
- Domain
- SHA-256
- File name
- VirusTotal verdict
- AI verdict
- Timestamp
- Language
- Category

Database: Supabase

## 9. Campaign Detection

Detect repeated attacks across users and groups.

Track:

- First seen in Cambodia
- Last seen
- Number of reports
- Groups affected
- Users affected
- Scam category

## 10. Reporting Workflow

Potential phishing enters a review queue.

Administrator may approve reporting to:

- Hosting providers
- Registrars
- Cloudflare abuse
- Google Safe Browsing
- Microsoft Defender
- PhishTank
- URLhaus
- OpenPhish

Reports are not automatically submitted by default.

## 11. Website (Phase 2)

Public:

- Scan URL
- Upload File
- Search Hash
- Learn about scams
- Latest threats

Dashboard:

- Incoming scans
- Review queue
- Campaigns
- Analytics
- Threat intelligence
- Reporting status

## 12. Architecture

```
Telegram User / Group
│
Telegram Bot
│
AI Intent Detection
│
VirusTotal API v3
│
Risk Engine
│
Supabase
│
Threat Intelligence
│
Admin Dashboard
```

## 13. Roadmap

### Phase 1

Telegram Bot MVP

- AI detection
- VirusTotal integration
- File scanning
- URL scanning
- Khmer & English

### Phase 2

Group Protection

- Real-time scanning
- Automatic warnings
- Moderation
- Admin controls

### Phase 3

Threat Intelligence Platform

- Campaign detection
- Analytics
- Dashboard
- Shared intelligence

### Phase 4

Takedown Platform

- Review queue
- Report generation
- Provider integrations
- Public API

## Vision

Build Cambodia's leading AI-powered community cybersecurity platform that protects individuals, groups, businesses, schools, NGOs, and government agencies from phishing, malware, and social engineering while creating the country's first collaborative threat intelligence network.
