# 🤖 TalentScout: AI Technical Interviewer (PG-AGI)

**TalentScout** ek specialized AI-powered recruitment assistant hai jo PG-AGI ke liye candidates ka initial screening aur technical interview process automate karta hai. Yeh chatbot candidate ki details collect karta hai aur unke tech stack ke basis par real-time, tailored technical questions generate karta hai.

---

## 🚀 Key Features

* **Automated Information Gathering:** Name, Email, Phone, Location, aur Experience ka seamless data collection.
* **Dynamic Tech Assessment:** Llama 3.3 (via Groq Cloud) ka use karke candidate ke tech stack ke hisaab se **exactly 5 questions** poochta hai.
* **Adaptive Difficulty:** Sawalon ka level fundamental definition se shuru hokar gradually scenario-based/conceptual tak jata hai.
* **Privacy-First (GDPR):** Data save karte waqt sensitive information (jaise email) ko mask karta hai.
* **Dual Storage System:** Saara candidate data aur unke answers automatically `JSON` aur `CSV` formats mein save ho jate hain.
* **Modern UI:** Streamlit-based clean interface jisme custom CSS branding aur full-screen layout diya gaya hai.

---

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/)
* **AI Engine:** [Groq Cloud SDK](https://console.groq.com/)
* **LLM Model:** `llama-3.3-70b-versatile`
* **Language:** Python 3.9+
* **Data Handling:** JSON & CSV modules

---

## ⚙️ Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/yourusername/talentscout-chatbot.git](https://github.com/yourusername/talentscout-chatbot.git)
    cd talentscout-chatbot
    ```

2.  **Install Required Packages:**
    ```bash
    pip install streamlit groq
    ```

3.  **API Configuration:**
    `app.py` file mein apni Groq API key enter karein:
    ```python
    GROQ_API_KEY = "your_gsk_key_here"
    ```

4.  **Launch the App:**
    ```bash
    streamlit run app.py
    ```

---

## 📂 Data Storage Details



Interview khatam hote hi system 2 files generate/update karta hai:
1.  **`interview_data.json`**: Developer-friendly structured format.
2.  **`interview_data.csv`**: HR-friendly spreadsheet format.

**Note:** Privacy logic ke mutabiq, email ID ko `ex****@domain.com` format mein secure kiya jata hai.

---

## 📝 Interview Flow

1.  **Greeting:** AI apna intro deta hai.
2.  **Profile Building:** Candidate se basic personal aur professional info mangi jati hai.
3.  **Technical Round:** 5 AI-generated questions (one-by-one).
4.  **Completion:** Data storage confirmation aur thank you note.

---

### Developed for PG-AGI Recruitment Team 🚀