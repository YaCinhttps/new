# 🚀 Smart ADL

Smart ADL is a Streamlit-based platform that helps you:
- ✍️ Write and test **ADL code** with AI assistance
- ⚡ Optimize ADL code automatically
- 🧪 Create, run, and evaluate **prompts & tests**
- 📜 Save and review **AI test history** and **ADL code history**
- 👥 Manage multiple users with login/registration

---

## 📂 Project Structure

```
smart-adl/
│── app.py              # Main Streamlit application
│── prompts.sqlite      # SQLite database (auto-created)
│── requirements.txt    # Dependencies
│── README.md           # Project documentation
```

---

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/smart-adl.git
   cd smart-adl
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your Google Gemini API key**

   Create a `.streamlit/secrets.toml` file:
   ```toml
   API_KEY = "your_gemini_api_key_here"
   ```

---

## ▶️ Usage

Run the app with:
```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📖 Features

### 🔹 ADL Development
- Write ADL code with an integrated editor
- Ask questions to Gemini AI about ADL
- Insert AI-generated code snippets directly into the editor
- Save code + responses in history

### 🔹 Code Optimization
- Paste your ADL code
- AI suggests a more efficient, clean, and readable version
- Save optimized code

### 🔹 Prompts & Tests
- Create custom prompts with expected answers
- Run batch tests against Gemini
- Evaluate correctness automatically
- Import/export prompts in JSON

### 🔹 History
- Review test results (prompt, expected, AI answer, correctness)
- Review ADL code history (code, question, AI response)
- Delete items if needed

### 🔹 User Management
- Register/login/logout system
- Passwords stored securely (hashed)
- Each user has separate prompts/tests/history

---

## 🛠️ Requirements

- Python 3.9+
- Streamlit
- google-generativeai
- sqlite3
- bcrypt (recommended for secure passwords)

📌 Example `requirements.txt`:
```txt
streamlit
google-generativeai
bcrypt
```

---

## 🔒 Security Notes

- Your API key must be kept secret in `.streamlit/secrets.toml`.
- Passwords are hashed before storage.
- Never commit `prompts.sqlite` with real data to GitHub.

---

## 📌 Roadmap

- [ ] Add prompt search/filter in history
- [ ] Export all prompts to JSON at once
- [ ] Improve ADL code parsing (extract only valid code blocks)
- [ ] Switch from SQLite to PostgreSQL/MySQL for scalability

---

## 👨‍💻 Author

**Yassine Harbaoui**  
📍 Kef, Tunisia  
