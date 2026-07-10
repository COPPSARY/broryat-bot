# Broryat — Web Development Spec

**Bot:** `@broryat_bot` → `https://t.me/broryat_bot`
**Tagline (KH):** ប្រយ័ត្ន គឺជា AI Bot ដែលជួយការពារអ្នកពីការបោកប្រាស់តាមអ៊ីនធឺណិត។ ផ្ញើ Link, សារ ឬ File ដែលអ្នកសង្ស័យមកកាន់ Bot ដើម្បីវិភាគហានិភ័យ និងទទួលបានការណែនាំភ្លាមៗ។
**Tagline (EN):** *(needs translation — see note in Part 4)*
**Studio / footer links:** https://sayanastudio.tech/ · https://www.instagram.com/sayana.studio
**Logo asset:** `assets/logo.png` (provided)

---

## Part 1 — Tech Stack & Architecture

- **Framework:** Astro
- **Content:** Astro Content Collections, all articles/tutorials authored in Markdown (`.md` / `.mdx` if image-heavy embeds are needed)
- **i18n:** Two locales — `kh` (default) and `en`. Every page and every content entry must exist in both locales.
- **Images:** All article/tutorial frontmatter must support a cover image field, and article body must support inline images via standard Markdown image syntax.
- **Routing pattern:**
  - `/` and `/en/` — landing page
  - `/articles/` and `/en/articles/` — article listing
  - `/articles/[slug]/` and `/en/articles/[slug]/` — article detail
  - `/tutorials/` and `/en/tutorials/` — tutorial listing
  - `/tutorials/[slug]/` and `/en/tutorials/[slug]/` — tutorial detail
- **Language switch** must preserve the current page (e.g. switching on an article detail page goes to that article's translated counterpart, not back to homepage).

### Content Collection Schemas

**`articles` collection** (frontmatter):
```yaml
title: string
description: string        # used for card excerpt + SEO meta
date: date
lang: "kh" | "en"
translationId: string      # shared ID linking a KH entry to its EN counterpart
tag: string                # e.g. "Security Alert", "Guide"
coverImage: string         # path to image
draft: boolean             # optional, default false
```

**`tutorials` collection** (frontmatter):
```yaml
title: string
description: string
lang: "kh" | "en"
translationId: string
coverImage: string
videoUrl: string           # optional, empty/null until recordings exist — placeholder state must be handled in UI
draft: boolean
```

Body content for both collections is Markdown and must render inline images cleanly (figure/caption support is a nice-to-have, not required).

---

## Part 2 — UI Style Requirements (visual system)

**Palette (5 colors max, white-dominant)**
- White `#FFFFFF` — dominant surface
- Black `#111111` — primary text
- Gray `#666666` — secondary text
- Cambodia Blue `#032EA1` — accent (used for the Telegram nav button, links, primary CTAs)
- Cambodia Red `#E00025` — accent, used sparingly (alerts, tags, risk indicators)

**Typography**
- Editorial, high-contrast type — large display headlines, comfortable body line-height
- Must support Khmer script cleanly (choose a typeface pairing that renders Khmer glyphs well, not just Latin)
- One display face for headlines, one body face, optional monospace/utility face for labels/dates

**Surfaces & structure**
- No cards for general content blocks (exception: the 3 article-preview cards on the landing page, and standard blog-card treatment on listing pages — those are allowed to look like cards)
- No drop shadows, no gradients, no glassmorphism, no border-radius (sharp corners) elsewhere
- Sections divided by hairline rules, not background color blocks
- Minimal iconography — typography and spacing carry hierarchy

**Components**
- Buttons: flat fill or flat outline, sharp corners, no shadow
- Primary nav CTA button ("Telegram Bot" → `https://t.me/broryat_bot`) always uses Cambodia Blue fill
- Two-column layout pattern (description left / image right) used for the "Attack Types" and "How It Works" sections — must reflow to stacked single-column on mobile

**Motion**
- Minimal — fade/opacity only, no scroll-jacking or parallax

---

## Part 3 — Landing Page Structure

### 1. Navbar
- Logo (`assets/logo.png`) + wordmark
- Page navigation links (Home, Articles, Tutorials — plus anchors to on-page sections if applicable)
- Language switch (KH / EN)
- Primary CTA button, Cambodia Blue, links to `https://t.me/broryat_bot`

### 2. Hero
- Left-aligned or centered headline + description text (bot tagline)
- Primary CTA to the bot
- No stats in this version of the spec unless you want them re-added — confirm

### 3. Attack Types section
- Explains the categories of scam/attack messages the bot detects (phishing links, malware files, impersonation, etc.)
- Layout: title + description on the left, supporting image on the right, per type
- Confirm: is this one combined section with a list of types, or repeated left/right blocks per type (stacked)?

### 4. How It Works / Usage section
- Same left description / right image pattern
- Covers: forwarding a message to the bot, adding the bot to a group chat
- Includes a video tutorial placeholder (recording pending) — needs a clearly-marked "coming soon" state, not a broken embed

### 5. Latest Articles
- 3-card row pulling the latest entries from the `articles` collection (current locale only)
- Each card: cover image, tag, title, excerpt, date

### 6. CTA banner
- Simple repeat call-to-action linking to the bot

### 7. Footer
- Link to https://sayanastudio.tech/
- Link to https://www.instagram.com/sayana.studio
- (Optional, carried over from earlier spec — confirm if still wanted: Privacy, Contact, GitHub)

---

## Part 4 — Content To Prepare

### Site copy needing EN translation
- Hero tagline (KH provided above; EN version needs writing/confirmation)
- Nav labels, section titles, button labels — standard i18n string table

### Starter Articles (each needs a KH and EN version, both with images)
1. **What is phishing** — explains phishing tactics, how to recognize them
2. **What malware attackers send** — explains malicious file types (APK/EXE/etc.) commonly forwarded on Telegram, what they do
3. **How to enable Telegram two-step/password protection** — step-by-step account security guide

### Tutorials (video placeholder state, to be recorded later)
- Forwarding a suspicious message to the bot
- Adding the bot to a group chat
- *(confirm if the two "usage" tutorials above are their own tutorial-collection entries, or just embedded in the landing page How It Works section — recommend: landing page shows a summary, full tutorial page has the depth + eventual video)*

---

## Open questions before build
1. Hero: keep it text-only, or reintroduce the stats row from the earlier draft?
2. Attack Types: how many categories, and do you have names/copy for each yet, or should placeholders be scaffolded?
3. Footer: confirm final link list (studio + Instagram only, or also Privacy/Contact/GitHub as previously discussed)?
4. Tutorials: standalone collection page as scaffolded above, or merged into Articles with a `type` field instead of a separate collection?