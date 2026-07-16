# Candidate-Profile-Change-Tracker
A comprehensive web application for comparing two versions of a candidate's resume/profile and identifying meaningful changes. Built with Streamlit, Python, and AI fallback support.
# Candidate Profile Change Tracker

A Streamlit app that compares two versions of a candidate's resume/profile — a "Previous" version and an "Updated" version — and automatically detects and classifies what changed (job title, skills, employer, experience, location, employment dates).

This is the **manual-input version**: instead of uploading resume files, the user fills in both profiles through a form, and the app runs the comparison logic on the structured data.

## Features

- **Manual Input tab** — enter Previous and Updated resume details side by side (job title, skills, employer, experience, location, employment start/end dates); a "Load Example Data" button in the sidebar pre-fills a sample comparison
- **AI-assisted classification (optional)** — toggle "Enable AI Classification" in the sidebar to use Google Gemini for parsing/classifying changes, with a rule-based fallback when AI is off or unavailable; sidebar shows live AI usage stats (success count, token usage, fallback count, success rate)
- **Comparison Results tab** — overall status banner (No Significant Changes / Minor / Moderate / Significant Profile Update), summary stats (total, important, minor, needs-review changes), and a detailed, severity-highlighted changes table
- **Export** — download each comparison as CSV or JSON
- **History tab** — browse all past comparisons stored in the database and drill into any one for full details
- **Analytics tab** — per-candidate timeline chart of changes over time, plus average changes, total comparisons, and latest status

## Tech Stack

- [Streamlit](https://streamlit.io/) — UI
- [pandas](https://pandas.pydata.org/) — tabular data handling/display
- [python-dotenv](https://pypi.org/project/python-dotenv/) — loads `GEMINI_API_KEY` from a `.env` file
- Google Gemini API — optional AI-powered change classification
- Custom backend modules (see below) for persistence and comparison logic

## Project Structure

> Note: only `app.py` is included here — fill in/adjust this section to match your actual repo layout.

```
.
├── app.py                  # Main Streamlit app (this file)
├── backend/
│   ├── database.py         # Database class — stores/retrieves candidates, resumes, comparisons
│   ├── models.py            # Resume, Comparison data models
│   ├── ai_service.py        # AIService — Gemini integration + rule-based fallback
│   └── comparator.py        # Comparator — core profile-diff / comparison logic
├── .env                     # GEMINI_API_KEY (not committed)
└── requirements.txt
```

## Setup

1. Clone the repo
   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Create a `.env` file for AI-assisted classification
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
4. Run the app
   ```bash
   streamlit run app.py
   ```

## Usage

1. Open the **Manual Input** tab and fill in the Previous and Updated resume fields (or click **Load Example Data** in the sidebar for a quick demo).
2. Click **Compare Resumes**.
3. Review the results in the **Comparison Results** tab — overall status, stats, and a detailed changes table — and download as CSV or JSON if needed.
4. Check the **History** tab to revisit past comparisons.
5. Use the **Analytics** tab to see how a specific candidate's profile has evolved over multiple comparisons.
