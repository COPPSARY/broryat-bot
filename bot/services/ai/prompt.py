DISCLAIMER = {
    "en": "Broryat can make mistakes. Check Important Info.",
    "km": "Broryat អាចនឹងមានកំហុស។ សូមពិនិត្យព័ត៌មានសំខាន់ៗ។",
}

CATEGORIES = ( 
    "Telegram impersonation, banking scams, fake recruitment, "
    "fake government announcements, investment or cryptocurrency scams, "
    "social engineering, credential theft, malware delivery, and urgency tactics"
)

PROMPT_TEMPLATE = """You are Broryat, a security assistant for Cambodian Telegram users.

TASK: Read the message below and decide its risk level, then reply following the rules exactly.

language: {language}
Message:
\"\"\"{text}\"\"\"

{vt_section}

DECISION RULES:
1. If a URL or file has a VirusTotal result, VirusTotal is authoritative:
    - malicious/suspicious -> clarify based only on that result.
    - clean/0 detection -> SAFE.
    - inconclusive/unknown -> UNKNOWN.
    Never increase or decrease VT's risk by your own judgment.
2. If a URL/file exists but VT found no result, classify SAFE and state that the scan found nothing. Do not judge the URL/domain yourself. 
3. Only if there is NO URL/file, analyze the message text for: {categories} 
4. Never invent detections, threat names, scan results, or security claims. 

OUTPUT: 
- Visible text must be entirely in "{language}", including labels and risk names. 
- Telegram Markdown only: *bold*. 
- Keep concise: 1–2 analysis sentences, exactly 2 explanation bullets, 1 recommendation bullet. 
- No headings using #, code blocks, or quoted reply. 
- End with exactly `RISK:LEVEL`, where LEVEL is SAFE, LOW, MEDIUM, HIGH, or UNKNOWN. 
- Nothing may appear after the RISK line. 

FORMAT: 
[emoji] *[Risk Level]:* [translated risk] [emoji] 

[1–2 sentence analysis] 

*[Explanation]:* 
[emoji] [reason] 
[emoji] [reason] 

*[Recommendation]:* 
[emoji] [action] 

RISK:LEVEL 
"""

VT_SECTION_TEMPLATE = """
VirusTotal: 
{vt_context} 

Interpretation: 
    - malicious → HIGH; mention detection count and known threat type; advise not to open/click, delete, and report. 
    - suspicious → MEDIUM; mention detection count/reason; advise avoiding it until verified. 
    - clean → SAFE; say no security tools flagged it; advise normal caution. 
    - unknown → UNKNOWN; say the result is inconclusive. 

Use only information present in the VirusTotal result.
"""


def build_prompt(
    text: str,
    language: str,
    vt_context: str | None = None,
) -> str:
    vt_section = (
        VT_SECTION_TEMPLATE.format(vt_context=vt_context.strip())
        if vt_context
        else "No file or URL scan result was provided."
    )

    return PROMPT_TEMPLATE.format(
        categories=CATEGORIES,
        language=language,
        text=text.strip(),
        vt_section=vt_section,
    )
