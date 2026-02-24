import os
import re
import json
import csv
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# --- 1. ENV SETUP ---
load_dotenv("API.env")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# --- 2. SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are TalentScout, an AI interviewer.

- Ask 5 technical questions based on the candidate's tech stack.
- Start simple, then move to real-world or conceptual questions.
- Keep each question short and clear.
- Ask only one question at a time.
"""

# --- 3. PAGE CONFIG + CSS (Original Frontend Style) ---
st.set_page_config("TalentScout | PG-AGI", "", layout="wide")
st.markdown("""
<style>
.block-container { max-width: 100% !important; padding: 0 !important; }
[data-testid="stSidebar"] { display: none; }
header { visibility: hidden; }

/* NAVBAR */
.talentscout-header {
    background: #0F172A;
    padding: 15px 60px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: white;
    width: 100%;
    position: fixed;
    top: 0;
    z-index: 999;
}
.brand-text { font-size: 24px; font-weight: 800; }

/* HERO */
.hero-bg {
    background: white;
    padding: 60px 20px 20px 20px;
    text-align: center;
    border-bottom: 1px solid #E2E8F0;
}
.hero-h1 { font-size: 42px; font-weight: 800; color: #1E293B; margin: 5px 0; }

/* CHAT BODY */
.chat-body {
    max-width: 900px;
    margin: 20px auto;
    padding: 0 20px 100px 20px;
}
</style>
""", unsafe_allow_html=True)

# --- 4. NAVBAR + HERO ---
st.markdown('<div class="talentscout-header"><div class="brand-text">Talentscout</div><div style="font-size:12px;opacity:0.8;">ONLINE MODE</div></div>', unsafe_allow_html=True)
st.markdown('<div class="hero-bg"><p style="color:#64748B;font-size:14px;margin-bottom:0;">PG-AGI RECRUITMENT</p><h1 class="hero-h1">PG-AGI Hiring Assistant 🤖</h1>', unsafe_allow_html=True)

logo_path = "1701980258268.jpeg"
c1, c2, c3 = st.columns([1,0.3,1])
with c2:
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 5. HELPER FUNCTIONS ---
def is_valid_name(name: str) -> bool:
    name = name.strip()
    return len(name) >= 3 and all(ch.isalpha() or ch.isspace() for ch in name)

def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def is_valid_tech_stack(tech: str) -> bool:
    tech = tech.strip().lower()
    blacklist = ["0","nasd","asdf","none","nothing","xyz","123","null","test"]
    if len(tech) < 2 or tech in blacklist: return False
    if not any(ch.isalpha() for ch in tech): return False
    return True

def mask_data_for_privacy(data: dict) -> dict:
    safe_copy = data.copy()
    if "email" in safe_copy:
        email = safe_copy["email"]
        if "@" in email:
            safe_copy["email"] = email[:2] + "****" + email[email.find("@"):]
        else:
            safe_copy["email"] = "hidden@domain.com"
    return safe_copy

def save_to_json(data: dict, file_name="interview_data.json"):
    records = []
    if os.path.exists(file_name):
        try:
            with open(file_name,"r") as f: records = json.load(f)
        except: records = []
    records.append(data)
    with open(file_name,"w") as f: json.dump(records,f,indent=4)

def save_to_csv(data: dict, file_name="interview_data.csv"):
    file_exists = os.path.isfile(file_name)
    with open(file_name,"a",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists: writer.writeheader()
        writer.writerow(data)

# --- 6. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"assistant","content":"Namaste! I'm **Talentscout**. Let's start with your **Full Name**?"}]
if "step" not in st.session_state: st.session_state.step = "name"
if "user_data" not in st.session_state: st.session_state.user_data = {}
if "q_count" not in st.session_state: st.session_state.q_count = 0

# --- 7. PROCESS INPUT ---
def process_input(user_input: str):
    step = st.session_state.step
    user_input = user_input.strip()
    if not user_input: 
        st.warning("Please type something before continuing."); return

    # PHASE 1: Candidate info
    if step == "name":
        if is_valid_name(user_input):
            st.session_state.user_data["name"] = user_input
            st.session_state.step = "email"
            return f"Nice to meet you, **{user_input}**! Can you share your **Email ID**?"
        return "Hmm... that doesn't look like a valid name. Try again."

    elif step == "email":
        if is_valid_email(user_input):
            st.session_state.user_data["email"] = user_input
            st.session_state.step = "phone"
            return "Now please provide your **Contact Number** (with country code)."
        return "Please enter a valid email."

    elif step == "phone":
        digits_only = re.sub(r"\D","",user_input)
        if len(digits_only)>=10:
            st.session_state.user_data["phone"] = user_input
            st.session_state.step = "location"
            return "Which **City/Location** are you based in?"
        return "Phone number seems invalid. Try again."

    elif step == "location":
        st.session_state.user_data["location"] = user_input
        st.session_state.step = "exp"
        return "How many **years of experience** do you have? (0 if fresher)"

    elif step == "exp":
        st.session_state.user_data["exp"] = user_input
        st.session_state.step = "tech"
        return "Great! What is your **tech stack** or primary skills? (e.g. Python, Java, SQL)"

    # PHASE 2: Technical interview
    elif step in ["tech","interview"]:
        if step=="tech":
            if is_valid_tech_stack(user_input):
                st.session_state.user_data["tech_stack"] = user_input
                st.session_state.step = "interview"
            else:
                return "Invalid tech stack — try again (Python, Java, React)."

        if step=="interview" and st.session_state.q_count>0:
            st.session_state.user_data[f"q{st.session_state.q_count}_ans"] = user_input

        st.session_state.q_count += 1
        if st.session_state.q_count <= 5:
            with st.spinner("Generating next question..."):
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role":"system","content":SYSTEM_PROMPT},
                            {"role":"user","content":f"Candidate Tech: {st.session_state.user_data['tech_stack']}. Question {st.session_state.q_count}/5."}
                        ],
                        model="llama-3.3-70b-versatile"
                    )
                    current_q = chat_completion.choices[0].message.content.strip()
                    st.session_state.user_data[f"q{st.session_state.q_count}_question"] = current_q
                    return f"**Technical Round ({st.session_state.q_count}/5):**\n\n{current_q}"
                except Exception as e:
                    print(f"[error] Groq API failed: {e}")
                    return "Couldn’t fetch the question — try again."
        else:
            st.session_state.step = "done"
            masked = mask_data_for_privacy(st.session_state.user_data)
            save_to_json(masked)
            save_to_csv(masked)
            name = masked.get("name","Candidate")
            return f"Thanks, **{name}**! Great job! We’ve successfully received your responses and are excited to review them. You’ll hear from us on your email very soon.."

    return "All steps completed — thank you!"

# --- 8. CHAT DISPLAY ---
st.markdown('<div class="chat-body">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_prompt = st.chat_input("Type your message here...")
if user_prompt:
    st.session_state.messages.append({"role":"user","content":user_prompt})
    with st.chat_message("user"): st.markdown(user_prompt)

    bot_reply = process_input(user_prompt)
    st.session_state.messages.append({"role":"assistant","content":bot_reply})
    with st.chat_message("assistant"): st.markdown(bot_reply)

st.markdown("</div>", unsafe_allow_html=True)

# --- 9. DOWNLOAD BUTTON AFTER INTERVIEW COMPLETION ---
if st.session_state.step == "done":
    csv_path = "interview_data.csv"
    if os.path.exists(csv_path):
        with open(csv_path, "rb") as file:
            st.download_button(
                label="Download All Candidate Data (CSV)",
                data=file,
                file_name="candidate_responses.csv",
                mime="text/csv",
                help="Click to download all collected candidate responses"
            )
