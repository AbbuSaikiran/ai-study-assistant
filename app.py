"""AI Study Assistant - Streamlit interface.

Ultra-modern, high-aesthetic study assistant powered by Google Gemini.
Flow: Student -> Interactive UI -> Prompt Builder -> Gemini API -> Instant Study Guide
"""

import time
import streamlit as st
from dotenv import load_dotenv

from ai_client import ask_ai, get_api_key, DEFAULT_MODEL
from prompt_builder import MODES, MODE_ICONS, MODE_DESCRIPTIONS, build_prompt

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Study Assistant | Smart Study Hub",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Glassmorphism & Modern Typography)
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Main Container Gradient Ambient */
.stApp {
    background: radial-gradient(circle at 10% 10%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(236, 72, 153, 0.06) 0%, transparent 40%),
                #0f172a;
    color: #f8fafc;
}

/* Hero Banner */
.hero-container {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5), 0 0 20px rgba(99, 102, 241, 0.15);
    backdrop-filter: blur(12px);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
}

.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a5b4fc 0%, #c084fc 50%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.2;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 1.05rem;
    margin-top: 6px;
    margin-bottom: 0;
}

.badge-gemini {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 9999px;
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.35);
    color: #818cf8;
    font-size: 0.85rem;
    font-weight: 600;
}

/* Card Styling */
.stCard, .glass-card {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 16px;
    padding: 20px;
    backdrop-filter: blur(8px);
}

/* Mode Pill Descriptions */
.mode-desc {
    color: #cbd5e1;
    font-size: 0.92rem;
    background: rgba(99, 102, 241, 0.08);
    border-left: 3px solid #6366f1;
    padding: 8px 14px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 16px;
}

/* Result Box Styling */
.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(148, 163, 184, 0.15);
}

.stat-chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.8rem;
    background: rgba(15, 23, 42, 0.6);
    color: #94a3b8;
    border: 1px solid rgba(148, 163, 184, 0.15);
}

/* Primary Button Styling */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 28px !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    letter-spacing: 0.3px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.35) !important;
}

div.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.5) !important;
}

/* Text Area */
.stTextArea textarea {
    background: rgba(15, 23, 42, 0.7) !important;
    border: 1px solid rgba(148, 163, 184, 0.2) !important;
    border-radius: 12px !important;
    color: #f1f5f9 !important;
    font-size: 0.98rem !important;
}

.stTextArea textarea:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.2) !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Session State Initialization
if "study_count" not in st.session_state:
    st.session_state.study_count = 0
if "last_result" not in st.session_state:
    st.session_state.last_result = ""
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ **Settings & Studio**")

    # API Key Configuration
    env_api_key = get_api_key(st.secrets)
    user_api_key = st.text_input(
        "🔑 Gemini API Key",
        value=env_api_key or "",
        type="password",
        placeholder="Paste AIzaSy... key",
        help="Get your free key from Google AI Studio: https://aistudio.google.com/app/apikey",
    )
    active_key = user_api_key.strip() if user_api_key else env_api_key

    if active_key:
        st.caption("🟢 **API Key Connected**")
    else:
        st.warning("⚠️ **Key Required:** Add your free key above or in `.env`")

    st.markdown("---")

    # Model Selector
    model_choice = st.selectbox(
        "🧠 **AI Model**",
        options=["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-3.1-pro-preview"],
        index=0,
        help="gemini-3.6-flash provides ultra-fast, high-quality responses.",
    )

    difficulty = st.select_slider(
        "🎯 **Target Level**",
        options=["Beginner (High School)", "Intermediate (College)", "Advanced (Mastery)"],
        value="Intermediate (College)",
    )

    st.markdown("---")

    # Quick Study Stats
    st.markdown("### 📊 **Your Study Session**")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("Prompts Run", st.session_state.study_count)
    with col_s2:
        st.metric("Model", "Gemini ⚡")

    st.markdown("---")
    st.caption("💡 **Tip:** Try **Generate Quiz** with 5 questions to test your active recall!")


