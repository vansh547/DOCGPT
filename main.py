import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import threading
import BACKEND
import speech_recognition as sr
import pyttsx3
from datetime import datetime
import os

# --- SAFE HARDWARE INITIALIZATION ---
# This prevents the app from crashing on cloud servers like Replit/PythonAnywhere
AUDIO_AVAILABLE = False
try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if len(voices) > 1:
        engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 185)
    engine.setProperty('volume', 1.0)
    AUDIO_AVAILABLE = True
except Exception as e:
    print(f"Audio System Unavailable: {e}")

def speak(text):
    if AUDIO_AVAILABLE:
        try:
            # Running speech in a separate thread prevents the GUI from freezing
            def speak_task():
                engine.say(text)
                engine.runAndWait()
            threading.Thread(target=speak_task, daemon=True).start()
        except:
            pass 

# --- UI SETTINGS ---
BG_COLOR = "#222831"
BOT_BUBBLE = "#393E46"
USER_BUBBLE = "#00ADB5"
USER_TEXT_COLOR = "#ffffff"
BOT_TEXT_COLOR = "#00E5FF"
FONT_FAMILY = "Segoe UI"

root = tk.Tk()
root.title("DOC - Medical Chatbot (Live Edition)")
root.geometry("780x700")
root.configure(bg=BG_COLOR)
root.minsize(650, 600)

# --- CHAT DISPLAY ---
chat_box = scrolledtext.ScrolledText(
    root, font=(FONT_FAMILY, 13), bg=BG_COLOR, fg=BOT_TEXT_COLOR,
    wrap="word", state="disabled", padx=16, pady=12, relief="flat", bd=0
)
chat_box.pack(padx=24, pady=(24, 8), fill="both", expand=True)

def show_message(sender, text, sender_type):
    chat_box.config(state="normal")
    timestamp = datetime.now().strftime("%I:%M %p")
    if sender_type == "user":
        chat_box.insert(tk.END, f"\n🧑 {sender} [{timestamp}]\n{text}\n", "user_bubble")
    else:
        chat_box.insert(tk.END, f"\nDOC [{timestamp}]\n{text}\n", "bot_bubble")
    chat_box.see(tk.END)
    chat_box.config(state="disabled")

chat_box.tag_configure("user_bubble", foreground=USER_TEXT_COLOR, justify='right')
chat_box.tag_configure("bot_bubble", foreground=BOT_TEXT_COLOR, justify='left')

# --- INPUT FRAME ---
bottom_frame = tk.Frame(root, bg=BG_COLOR)
bottom_frame.pack(fill="x", padx=24, pady=(0,24))

entry = tk.Entry(bottom_frame, font=(FONT_FAMILY, 13), bg="#EEEEEE", fg="#222831", relief="flat")
entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0,8))

conversation_history = [] 

def disable_input():
    entry.config(state="disabled")
    ask_btn.config(state="disabled")
    mic_btn.config(state="disabled")
    attach_btn.config(state="disabled")

def enable_input():
    entry.config(state="normal")
    ask_btn.config(state="normal")
    mic_btn.config(state="normal")
    attach_btn.config(state="normal")
    entry.focus()

# --- CORE LOGIC ---
def process_user_query():
    user_text = entry.get().strip()
    if not user_text: return
    
    entry.delete(0, tk.END)
    show_message("You", user_text, "user")
    conversation_history.append({"role": "user", "content": user_text})
    
    disable_input()
    def worker():
        show_message("DOC", "Thinking...", "bot")
        answer = BACKEND.ask_medical_gemini(conversation_history)
        show_message("DOC", answer, "bot")
        conversation_history.append({"role": "assistant", "content": answer})
        speak(answer)
        enable_input()
    threading.Thread(target=worker, daemon=True).start()

def listen_microphone():
    try:
        # Check if a microphone is connected before trying to use it
        with sr.Microphone() as source:
            pass
    except Exception:
        messagebox.showinfo("Hardware Info", "Microphone not detected. This feature is disabled on the server.")
        return

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        show_message("DOC", "Listening for your question...", "bot")
        try:
            audio = recognizer.listen(source, timeout=5)
            user_text = recognizer.recognize_google(audio)
            entry.insert(0, user_text)
            process_user_query()
        except:
            show_message("DOC", "Sorry, I couldn't hear that clearly.", "bot")

def attach_file():
    file_path = filedialog.askopenfilename(
        title="Select medical file",
        filetypes=[("Text/PDF/Images", "*.txt;*.csv;*.pdf;*.jpg;*.png;*.webp")]
    )
    if not file_path: return
    
    filename = os.path.basename(file_path)
    show_message("You", f"[Uploaded: {filename}]", "user")
    
    # Extract text if it's a simple text file, otherwise send the filename to the AI
    content = f"The user has attached a file named: {filename}."
    if file_path.lower().endswith(('.txt', '.csv')):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content += f"\nFile content snippet: {f.read(1500)}"
        except: pass

    conversation_history.append({"role": "user", "content": content})
    disable_input()
    def worker():
        show_message("DOC", f"Analyzing {filename}...", "bot")
        answer = BACKEND.ask_medical_gemini(conversation_history)
        show_message("DOC", answer, "bot")
        conversation_history.append({"role": "assistant", "content": answer})
        speak(answer)
        enable_input()
    threading.Thread(target=worker, daemon=True).start()

# --- BUTTONS ---
ask_btn = tk.Button(bottom_frame, text="Send", font=(FONT_FAMILY, 11, "bold"), bg=USER_BUBBLE, fg="white", command=process_user_query)
ask_btn.pack(side="left", padx=5)

mic_btn = tk.Button(bottom_frame, text="🎤", font=(FONT_FAMILY, 12), bg=USER_BUBBLE, fg="white", command=listen_microphone)
mic_btn.pack(side="left", padx=5)

attach_btn = tk.Button(bottom_frame, text="📎", font=(FONT_FAMILY, 12), bg=USER_BUBBLE, fg="white", command=attach_file)
attach_btn.pack(side="left", padx=5)

entry.bind("<Return>", lambda e: process_user_query())

# Initial greeting
show_message("DOC", "Hello, I'm DOC. You can type your symptoms or upload a medical report.", "bot")
root.mainloop()