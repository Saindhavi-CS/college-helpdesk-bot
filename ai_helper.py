
import streamlit as st
from openai import OpenAI


def ask_ai(question, pdf_text):
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model="gpt-5.5",
        instructions=(
            "You are a College Helpdesk assistant. "
            "Answer using only the supplied college document. "
            "If the document does not contain the answer, "
            "say that the information was not found. "
            "Be clear, helpful, and concise."
        ),
        input=(
            f"COLLEGE DOCUMENT:\n{pdf_text[:40000]}\n\n"
            f"STUDENT QUESTION:\n{question}"
        ),
    )

    return response.output_text