# Hero Banner
st.markdown(
    """
    <div class="hero-container">
        <div>
            <h1 class="hero-title">🎓 AI Study Assistant</h1>
            <p class="hero-subtitle">Instant explanations, smart summaries, practice quizzes & flashcards.</p>
        </div>
        <div>
            <span class="badge-gemini">⚡ Powered by Google Gemini 3.6</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Mode Selection
col_mode, col_options = st.columns([3, 1])

with col_mode:
    mode = st.radio(
        "**Select Study Mode:**",
        MODES,
        format_func=lambda m: f"{MODE_ICONS.get(m, '✨')} {m}",
        horizontal=True,
    )

with col_options:
    num_questions = 5
    if mode in ("Generate Quiz", "Create Flashcards"):
        num_questions = st.slider("Number of items", 3, 12, 5)

# Mode Description
st.markdown(f'<div class="mode-desc">📌 <strong>{mode}:</strong> {MODE_DESCRIPTIONS.get(mode, "")}</div>', unsafe_allow_html=True)

# Sample Starters
sample_topics = {
    "Ask Question": [
        "How does gradient descent optimize neural network weights?",
        "Explain the difference between TCP and UDP with real-world examples.",
        "What is the Krebs Cycle and why is ATP yield important?",
    ],
    "Summarize Notes": [
        "Photosynthesis takes place in two stages: Light-dependent reactions (in thylakoids) generate ATP & NADPH using sunlight, splitting water and releasing oxygen. Light-independent reactions (Calvin cycle in stroma) use ATP & NADPH to fix carbon dioxide into glucose with RuBisCO.",
        "Newton's Laws: 1st Law states an object stays in motion unless acted upon. 2nd Law F=ma connects force, mass, and acceleration. 3rd Law states every action has an equal and opposite reaction.",
    ],
    "Generate Quiz": [
        "Operating Systems: Process vs Thread, Deadlocks, Virtual Memory, Paging, and CPU Scheduling algorithms (FIFO, Round Robin).",
        "World War II: Causes (Treaty of Versailles, rise of fascism), major turning points (Stalingrad, Midway, D-Day), and outcomes.",
    ],
    "Create Flashcards": [
        "Microeconomics: Supply and demand curves, price elasticity, opportunity cost, consumer surplus, monopoly vs perfect competition.",
    ],
    "Explain Like I'm 5": [
        "How does quantum computing work?",
        "Why is the sky blue?",
        "How does blockchain create trust without a central bank?",
    ],
}

st.caption("✨ **Quick Starters (Click to load):**")
quick_cols = st.columns(len(sample_topics.get(mode, [])))
for i, sample_text in enumerate(sample_topics.get(mode, [])):
    short_title = sample_text.split("?")[0].split(":")[0][:38] + ("..." if len(sample_text) > 38 else "")
    if quick_cols[i].button(f"⚡ {short_title}", key=f"quick_{mode}_{i}", use_container_width=True):
        st.session_state.input_text = sample_text

# Text Input Area
placeholders = {
    "Ask Question": "Type your question or difficult concept here...",
    "Summarize Notes": "Paste your lecture notes, textbook excerpt, or article here...",
    "Generate Quiz": "Paste the study material or topics you want to practice on...",
    "Create Flashcards": "Paste key terms, formulas, or concepts to generate recall cards...",
    "Explain Like I'm 5": "Enter any complex topic you want explained simply...",
}

input_val = st.text_area(
    "**Your Study Input:**",
    value=st.session_state.input_text,
    height=180,
    placeholder=placeholders.get(mode, "Enter your material here..."),
)

# Submit button & Actions
col_btn, col_clear = st.columns([4, 1])

with col_btn:
    run_clicked = st.button("🚀 Generate Answer Fast", type="primary", use_container_width=True)

with col_clear:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.input_text = ""
        st.session_state.last_result = ""
        st.rerun()

# Execution Flow
if run_clicked:
    if not input_val.strip():
        st.warning("⚠️ Please enter some text or click a quick starter above first.")
    elif not active_key:
        st.error("🔑 Please enter your Gemini API Key in the sidebar or add `GEMINI_API_KEY` in `.env`.")
    else:
        system, user_prompt = build_prompt(mode, input_val.strip(), num_questions, difficulty)
        
        start_time = time.time()
        with st.spinner("⚡ Gemini is thinking and drafting your answer..."):
            try:
                result = ask_ai(system, user_prompt, active_key, model_name=model_choice)
                elapsed = time.time() - start_time
                st.session_state.last_result = result
                st.session_state.study_count += 1
            except Exception as e:
                st.error(f"❌ Error generating response: {e}")

# Result Display
if st.session_state.last_result:
    result_text = st.session_state.last_result
    words = len(result_text.split())
    reading_time = max(1, round(words / 200))
    
    st.markdown("---")
    st.markdown(
        f"""
        <div class="result-header">
            <div>
                <h3 style="margin: 0; color: #a5b4fc;">📖 Study Guide & Answer</h3>
            </div>
            <div>
                <span class="stat-chip">⏱️ ~{reading_time} min read</span>
                <span class="stat-chip">📝 {words} words</span>
                <span class="stat-chip">🎯 {mode}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Styled Output Box
    st.markdown(result_text)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Download & Quick Tools
    c_dl, c_prompt = st.columns([1, 1])
    with c_dl:
        st.download_button(
            label="📥 Download Study Notes (.md)",
            data=result_text,
            file_name=f"study_notes_{mode.lower().replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with c_prompt:
        with st.expander("🔍 Inspect AI Prompt details"):
            system, user_p = build_prompt(mode, input_val, num_questions, difficulty)
            st.code(f"SYSTEM INSTRUCTION:\n{system}\n\nUSER PROMPT:\n{user_p}", language="markdown")
