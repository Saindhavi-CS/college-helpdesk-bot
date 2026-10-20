
from pathlib import Path
import re
import ollama
import streamlit as st
from pypdf import PdfReader
from openai import OpenAI
from login_ui import show_login_page
from rag_service import retrieve_relevant_chunks


# ==========================================
# 1. PROJECT SETUP
# ==========================================
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "documents"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="College Helpdesk Bot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
# Login protection
if "user" not in st.session_state:
    show_login_page()
    st.stop()

user = st.session_state["user"]

# Logged-in user details
st.sidebar.write(f"👤 {user['email']}")
st.sidebar.write(f"Role: {user['role']}")

if st.sidebar.button("Logout"):
    del st.session_state["user"]
    st.rerun()
# ==========================================
# 2. MIDNIGHT LAVENDER THEME
# ==========================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #090E1C, #11172B 55%, #17152E);
    color: #E5E7F2;
}

[data-testid="stHeader"] {
    background: rgba(9, 14, 28, 0.95);
}

.block-container {
    max-width: 1400px;
    padding: 1.5rem 2rem 3rem;
}

h1, h2, h3 {
    color: #F4F1FF !important;
}

p, label, li {
    color: #D1D6E8;
}

section[data-testid="stSidebar"] {
    background: #11172B;
    border-right: 1px solid #303653;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #CDB7FF !important;
}

div[data-testid="stTextInput"] input {
    background: #171D33;
    color: #FFFFFF;
    border: 1px solid #41496B;
    border-radius: 12px;
    padding: 0.8rem;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #A6AEC8;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: #171D33;
    color: #F4F1FF;
    border-color: #41496B;
    border-radius: 12px;
}

