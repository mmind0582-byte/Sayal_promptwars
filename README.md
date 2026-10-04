# 🔍 Blind Spot — Socratic Decision Intelligence

> **PromptWars 2026 Submission** | Powered by **Google Gemini API** & **Google Cloud Run**

Blind Spot is an AI thinking companion designed to expose what a decision-maker is *not* seeing. Rather than providing advice, picking choices, or acting as an answer engine, Blind Spot employs the **Socratic Method** to dissect the reasoning behind a choice: surfacing hidden assumptions, unweighed variables, internal goal contradictions, and reflective questions that leave the ultimate decision in human hands.

---

## 🎯 The Problem

When faced with critical decisions (career shifts, education, investments, relationships), humans naturally anchor to salient, easy-to-quantify attributes (e.g., immediate salary, commute distance) while systematically overlooking:
1. **Unstated Assumptions:** Underlying beliefs taken as given without verification.
2. **Mentioned But Unweighed Factors:** Crucial facts stated in passing that never factored into the core evaluation.
3. **Completely Unmentioned Angles:** Reversibility, opportunity cost, learning velocity, and second-order consequences.
4. **Internal Tensions:** Contradictions between stated priorities and chosen courses of action.

---

## 🧠 Socratic Prompt Engineering & Guardrails

The engine is driven by a carefully structured system prompt ([`system_prompt.txt`](./system_prompt.txt)):

- **Hard No-Verdict Constraint:** Under no circumstances does the model advise, rank options, or say *"you should"* or *"the better choice is"*.
- **The "Just Tell Me What To Do" Guardrail:** If an overwhelmed user pleads for an answer, the model gently triggers a warm `reframe` notice clarifying its role as an intellectual mirror, not a surrogate decision-maker.
- **Hyper-Specific Anchoring:** Generic platitudes (*"weigh pros and cons"*) are prohibited. The model quotes back specific names, figures, and constraints provided by the user.
- **Internal Conflict Detection:** Specifically identifies cognitive dissonance (e.g., valuing academic excellence while taking a 40-hour work week during exams).
- **Multi-Round Recursive Deepening:** Users can respond to reflective questions in subsequent rounds, allowing the AI to prune resolved blind spots and drill into deeper premises.

---

## 🛠️ Tech Stack & Architecture

- **AI Model:** Google Gemini (`gemini-2.5-flash` with dynamic fallback to `gemini-2.0-flash` / `gemini-1.5-flash`) via `google-genai` SDK
- **Backend:** Python / Flask with JSON mode schema enforcement
- **Frontend:** Vanilla HTML5 / Modern CSS (Zero heavy JS framework dependencies, glassmorphism design system)
- **Deployment:** Docker / Google Cloud Run (Containerized via Gunicorn)

---

## 🚀 Quickstart & Local Setup

### Prerequisites
- Python 3.10+
- A Google Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

### 1. Clone & Install
```bash
git clone https://github.com/YOUR_USERNAME/blindspot.git
cd blindspot
pip install -r requirements.txt
```

### 2. Configure API Key
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run Locally
```bash
python app.py
```
Open **[http://localhost:8080](http://localhost:8080)** in your browser.

---

## ☁️ Deployment Guide (Google Cloud Run)

### Method A: Via Google Cloud Shell (Fastest & Recommended)
1. Push your repository to GitHub.
2. Open [Google Cloud Shell](https://shell.cloud.google.com).
3. Clone and deploy:
   ```bash
   git clone https://github.com/YOUR_USERNAME/blindspot.git
   cd blindspot
   gcloud run deploy blindspot \
     --source . \
     --region asia-south1 \
     --allow-unauthenticated \
     --set-env-vars GEMINI_API_KEY=your_gemini_api_key
   ```
4. Copy the deployed Service URL (`https://blindspot-xxxx.asia-south1.run.app`).

### Method B: Via Google Cloud Console (Web UI)
1. Navigate to **Cloud Run** in the Google Cloud Console.
2. Click **Create Service**.
3. Choose **Continuously deploy from a repository** and connect your GitHub repo.
4. Under **Variables & Secrets**, add `GEMINI_API_KEY`.
5. Click **Create**.

---

## 📋 Hack2Skill Submission Checklist
- [x] **Challenge Category:** The Blind Spot
- [x] **Public GitHub Repo:** Containing all source code and documentation
- [x] **Live Deployed URL:** Google Cloud Run service endpoint
- [x] **Gemini API Integration:** Built using the `google-genai` SDK
