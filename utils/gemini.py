import os
import json
import re
import datetime
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_gemini_api_key():
    """Retrieves GEMINI_API_KEY from environment variables or st.secrets."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        try:
            if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            key = None
    return key

def ask_gemini_financial_question(summary_context: str, question: str) -> str:
    """
    Answers natural-language financial questions using Google Gemini AI with fallback.
    """
    api_key = get_gemini_api_key()
    
    if not api_key:
        return _fallback_financial_answer(question, summary_context)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        You are Finova AI, an expert personal financial assistant.
        Analyze the following user's financial summary and answer their question clearly, concisely, and helpfully.
        
        USER FINANCIAL SUMMARY:
        {summary_context}
        
        USER QUESTION:
        {question}
        
        Instructions:
        - Provide numbers, percentages, and insights based directly on their summary when applicable.
        - Keep the answer under 4 paragraphs.
        - Be encouraging, realistic, and practical.
        """
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
        return _fallback_financial_answer(question, summary_context)
    except Exception as e:
        return _fallback_financial_answer(question, summary_context)

def parse_plain_language_transaction(prompt_text: str) -> dict:
    """
    Uses Gemini AI (with regex fallback) to extract transaction JSON from natural language prompt.
    Returns dict with keys: amount, type, category, date, description.
    """
    api_key = get_gemini_api_key()
    today_str = datetime.date.today().strftime("%Y-%m-%d")

    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            system_instruction = f"""
            Extract transaction details from the given text into strict JSON with no markdown syntax wrapping.
            Today's date is {today_str}.
            JSON schema:
            {{
                "amount": float,
                "type": "Expense" or "Income",
                "category": "Food" | "Travel" | "Bills" | "Shopping" | "Health" | "Education" | "Entertainment" | "Salary" | "Other",
                "date": "YYYY-MM-DD",
                "description": string
            }}
            Text: "{prompt_text}"
            """
            response = model.generate_content(system_instruction)
            if response and response.text:
                clean_text = response.text.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean_text)
                if "amount" in parsed:
                    parsed["amount"] = float(parsed.get("amount", 0.0))
                    if "type" not in parsed or parsed["type"] not in ["Income", "Expense"]:
                        parsed["type"] = "Expense"
                    if "date" not in parsed or not parsed["date"]:
                        parsed["date"] = today_str
                    if "category" not in parsed:
                        parsed["category"] = "Other"
                    if "description" not in parsed:
                        parsed["description"] = prompt_text
                    return parsed
        except Exception:
            pass

    # Regex Rule-Based Fallback parser
    return _rule_based_transaction_parser(prompt_text, today_str)

def generate_saving_tips(summary_context: str) -> list:
    """
    Generates 3 smart saving recommendations / tips using Gemini AI or fallback.
    """
    api_key = get_gemini_api_key()
    
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            prompt = f"""
            Based on the user's financial summary below, generate 3 specific, actionable saving recommendations.
            Format output as a JSON list of 3 strings.
            
            FINANCIAL SUMMARY:
            {summary_context}
            """
            response = model.generate_content(prompt)
            if response and response.text:
                clean_text = response.text.replace("```json", "").replace("```", "").strip()
                tips = json.loads(clean_text)
                if isinstance(tips, list) and len(tips) > 0:
                    return tips[:3]
        except Exception:
            pass

    # Smart Rule-Based Fallback Tips
    return [
        "Track food and dining out expenses carefully: Preparing meals at home 3 days a week can save up to 25% of monthly discretionary spend.",
        "Review recurring subscriptions: Cancel unused entertainment or streaming services to reduce monthly fixed bills.",
        "Follow the 50/30/20 budget rule: Allocate 50% of income to needs, 30% to wants, and reserve at least 20% directly into high-yield savings or investments."
    ]

def _fallback_financial_answer(question: str, summary_context: str) -> str:
    """Rule-based fallback when Gemini API is unavailable."""
    q_lower = question.lower()
    
    if "food" in q_lower:
        return f"Based on your transaction records:\nFood expenses are tracked under the 'Food' category. (Note: For detailed AI answers, configure GEMINI_API_KEY in your .env file).\n\nContext Summary:\n{summary_context}"
    elif "spend" in q_lower or "expense" in q_lower:
        return f"Here is your current financial summary:\n{summary_context}\n\nTip: You can filter transactions by date range or category in the Transactions page to analyze specific periods."
    elif "save" in q_lower or "saving" in q_lower or "budget" in q_lower:
        return f"To improve savings, aim to keep total monthly expenses below 70% of total income. Review your Budget page to monitor progress bar limits."
    else:
        return f"Here is a summary of your financial data:\n{summary_context}\n\n(Finova AI System Response)"

def _rule_based_transaction_parser(prompt_text: str, today_str: str) -> dict:
    """Parses plain text prompts using regex for offline fallback."""
    text = prompt_text.lower()
    
    # Extract amount
    amounts = re.findall(r'(\d+(?:\.\d{1,2})?)', text)
    amount = float(amounts[0]) if amounts else 100.0

    # Extract type
    txn_type = "Expense"
    if any(w in text for w in ["salary", "earned", "received", "income", "freelance", "credit", "got"]):
        txn_type = "Income"

    # Extract category
    category = "Other"
    if any(w in text for w in ["food", "lunch", "dinner", "breakfast", "swiggy", "zomato", "coffee", "starbucks", "pizza", "grocery"]):
        category = "Food"
    elif any(w in text for w in ["uber", "ola", "cab", "petrol", "fuel", "flight", "bus", "train", "travel", "auto"]):
        category = "Travel"
    elif any(w in text for w in ["rent", "bill", "electricity", "wifi", "internet", "water", "recharge", "gas"]):
        category = "Bills"
    elif any(w in text for w in ["amazon", "flipkart", "clothes", "shoes", "shopping", "myntra"]):
        category = "Shopping"
    elif any(w in text for w in ["medicine", "doctor", "hospital", "health", "pharmacy"]):
        category = "Health"
    elif any(w in text for w in ["book", "course", "udemy", "tuition", "fee", "school", "college"]):
        category = "Education"
    elif any(w in text for w in ["movie", "netflix", "spotify", "ticket", "game", "pvr"]):
        category = "Entertainment"
    elif any(w in text for w in ["salary", "stipend"]):
        category = "Salary"

    # Extract date offset
    date_val = today_str
    if "yesterday" in text:
        date_val = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    return {
        "amount": amount,
        "type": txn_type,
        "category": category,
        "date": date_val,
        "description": prompt_text.strip()
    }