div.stButton > button {
    background: linear-gradient(135deg, #8066D6, #A78BFA);
    color: #FFFFFF;
    border: 1px solid #B8A6FF;
    border-radius: 12px;
    font-weight: 600;
    transition: 0.2s ease;
}

div.stButton > button:hover {
    background: #B09AFF;
    color: #11172B;
    border-color: #D2C5FF;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(23, 29, 51, 0.88);
    border: 1px solid #343B5C;
    border-radius: 16px;
}

div[data-testid="stChatMessage"] {
    background: #171D33;
    border: 1px solid #303957;
    border-radius: 15px;
}

div[data-testid="stFileUploader"] {
    background: #171D33;
    border: 1px dashed #71639A;
    border-radius: 12px;
    padding: 0.6rem;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

.stCaption, small {
    color: #AEB7D2 !important;
}

hr {
    border-color: #303957;
}

.hero {
    background: linear-gradient(120deg, #151B30, #30264F, #554078);
    border: 1px solid #66548A;
    padding: 34px;
    border-radius: 22px;
    margin: 12px 0 24px 0;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
}

.hero-eyebrow {
    color: #CDB7FF;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 3px;
    margin-bottom: 12px;
}

.hero-title {
    color: #FFFFFF;
    font-size: 34px;
    font-weight: 750;
    line-height: 1.25;
    margin-bottom: 12px;
}

.hero-description {
    color: #DDD5EE;
    font-size: 16px;
    line-height: 1.7;
    margin-bottom: 0;
}

.section-note {
    color: #AEB7D2;
    font-size: 14px;
}

.tip-card {
    background: #171D33;
    border: 1px solid #343B5C;
    padding: 16px;
    border-radius: 15px;
    min-height: 110px;
}

.tip-title {
    color: #D8CBFF;
    font-weight: 650;
    margin-bottom: 8px;
}

.tip-description {
    color: #B8C1D9;
    font-size: 13px;
    line-height: 1.5;
}
            
/* Glassmorphism — Midnight Lavender */

.stApp {
    background:
        radial-gradient(
            circle at 15% 15%,
            rgba(139, 92, 246, 0.20),
            transparent 35%
        ),
        radial-gradient(
            circle at 85% 75%,
            rgba(96, 80, 180, 0.18),
            transparent 35%
        ),
        linear-gradient(135deg, #090E1C, #11172B 55%, #17152E);
    color: #F3F0FF;
}

/* Glass cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 255, 255, 0.045);
    border: 1px solid rgba(216, 180, 254, 0.22);
    border-radius: 20px;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.20);
}

/* Glass inputs */
.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(255, 255, 255, 0.07);
    color: #FFFFFF;
    border: 1px solid rgba(216, 180, 254, 0.30);
    border-radius: 12px;
    backdrop-filter: blur(12px);
}

/* Glass buttons */
.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(
        135deg,
        rgba(139, 92, 246, 0.90),
        rgba(109, 75, 170, 0.90)
    );
    color: #FFFFFF;
    border: 1px solid rgba(221, 214, 254, 0.35);
    border-radius: 12px;
    transition: all 0.25s ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    border-color: #DDD6FE;
    box-shadow: 0 0 22px rgba(167, 139, 250, 0.35);
    transform: translateY(-2px);
}

/* Sidebar glass background */
section[data-testid="stSidebar"] {
    background: rgba(15, 18, 39, 0.88);
    border-right: 1px solid rgba(216, 180, 254, 0.18);
}

/* Glass tabs */
button[data-baseweb="tab"] {
    color: #D8D4E8;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #DDD6FE;
    border-bottom-color: #A78BFA;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. SESSION STATE
# ==========================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "recent_searches" not in st.session_state:
    st.session_state.recent_searches = []

if "question_input" not in st.session_state:
    st.session_state.question_input = ""

if "user_role" not in st.session_state:
    st.session_state.user_role = "Student"


def choose_tip(question):
    st.session_state.question_input = question


# ==========================================
# 4. WELCOME BANNER
# ==========================================
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">YOUR TRUSTED ACADEMIC ASSISTANT📚..</div>
    <div class="hero-title">Welcome to Helpdesk Bot ✨</div>
    <p class="hero-description">
        Your academic companion for college rules, syllabus,
        examination guidelines, and campus documents.
    </p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 5. PROFILE AND LANGUAGE
# ==========================================
profile_col, language_col = st.columns([1, 1])

with profile_col:
    role = st.selectbox(
        "👤 Your profile",
        ["Student", "Faculty"],
        key="user_role",
    )

with language_col:
    language = st.selectbox(
        "🌐 Answer language",
        ["English", "Tamil", "Hindi"],
        key="answer_language",
    )

if role == "Student":
    st.caption(
        "🎓 Student Portal · Syllabus, exams, attendance and college rules"
    )
else:
    st.caption(
        "👩‍🏫 Faculty Portal · Academic documents and college regulations"
    )

st.divider()


# ==========================================
# 6. PDF UPLOAD AND DOCUMENT LIBRARY
# ==========================================
with st.sidebar:
    st.markdown("## 🎓 Helpdesk")
    st.caption("MIDNIGHT LAVENDER")

    st.divider()
    st.header("📤 Upload PDF")

    uploaded_file = st.file_uploader(
        "Choose a college document",
        type=["pdf"],
        key="pdf_uploader",
    )

    if uploaded_file is not None:
        safe_name = Path(uploaded_file.name).name
        save_path = DOCS_DIR / safe_name

        if not save_path.exists():
            try:
                reader = PdfReader(uploaded_file)

                if len(reader.pages) == 0:
                    st.error("This PDF has no pages.")
                else:
                    save_path.write_bytes(uploaded_file.getvalue())
                    st.success("PDF uploaded successfully!")
                    st.cache_data.clear()
                    st.rerun()

            except Exception as exc:
                st.error(f"{type(exc).__name__}: {exc}")
                st.stop()
    else:
            st.info("This PDF already exists.")

    st.divider()
    st.header("📚 Document Library")


# ==========================================
# 7. READ PDF DOCUMENTS
# ==========================================
@st.cache_data
def load_documents():
    records = []
    errors = []

    for pdf_path in sorted(DOCS_DIR.glob("*.pdf")):
        try:
            reader = PdfReader(str(pdf_path))

            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""

                if text.strip():
                    records.append({
                        "document": pdf_path.name,
                        "page": page_number,
                        "text": text,
                    })

        except Exception as exc:
            errors.append(f"{pdf_path.name}: {exc}")

    return records, errors


records, errors = load_documents()

with st.sidebar:
    documents = sorted({
        record["document"] for record in records
    })

    st.metric("Readable PDF pages", len(records))

    if documents:
        for document in documents:
            st.caption(f"📄 {document}")
    else:
        st.info("No readable PDF documents yet.")

    if errors:
        with st.expander("Document reading errors"):
            for error in errors:
                st.caption(error)

    st.divider()
    st.header("🕘 Recent Searches")

    if st.session_state.recent_searches:
        for index, recent in enumerate(
            st.session_state.recent_searches
        ):
            st.button(
                f"🔎 {recent}",
                key=f"recent_{index}",
                on_click=choose_tip,
                args=(recent,),
                use_container_width=True,
            )
    else:
        st.caption("Your recent questions will appear here.")


# ==========================================
# 8. FIND RELEVANT PDF PAGES
# ==========================================
STOP_WORDS = {
    "the", "is", "are", "a", "an", "of", "to", "in",
    "for", "and", "or", "what", "how", "when", "where",
    "can", "i", "my", "do", "does", "be", "on", "with",
    "college", "please", "tell", "me", "about", "from",
    "tell", "which", "who", "why", "this", "that",
}
def find_matches(question, document_records):
    return retrieve_relevant_chunks(
        question=question,
        records=document_records,
        top_k=5,
    )
    if not words:
        return []

    matches = []

    for record in document_records:
        text_words = {
            word.lower()
            for word in re.findall(
                r"[a-zA-Z0-9]+", record["text"]
            )
        }

        matched_words = words.intersection(text_words)

        if matched_words:
            score = len(matched_words) / len(words)
            matches.append((score, record))

    matches.sort(key=lambda item: item[0], reverse=True)

    return [record for score, record in matches[:5]]

# OpenAI client: read the API key securely from Streamlit secrets
@st.cache_resource
def get_openai_client():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
def generate_ai_answer(question, matches, language="English"):
    if not matches:
        return (
            "Uploaded college documents-ல் இந்தக் "
            "கேள்விக்குப் பொருத்தமான தகவல் கிடைக்கவில்லை."
        )

    context_parts = []

    for item in matches:
        context_parts.append(
            f"Document: {item['document']}\n"
            f"Page: {item['page']}\n"
            f"Content: {item['text']}"
        )

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""
You are a College Helpdesk Assistant.

Answer the question using ONLY the supplied document context.
If the context does not contain the answer, say that the
uploaded documents do not provide enough information.
Do not invent college rules, dates, fees, or procedures.
Answer in this language: {language}.

DOCUMENT CONTEXT:
{context}

STUDENT QUESTION:
{question}
"""

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        options={"temperature": 0.1},
    )

    return response["message"]["content"].strip()


    context = "\n\n---\n\n".join(context_parts)

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=(
            "You are a professional College Helpdesk Assistant. "
            "Answer using only the supplied college PDF context. "
            "Explain the information clearly and naturally. "
            "Do not invent college rules or facts. "
            "If the context does not answer the question, say that "
            "the uploaded PDFs do not provide enough information. "
            f"Write the answer in {answer_language}. "
            "Do not invent page numbers or citations."
        ),
        input=(
            f"Student or faculty question:\n{question}\n\n"
            f"Relevant college PDF context:\n{context}"
        ),
        max_output_tokens=700,
    )

    return response.output_text
# ==========================================
# 9. BUILD PDF-BASED ANSWER
# ==========================================
def build_free_answer(matches, answer_language):
    if not matches:
        if answer_language == "Tamil":
            return "PDF-ல் தொடர்புடைய தகவல் கிடைக்கவில்லை."
        if answer_language == "Hindi":
            return "PDF में संबंधित जानकारी नहीं मिली."
        return "No matching information was found in the PDFs."

    if answer_language == "Tamil":
        heading = "📄 PDF ஆவணங்களில் கிடைத்த தகவல்:"
    elif answer_language == "Hindi":
        heading = "📄 PDF दस्तावेज़ों में मिली जानकारी:"
    else:
        heading = "📄 Relevant information found in the PDFs:"

    sections = []

    for record in matches:
        text = record["text"].strip()

        if text:
            sections.append(
                f"**Source:** {record['document']}  \n"
                f"**PDF page:** {record['page']}  \n\n"
                f"{text[:1800]}"
            )

    if not sections:
        return "No readable text found in the matching PDF pages."

    return heading + "\n\n---\n\n".join(sections)


# ==========================================
# 10. ASK THE HELPDESK
# ==========================================
st.markdown("## 💡Ask the College Helpdesk")
st.markdown(
    '<p class="section-note">Search your uploaded college PDFs and find relevant information.</p>',
    unsafe_allow_html=True,
)

with st.form("question_form", clear_on_submit=True):
    question = st.text_input(
        "Your question",
        placeholder="Example: What is the exam attendance requirement?",
        key="question_input",
    )

    submitted = st.form_submit_button(
        "✨ Find Answer",
        use_container_width=True,
    )

if submitted:
    if not question.strip():
        st.warning("Please enter a question.")

    elif not records:
        st.warning(
            "No readable PDF pages found. Upload a valid PDF first."
        )

    else:
        matches = find_matches(question, records)

        if not matches:
            st.warning(
                "No matching information found. Try different keywords."
            )
        else:
            
            with st.spinner("🤖 AI is reading your college documents..."):
                try:
                    answer_text = generate_ai_answer(
                        question,
                        matches,
                        language,
                    )
                except Exception as exc:
                    st.error(
                        "AI answer failed. Check your API key, "
                        "API billing, internet connection, and terminal error."
                    )
                    st.caption(f"Error details: {exc}")
                    st.stop()

            st.subheader("🎓 Answer")
            st.markdown(answer_text)

            sources = [
                f"{record['document']} | Page {record['page']}"
                for record in matches
            ]

            st.session_state.chat_history.append({
                "question": question,
                "answer": answer_text,
                "sources": sources,
                "role": role,
                "language": language,
            })

            if question not in st.session_state.recent_searches:
                st.session_state.recent_searches.insert(0, question)

            st.session_state.recent_searches = (
                st.session_state.recent_searches[:8]
            )

            st.rerun()


# ==========================================
# 11. CHAT HISTORY AND ANSWERS
# ==========================================
st.markdown("## 💬 Conversation History")

if not st.session_state.chat_history:
    st.info(
        "Welcome! Ask a question above to start your conversation."
    )

else:
    for chat in reversed(st.session_state.chat_history):
        with st.chat_message("user"):
            st.write(chat["question"])
            st.caption(f"Profile: {chat.get('role', 'Student')}")

        with st.chat_message("assistant"):
            st.markdown(chat["answer"])

            if chat.get("sources"):
                st.caption("Citations: " + "; ".join(chat["sources"]))


# ==========================================
# 12. QUICK TIPS
# ==========================================
st.divider()
st.markdown("## ✨ Quick Tips")
st.caption("Try one of these questions to get started.")

tip_columns = st.columns(3)

tips = [
    (
        "📘 Syllabus",
        "Find my syllabus and unit-wise topics",
    ),
    (
        "📝 Examinations",
        "What are the examination rules?",
    ),
    (
        "🎓 Attendance",
        "What does the PDF say about attendance?",
    ),
]

for column, (title, prompt) in zip(tip_columns, tips):
    with column:
        st.markdown(
            f"""
            <div class="tip-card">
                <div class="tip-title">{title}</div>
                <div class="tip-description">{prompt}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.button(
            f"Ask this question",
            key=f"tip_{title}",
            on_click=choose_tip,
            args=(prompt,),
            use_container_width=True,
        )


# ==========================================
# 13. CLEAR CHAT HISTORY
# ==========================================
st.divider()

if st.button("🗑️ Clear Chat History"):
    st.session_state.chat_history = []
    st.session_state.recent_searches = []
    st.rerun()

st.caption(
    "College Helpdesk Bot · Midnight Lavender · "
    "Answers are based on uploaded PDF documents."
)