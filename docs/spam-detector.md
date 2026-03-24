# Email Spam Detection (Python + OpenAI)

Detect whether an email is **spam** or **ham** by sending the email **content** to an OpenAI model for classification. The script returns structured JSON: label, confidence, reasons, risk flags, and a safe summary.

## Features

- Classifies email content as `spam` or `ham`
- Returns:
  - `label`: "spam" / "ham"
  - `confidence`: 0.0–1.0
  - `reasons`: up to 5 short reasons
  - `risk_flags`: tags like `credential_theft`, `urgent_payment`, etc.
  - `safe_summary`: neutral 1–2 sentence summary
- Uses strict JSON Schema output for reliable parsing
- CLI-friendly (run from terminal)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install openai python-dotenv
```

Create `.env`:

```dotenv
OPENAI_API_KEY=your_key_here
```

## Usage

```bash
python spam_detector.py --text "URGENT: Your account will be closed. Click here to verify your password..."
```