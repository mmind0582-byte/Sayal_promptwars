import json, os, logging
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("blindspot")

app = Flask(__name__, static_folder="static")

SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
try:
    with open(SYSTEM_PROMPT_PATH, encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
except Exception as e:
    logger.error(f"Failed to read system_prompt.txt: {e}")
    SYSTEM_PROMPT = "You are Blind Spot, a Socratic thinking companion. You help a person examine HOW they are reasoning about a decision."

def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

@app.get("/")
def index():
    return send_from_directory("static", "index.html")

@app.get("/health")
def health():
    has_key = bool(os.environ.get("GEMINI_API_KEY"))
    return jsonify({
        "status": "healthy",
        "api_key_configured": has_key,
        "model_configured": os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    })

@app.post("/api/analyze")
def analyze():
    client = get_client()
    if not client:
        return jsonify(
            error="GEMINI_API_KEY is not set. Please set the GEMINI_API_KEY environment variable or define it in a .env file."
        ), 400

    d = request.get_json(force=True) or {}
    decision = (d.get("decision") or "").strip()
    reasons = (d.get("reasons") or "").strip()
    if not decision or not reasons:
        return jsonify(error="Please describe both your decision and your reasons."), 400

    parts = [f"DECISION: {decision}\n\nDETAILS/FACTS: {(d.get('details') or '').strip() or '(none given)'}\n\nMY REASONS: {reasons}"]
    for r in d.get("rounds", [])[-4:]:  # earlier questions + user's answers
        parts.append("YOUR EARLIER QUESTIONS:\n" + "\n".join(f"- {q}" for q in r.get("questions", [])))
        parts.append("MY ANSWERS:\n" + (r.get("answers") or "")[:3000])

    candidate_models = [
        os.environ.get("GEMINI_MODEL"),
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
    ]
    # Unique non-empty models
    models_to_try = [m for i, m in enumerate(candidate_models) if m and m not in candidate_models[:i]]

    last_error = None
    for model_name in models_to_try:
        try:
            logger.info(f"Attempting analysis with model: {model_name}")
            resp = client.models.generate_content(
                model=model_name,
                contents="\n\n".join(parts)[:12000],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    temperature=0.7,
                ),
            )
            data = json.loads(resp.text)
            return jsonify(data)
        except Exception as e:
            logger.warning(f"Model '{model_name}' encountered an error: {e}")
            last_error = e
            continue

    logger.exception(last_error)
    return jsonify(error=f"Model generation failed: {str(last_error)}"), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Blind Spot on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port)
