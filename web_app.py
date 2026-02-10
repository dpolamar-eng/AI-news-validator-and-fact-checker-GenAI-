import streamlit as st
import pickle
import re
import os
import wikipedia
import google.generativeai as genai
from duckduckgo_search import DDGS
from datetime import datetime

# --- CONFIGURATION ---
# Setup Gemini API
# Get your FREE key at https://aistudio.google.com/
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY_HERE"
genai.configure(api_key=GOOGLE_API_KEY)

# Use the verified Lite model for best free-tier performance
MODEL_NAME = 'gemini-2.0-flash-lite'

# Set page config
st.set_page_config(page_title="AI News Validator & Fact Checker", page_icon="🧠", layout="centered")

# Paths
MODEL_PATH = "fake_news_model.pkl"

@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH): return None
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        return model
    except: return None

model = load_model()

# Title
st.title("🧠 AI News Validator & Fact Checker")
st.markdown("""
This tool uses **Google Gemini Pro (LLM)** + **Live Web Search** to act as a human-like fact checker.
1. 🌐 **Searches** the web for context.
2. 🤖 **Reasons** about the claim (Nuance, Satire, Logic).
3. ✅ **Verifies** complex facts (e.g. "Chess is Olympic?").
""")

# User Input
news_text = st.text_area("Enter News Headline / Claim:", height=100, 
                        placeholder="e.g. 'Chess is an Olympic game' or 'Narendra Modi is President'")

# --- AI AGENT LOGIC ---
import time

def analyze_with_gemini(claim, facts_list):
    """
    Sends the Claim + Gathered Facts to Gemini for a Verdict.
    Includes Auto-Retry for Rate Limits.
    """
    # Use the CONFIRMED Lite model
    model = genai.GenerativeModel(MODEL_NAME)
    today = datetime.now().strftime("%B %d, %Y")
    
    context_text = "\n".join([f"- {f['title']}: {f['body']}" for f in facts_list])
    
    prompt = f"""
    You are a SKEPTICAL Fact Checker. Your job is to catch rumors, half-truths, and common misconceptions.
    TODAY'S DATE: {today}

    CLAIM: "{claim}"
    
    SEARCH RESULTS:
    {context_text}
    
    CRITICAL RULES:
    1. RECENCY GUARD: If the claim is about "Breaking News", but search results are older than 48 hours, mark as FALSE.
    2. LOCATION GUARD: The city/place must match perfectly. Do NOT validate if the city is different.
    3. ENTITY STITCHING: Do NOT validate a claim by combining pieces from different results (e.g., if Source A mentions "Hyderabad" and Source B mentions "Crash in Chandigarh", the verdict for "Hyderabad Crash" is FALSE).
    4. MOCK DRILLS: Must match context and date perfectly to be TRUE.
    5. NO EVIDENCE: If no single result confirms ALL parts of the claim, mark it FALSE.
    
    TASK:
    Based strictly on the text above, determine the verdict.
    
    OUTPUT FORMAT:
    Verdict: [TRUE / FALSE / MISLEADING]
    Category: [NEWS / FACTUAL]
    Reason: [Explanation]
    """

    # Retry Logic (3 Attempts)
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            return response.text, "🟢 Google Gemini 2.0 Flash (Advanced AI)"
        except Exception as e:
            if "429" in str(e):
                time.sleep(2)
                continue
    
    # FALLBACK: If Gemini is busy, use Local Logic with WARNING
    return local_fallback_analysis(claim, facts_list), "⚠️ Local Rule-Based Logic (Basic Fallback)"

def local_fallback_analysis(claim, facts_list):
    """
    Classic Keyword & Negation Logic (Backup Brain).
    """
    # ... logic stays same ...
    # Return string only, caller handles source label? No, simpler to return text.
    # Wait, previous step asked to call this function. Let's return text here.
    # Actually, simpler: analyze_with_gemini handles the label for fallback.
    # Rerunning logic:
    
    full_text = " ".join([f.get('title', '') + " " + f.get('body', '') for f in facts_list]).lower()
    claim_lower = claim.lower()
    
    # ... (Keep existing logic code) ...

    stopwords = set(['this', 'that', 'with', 'from', 'have', 'were', 'will', 'your', 'been', 'there', 'about', 'just', 'happen', 'happened', 'mock', 'drill', 'simulating', 'emergency', 'airport', 'simulates', 'simulated'])
    
    claim_words = re.sub(r'[^\w\s]', '', claim_lower).split()
    core_keywords = [w for w in claim_words if len(w) > 3 and w not in stopwords]
    
    # 0. CATEGORY DETECTION
    is_news = any(w in claim_lower for w in ['today', 'yesterday', 'breaking', 'news', 'happen', 'drills', 'crash', 'arrest', '2026', '2025'])
    cat_label = "NEWS" if is_news else "FACTUAL"

    # 1. PER-RESULT VERIFICATION (Strict Mode)
    final_verdict = f"Verdict: FALSE\nCategory: {cat_label}\nReason: ⚠️ [BASIC MODE] No matching sources confirm this specific claim. (GenAI was busy)."
    high_score = 0
    
    # Synonym Map
    synonyms = {
        'leader': ['president', 'chief', 'chairman', 'head', 'founder'],
        'president': ['leader', 'chief', 'chairman', 'head'],
        'freedom': ['independence', 'revolutionary', 'martyr'],
        'fighter': ['activist', 'soldier', 'leader']
    }
    
    negations = ["fake", "false", "hoax", "debunk", "not true", "untrue", "scam", "myth", "misrepresented", "unverified"]

    for fact in facts_list:
        content = (fact.get('title', '') + " " + fact.get('body', '')).lower()
        
        match_count = 0
        for word in core_keywords:
            if word in content:
                match_count += 1
            elif word in synonyms:
                if any(syn in content for syn in synonyms[word]):
                    match_count += 1
        
        score = match_count / len(core_keywords) if core_keywords else 0
        if score > high_score: high_score = score
            
        # STRICT TRUE (90%+)
        if score >= 0.9:
            found_negation = any(neg in content for neg in negations)
            if found_negation:
                return f"Verdict: FALSE\nCategory: {cat_label}\nReason: ⚠️ [BASIC MODE] Found negation/debunking language in a matching source. (GenAI was busy)."
            else:
                return f"Verdict: TRUE\nCategory: {cat_label}\nReason: ⚠️ [BASIC MODE] Verified entity and role in a reliable source. (GenAI was busy)."

    # 2. DECISIVE FALLBACK
    if high_score >= 0.75:
        return f"Verdict: MISLEADING\nCategory: {cat_label}\nReason: ⚠️ [BASIC MODE] Partial match ({int(high_score*100)}%). Source names match but connection is unclear. (GenAI was busy)."
    
    return f"Verdict: FALSE\nCategory: {cat_label}\nReason: ⚠️ [BASIC MODE] No reliable source confirmed this specific claim. (Best match: {int(high_score*100)}%). (GenAI was busy)."

