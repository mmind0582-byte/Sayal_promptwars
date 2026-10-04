import json
import os
import streamlit as st
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

from google import genai
from google.genai import types

# Page setup
st.set_page_config(
    page_title="Blind Spot: AI Socratic Thinking Companion",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for modern dark theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,500;1,600&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    }

    .main .block-container {
        max-width: 920px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.35);
        color: #A5B4FC;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    .hero-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 2.8rem;
        font-weight: 700;
        line-height: 1.15;
        background: linear-gradient(135deg, #FFFFFF 30%, #CBD5E1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }

    .hero-sub {
        font-size: 1.05rem;
        color: #94A3B8;
        line-height: 1.6;
        margin-bottom: 24px;
    }

    .hear-card {
        background: rgba(30, 41, 59, 0.65);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    }

    .guardrail-card {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.4);
        border-left: 5px solid #F59E0B;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 20px;
        color: #FDE68A;
    }

    .section-header {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.4rem;
        font-weight: 700;
        margin-top: 28px;
        margin-bottom: 14px;
        color: #F8FAFC;
    }

    .item-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }

    .item-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        background: rgba(24, 34, 56, 0.85);
    }

    .tension-card {
        background: rgba(30, 20, 10, 0.6);
        border: 1px solid rgba(245, 158, 11, 0.25);
        border-left: 4px solid #F59E0B;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }

    .conf-box {
        background: rgba(99, 102, 241, 0.08);
        border: 1px dashed rgba(99, 102, 241, 0.4);
        border-radius: 14px;
        padding: 20px;
        margin-top: 24px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Load System Prompt
SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
try:
    with open(SYSTEM_PROMPT_PATH, encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
except Exception:
    SYSTEM_PROMPT = (
        "You are 'Blind Spot', a Socratic thinking companion. You help a person examine HOW "
        "they are reasoning about a decision. You never make the decision for them."
    )

# Resolve API Key from env, streamlit secrets, or sidebar
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass

# Sidebar configuration
with st.sidebar:
    st.markdown("### 🎯 Blind Spot")
    st.markdown(
        "**AI Socratic Thinking Companion**  \n"
        "Surfaces hidden assumptions, overlooked factors, and internal conflicts in decision-making — *without ever deciding for you.*"
    )
    st.markdown("---")
    
    # API key input in sidebar (with auto-fill if detected)
    user_key = st.text_input(
        "Google Gemini API Key",
        value=api_key or "",
        type="password",
        help="Get a free key from https://aistudio.google.com if needed.",
    )
    if user_key:
        api_key = user_key

    st.markdown("---")
    st.markdown("### 🏛️ Socratic Principles")
    st.markdown(
        "- **No verdicts:** Never says 'you should' or chooses for you.\n"
        "- **Boundaries:** Reframes when asked 'just tell me what to do'.\n"
        "- **Specificity:** Quotes your numbers, constraints, and words.\n"
        "- **Internal Conflicts:** Catches contradictory reasoning."
    )
    
    st.markdown("---")
    if st.button("🔄 Reset / Clear", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# Initialize session state keys
if "decision" not in st.session_state:
    st.session_state["decision"] = ""
if "details" not in st.session_state:
    st.session_state["details"] = ""
if "reasons" not in st.session_state:
    st.session_state["reasons"] = ""
if "rounds" not in st.session_state:
    st.session_state["rounds"] = []
if "analysis" not in st.session_state:
    st.session_state["analysis"] = None

# Header Section
st.markdown('<div class="hero-badge">⭐ PromptWars 2026 Submission</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">See what you\'re not seeing.</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">'
    'Describe a decision you are weighing. Blind Spot surfaces the <strong>hidden assumptions, overlooked factors, '
    'and internal contradictions</strong> in your reasoning — without ever choosing for you.'
    '</div>',
    unsafe_allow_html=True,
)

# Presets Row
st.markdown("**Try an example:**")
pcol1, pcol2, pcol3 = st.columns([1, 1, 1.2])

with pcol1:
    if st.button("🎓 6-month Internship", use_container_width=True):
        st.session_state["decision"] = "Should I accept a 6-month internship during my college term?"
        st.session_state["details"] = (
            "Stipend is Rs 15,000/month. Office is 2 km from home. 40 hrs/week, role is 'software intern'. "
            "My college term runs for 4 more months with midterms in 2 months."
        )
        st.session_state["reasons"] = (
            "The stipend is good, the company is close to home, and I'll get industry experience. "
            "Academics matter a lot to me too."
        )
        st.session_state["rounds"] = []
        st.session_state["analysis"] = None
        st.rerun()

with pcol2:
    if st.button("🚀 Safe Job vs Startup", use_container_width=True):
        st.session_state["decision"] = "Should I leave my stable MNC job to join an early-stage AI startup?"
        st.session_state["details"] = (
            "Current job pays 18 LPA with full health insurance and 2 days WFH. "
            "Startup offers 14 LPA + 0.5% equity, 6 days in-office, seed-funded for 14 months."
        )
        st.session_state["reasons"] = (
            "Current job feels repetitive and slow. At the startup I will build things from scratch and learn 5x faster, "
            "but I have personal loan EMIs of 25k/month."
        )
        st.session_state["rounds"] = []
        st.session_state["analysis"] = None
        st.rerun()

with pcol3:
    if st.button("🛡️ Test Guardrail: 'Tell me what to do'", use_container_width=True):
        st.session_state["decision"] = "Bas bata do main kya karun, please choose for me!"
        st.session_state["details"] = (
            "I have two offers and I'm stressed out. Offer A is Infosys in Bangalore, Offer B is TCS in Pune."
        )
        st.session_state["reasons"] = (
            "I can't think anymore, just tell me which city is better and which one I should join."
        )
        st.session_state["rounds"] = []
        st.session_state["analysis"] = None
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Main Form Inputs
decision_input = st.text_input(
    "What are you deciding?",
    value=st.session_state["decision"],
    placeholder="e.g. Accept a 6-month internship during my college term",
    key="input_decision",
)
details_input = st.text_area(
    "Facts & details (pay, timing, constraints, locations, options)",
    value=st.session_state["details"],
    placeholder="Stipend, location, hours, role, learning opportunities, college schedule...",
    height=110,
    key="input_details",
)
reasons_input = st.text_area(
    "Why are you leaning the way you are?",
    value=st.session_state["reasons"],
    placeholder="Your honest reasons, hopes, and anxieties in your own words...",
    height=110,
    key="input_reasons",
)

# Socratic analysis function using Gemini
def run_analysis(decision_text, details_text, reasons_text, rounds_history):
    if not api_key:
        st.error("🔑 GEMINI_API_KEY is not set. Please enter it in the left sidebar.")
        return None

    client = genai.Client(api_key=api_key)
    parts = [
        f"DECISION: {decision_text}\n\nDETAILS/FACTS: {details_text or '(none given)'}\n\nMY REASONS: {reasons_text}"
    ]
    for r in rounds_history[-4:]:
        parts.append("YOUR EARLIER QUESTIONS:\n" + "\n".join(f"- {q}" for q in r.get("questions", [])))
        parts.append("MY ANSWERS:\n" + (r.get("answers") or "")[:3000])

    candidate_models = [
        os.environ.get("GEMINI_MODEL"),
        "gemini-3.1-flash-lite",
        "gemini-3.8-flash",
        "gemini-3.5-flash",
        "gemini-2.5-flash",
    ]
    models_to_try = [m for i, m in enumerate(candidate_models) if m and m not in candidate_models[:i]]

    last_error = None
    for model_name in models_to_try:
        try:
            resp = client.models.generate_content(
                model=model_name,
                contents="\n\n".join(parts)[:12000],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    temperature=0.7,
                ),
            )
            return json.loads(resp.text)
        except Exception as e:
            last_error = e
            continue

    st.error(f"❌ Analysis failed across candidate models: {last_error}")
    return None

# Action button
if st.button("🔍 Show me my blind spots", type="primary", use_container_width=True):
    if not decision_input.strip() or not reasons_input.strip():
        st.warning("⚠️ Please provide both what you are deciding and your reasons.")
    else:
        st.session_state["decision"] = decision_input.strip()
        st.session_state["details"] = details_input.strip()
        st.session_state["reasons"] = reasons_input.strip()
        st.session_state["rounds"] = []

        with st.spinner("Examining reasoning through Socratic lens..."):
            result = run_analysis(
                st.session_state["decision"],
                st.session_state["details"],
                st.session_state["reasons"],
                st.session_state["rounds"],
            )
            if result:
                st.session_state["analysis"] = result

# Render Results
if st.session_state["analysis"]:
    res = st.session_state["analysis"]
    st.markdown("---")

    # What I'm hearing
    if res.get("hearing"):
        st.markdown(
            f"""
            <div class="hear-card">
                <div style="font-size: 0.85rem; font-weight: 700; color: #818CF8; text-transform: uppercase; margin-bottom: 8px;">
                    💬 What I'm Hearing
                </div>
                <div style="font-size: 1.08rem; color: #F1F5F9; line-height: 1.6;">
                    {res.get('hearing')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Reframe Guardrail Alert
    if res.get("reframe"):
        st.markdown(
            f"""
            <div class="guardrail-card">
                <div style="font-size: 0.95rem; font-weight: 700; margin-bottom: 6px;">
                    🛡️ Socratic Boundary Guardrail
                </div>
                <div style="font-size: 0.98rem; line-height: 1.5;">
                    {res.get('reframe')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Helper function for rendering card lists
    def render_items(title, icon, items, is_tension=False):
        if not items:
            return
        st.markdown(f'<div class="section-header">{icon} {title}</div>', unsafe_allow_html=True)
        css_class = "tension-card" if is_tension else "item-card"
        for item in items:
            point = item.get("point", "")
            why = item.get("why_it_matters", "")
            st.markdown(
                f"""
                <div class="{css_class}">
                    <div style="font-weight: 600; color: #FFFFFF; font-size: 0.98rem; margin-bottom: 4px;">
                        {point}
                    </div>
                    <div style="color: #94A3B8; font-size: 0.9rem; line-height: 1.5;">
                        {why}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 4 Core Dimensions
    render_items("Assumptions You May Be Making", "🔍", res.get("assumptions", []))
    render_items("Things You Mentioned But Didn't Weigh", "⚖️", res.get("mentioned_not_weighed", []))
    render_items("Factors You Haven't Mentioned", "💡", res.get("not_mentioned", []))
    render_items("Tensions in Your Reasoning", "⚡", res.get("tensions", []), is_tension=True)

    # Reflective Questions
    questions = res.get("questions", [])
    if questions:
        st.markdown('<div class="section-header">🤔 Questions to Sit With</div>', unsafe_allow_html=True)
        q_answers = []
        for idx, q in enumerate(questions):
            ans = st.text_input(
                f"Question {idx + 1}: {q}",
                placeholder="Type your reflection or answer...",
                key=f"q_ans_{len(st.session_state['rounds'])}_{idx}",
            )
            q_answers.append((q, ans))

    # Confidence Check
    conf_check = res.get("confidence_check")
    conf_ans = ""
    if conf_check:
        st.markdown(
            f"""
            <div class="conf-box">
                <div style="font-weight: 700; color: #A5B4FC; margin-bottom: 6px;">
                    ⏱️ Confidence Check
                </div>
                <div style="color: #E2E8F0; font-size: 1rem; margin-bottom: 12px;">
                    {conf_check}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        conf_ans = st.text_area(
            "What evidence or information would shift your perspective?",
            key=f"conf_ans_{len(st.session_state['rounds'])}",
            height=70,
        )

    # Go deeper action
    if questions or conf_check:
        st.markdown("<br>", unsafe_allow_html=True)
        dcol1, dcol2 = st.columns([1.5, 1])
        with dcol1:
            if st.button("⚡ Go deeper with my answers", use_container_width=True):
                # Prepare round data
                ans_text_list = []
                for q, a in q_answers:
                    ans_text_list.append(f"Q: {q}\nA: {a or '(skipped)'}")
                if conf_check:
                    ans_text_list.append(f"Q: {conf_check}\nA: {conf_ans or '(skipped)'}")

                st.session_state["rounds"].append({
                    "questions": [q for q, _ in q_answers] + ([conf_check] if conf_check else []),
                    "answers": "\n".join(ans_text_list),
                })

                with st.spinner("Going deeper into your answers..."):
                    new_result = run_analysis(
                        st.session_state["decision"],
                        st.session_state["details"],
                        st.session_state["reasons"],
                        st.session_state["rounds"],
                    )
                    if new_result:
                        st.session_state["analysis"] = new_result
                        st.rerun()

        with dcol2:
            st.caption("The decision remains yours. Socratic inquiry only questions the reasoning.")
