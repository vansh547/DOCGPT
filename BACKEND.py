import google.generativeai as genai
import os
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

SYSTEM_PROMPT = (
    "You are DOC, a smart, professional medical chatbot who can have ongoing conversations. "
    "If a user sends you text from a file (lab results, prescriptions, etc.), read and advise as best you can. "
    "Be accurate, friendly, and clear."
)

def format_history_for_gemini(history):
    full_prompt = SYSTEM_PROMPT
    for turn in history:
        if turn['role'] == "user":
            full_prompt += f"\nUser: {turn['content']}"
        else:
            full_prompt += f"\nDOC: {turn['content']}"
    return full_prompt

def ask_medical_gemini(history):
    prompt = format_history_for_gemini(history)
    try:
        response = model.generate_content(prompt)
        answer = (response.text or "").strip()
        return answer if answer else "Sorry, I couldn't generate a response right now."
    except Exception as e:
        print("Gemini error:", e)
        return "Sorry, I'm having trouble connecting to the medical engine right now."