import requests
from xml.etree import ElementTree

# ... (Previous imports like st, pickle continue above) ...

def search_news_rss(query):
    """
    Directly fetches Google News via RSS (Unblockable & Fast).
    Returns list of dicts: [{'title':..., 'body':...}]
    """
    try:
        encoded_query = requests.utils.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
        
        response = requests.get(url, timeout=4)
        if response.status_code == 200:
            root = ElementTree.fromstring(response.content)
            items = root.findall('.//item')
            results = []
            for item in items[:5]:
                title = item.find('title').text
                link = item.find('link').text
                # RSS doesn't give body text, so we use Title + Link as context
                results.append({'title': title, 'body': f"Source: {link}"})
            return results
    except Exception as e:
        print(f"RSS Error: {e}")
    return []

def get_web_context(text):
    """
    Gathers snippets using Google News RSS (Primary) + DuckDuckGo (Backup).
    """
    context_data = []
    
    # 1. Google News RSS (Strategy A: Exact Query)
    print(f"Trying RSS Exact: {text}")
    results = search_news_rss(text)
    if results:
        context_data.extend(results)
    
    # 2. Google News RSS (Strategy B: Simple Keywords)
    if len(context_data) < 1:
        # Fallback to first 6 significant words
        stopwords = ['the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with']
        words = [w for w in text.split() if w.lower() not in stopwords]
        simple_query = " ".join(words[:6])
        print(f"Trying RSS Fallback: {simple_query}")
        
        results = search_news_rss(simple_query)
        if results:
            for res in results:
                if not any(d['title'] == res['title'] for d in context_data):
                    context_data.append(res)

    # 3. DuckDuckGo (Backup if RSS fails completely)
    if len(context_data) < 1:
        try:
            results = DDGS().text(text, backend='html', max_results=3)
            if results:
                for res in results:
                    context_data.append({'title': res['title'], 'body': res['body']})
        except: pass

    # 4. Wikipedia (For Definitions/History)
    try:
        topics = wikipedia.search(text, results=1)
        if topics:
            page = wikipedia.page(topics[0], auto_suggest=False)
            context_data.append({'title': f"Wikipedia: {page.title}", 'body': page.summary[:500]})
    except: pass
            
    return context_data

if st.button("Verify with GenAI 🧠"):
    if not news_text.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Step 1: Searching the Web... 🌐"):
            facts = get_web_context(news_text)
            
        if not facts:
            st.error(f"🚨 **FAKE NEWS**")
            st.markdown(f"### 🧐 AI Analysis:")
            st.info("Verdict: FALSE\nReason: 🚫 No online records or news sources found for this specific claim. Real news would be documented on the web.")
        else:
            with st.spinner("Step 2: Asking Gemini AI... 🤖"):
                # Call LLM
                ai_response, intelligence_source = analyze_with_gemini(news_text, facts)
                
                # Parse Output
                is_fact = "Category: FACTUAL" in ai_response
                label_suffix = "FACT" if is_fact else "NEWS"

                if "Verdict: TRUE" in ai_response:
                    st.success(f"✅ **REAL {label_suffix}**")
                elif "Verdict: FALSE" in ai_response:
                    st.error(f"🚨 **FAKE {label_suffix}**")
                else: 
                    st.warning(f"⚠️ **MISLEADING / COMPLEX**")
                
                # Display Reason
                st.markdown(f"### 🧐 AI Analysis:")
                st.info(ai_response)
                
                st.caption(f"🧠 Intelligence Source: **{intelligence_source}**")
                
                # Show Sources
                st.markdown("### 📚 Context Sources:")
                for f in facts[:2]:
                    st.caption(f"**{f['title']}**: {f['body'][:150]}...")

# Examples
with st.expander("Try Tricky Logic Examples"):
    st.markdown("""
    * "Chess is an Olympic game." (Result: FALSE - Recognized but not in Games)
    * "Kabaddi is an Olympic game." (Result: FALSE)
    * "Narendra Modi is the President of India." (Result: FALSE - He is PM)
    """)
