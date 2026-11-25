> **AI-Powered Personal Finance Tracker**

---

## 📌 About Finova
**Finova** is an intelligent, beginner-friendly personal finance tracking web application built using Python and Streamlit. It leverages Machine Learning (Scikit-Learn) for automatic expense categorization, spending prediction, and anomaly detection, alongside Google Gemini AI for natural-language Q&A and financial recommendations.

---

## 🛠️ Tech Stack
- **Frontend & Dashboard UI:** Python, Streamlit (Custom Fintech CSS Theme)
- **Data Wrangling & Validation:** Pandas
- **Machine Learning (ML):** Scikit-learn (TF-IDF + Logistic Regression, Linear Regression, IsolationForest)
- **Visual Analytics & Data Charts:** Plotly Express
- **Generative AI Assistant:** Google Gemini API (`google-generativeai`)
- **Database Storage:** Google Sheets API (`gspread`) with seamless **Automatic Local CSV Fallback**

---

## 🔄 7-Step System Workflow
1. **Data Input:** User logs income/expenses through Streamlit forms or plain-language AI prompts.
2. **Data Cleaning:** Pandas cleans text, validates types, formats dates, and filters anomalies.
3. **ML Categorization:** Scikit-Learn TF-IDF model auto-predicts category from transaction descriptions.
4. **Analytics:** Computes income vs. expenses, net balance, category totals, and budget progress.
5. **Gemini AI Insight:** Contextual financial summaries are sent to Gemini to answer natural language questions.
6. **Dashboard UI:** Displays interactive Plotly charts, summary KPI cards, and alerts.
7. **Secure Storage:** Records are saved to Google Sheets (or fallback CSV files in `data/`).

---

## 📁 Directory Structure
```
finova/
├── .streamlit/
│   └── config.toml          # Custom theme configuration
├── app.py                   # Main entry point & page navigation
├── modules/
│   ├── auth.py              # Login & Register UI with bcrypt validation
│   ├── dashboard.py         # Summary KPI cards & Plotly charts
│   ├── transactions.py      # Add (ML Auto-cat), search, filter, edit, delete & export CSV
│   ├── budget.py            # Category limit progress bars & 80%/100% warning alerts
│   ├── assistant.py         # Gemini AI Q&A chat & plain language transaction logger
│   ├── insights.py          # ML spending prediction, IsolationForest & Gemini savings tips
│   └── profile.py           # User profile info, password change & "Load Demo Data" button
├── utils/
│   ├── db.py                # Google Sheets & Local CSV fallback database engine
│   ├── ml.py                # Scikit-Learn classification, regression & anomaly models
│   ├── gemini.py            # Google Gemini AI wrapper & rule-based fallback
│   └── styles.py            # Custom CSS styles (gradients, KPI cards, badges, footer)
├── data/
│   └── sample_descriptions.csv # ML training data for auto-categorization
├── tests/
│   └── test_finova.py       # Pytest unit tests
├── requirements.txt         # Dependencies list
├── .env.example             # Environment template
└── README.md                # Documentation & setup guide
```

---

## 🚀 Quick Setup & Local Installation

### 1. Clone or Copy the Repository
```bash
cd finova
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your **Google Gemini API Key** in `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Run the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## ☁️ Streamlit Cloud Deployment Steps
1. Push the repository to GitHub.
2. Log into [Streamlit Community Cloud](https://streamlit.io/cloud).
3. Click **"New App"** and select your `finova` repository and `app.py` as the main file.
4. Go to **Advanced Settings -> Secrets** and paste your secrets:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key_here"
   GOOGLE_SHEET_NAME = "Finova_Database"
   ```
5. Click **Deploy!**

---



## 🔐 Google Authentication Setup
Finova supports both email/password authentication and Google sign-in through Streamlit's built-in OpenID Connect support.

1. Open Google Cloud Console and create/select a project.
2. Configure the OAuth consent screen.
3. Create an OAuth Client ID of type **Web application**.
4. Add `http://localhost:8501/oauth2callback` as an authorized redirect URI.
5. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
6. Add your Google OAuth Client ID, Client Secret, and a long random `cookie_secret`.
7. Restart the app with `streamlit run app.py`.

For deployment, add the same values in the hosting platform's Streamlit secrets configuration and use the deployed app's OAuth callback URL. Never commit `secrets.toml`, `.env`, or OAuth credentials to GitHub.

## 🧪 Running Unit Tests
To run unit tests:
```bash
pytest tests/
```
