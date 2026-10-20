
import math
import streamlit as st
import ollama

CHAT_MODEL = "llama3.2:3b"
EMBEDDING_MODEL = "nomic-embed-text"


def chunk_documents(records, chunk_size=1200, overlap=200):
    chunks = []

    for record in records:
        text = record["text"].strip()
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "document": record["document"],
                    "page": record["page"],
                    "text": chunk_text,
                })

            if end >= len(text):
                break

            start = end - overlap

    return chunks


@st.cache_data(show_spinner=False)
def embed_document_chunks(chunks):
    texts = [chunk["text"] for chunk in chunks]
    vectors = []

    # Small batches avoid sending too much text at once.
    for start in range(0, len(texts), 16):
        batch = texts[start:start + 16]

        result = ollama.embed(
            model=EMBEDDING_MODEL,
            input=batch,
        )

        vectors.extend(result["embeddings"])

    return vectors


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if not norm_a or not norm_b:
        return 0.0

    return dot / (norm_a * norm_b)


def retrieve_relevant_chunks(question, records, top_k=5):
    if not question.strip() or not records:
        return []

    chunks = chunk_documents(records)

    if not chunks:
        return []

    document_vectors = embed_document_chunks(chunks)

    query_result = ollama.embed(
        model=EMBEDDING_MODEL,
        input=question.strip(),
    )
    query_vector = query_result["embeddings"][0]

    ranked = []

    for chunk, vector in zip(chunks, document_vectors):
        result = dict(chunk)
        result["similarity"] = cosine_similarity(
            query_vector, vector
        )
        ranked.append(result)

    ranked.sort(
        key=lambda item: item["similarity"],
        reverse=True,
    )

    selected = []
    seen_pages = set()

    for item in ranked:
        page_key = (item["document"], item["page"])

        if page_key in seen_pages:
            continue

        selected.append(item)
        seen_pages.add(page_key)

        if len(selected) >= top_k:
            break

    return selected
