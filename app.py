import streamlit as st
from sql_chatbot_chain import db_chain
from rag_chain import rag_chain
from typing import Any, List
import re

st.set_page_config(page_title="E-commerce Chat Assistant", layout="wide")
st.title("E-commerce Chat Assistant")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Smart RAG detection based on query content
def is_rag_query(query: str) -> bool:
    q = query.lower()
    # doc_keywords = [
    #     "policy", "workflow", "return", "refund", "meaning of", "explain",
    #     "how does", "guidelines", "terms", "definition", "process"
    # ]
    # likely_sql_patterns = [
    #     r"\btop\b", r"\bmost\b", r"\bleast\b", r"\btotal\b", r"\bsum\b",
    #     r"\bcount\b", r"\bshow\b", r"\blist\b", r"\bnumber of\b",
    #     r"\bhow many\b", r"\bwhich\b.*\b(product|customer|order|payment)\b"
    # ]
    # if any(re.search(p, q) for p in likely_sql_patterns):
    #     return False
    rag_keywords = ["explain", "what does", "how does", "define", "meaning of", "status of", "policy", "return", "workflow"]
    # return any(k in q for k in doc_keywords)
    return any(kw in query.lower() for kw in rag_keywords)

# Ask user for a question
query = st.text_input("Ask your question:")

if query:
    with st.spinner("Thinking..."):
        try:
            if is_rag_query(query):
                response = rag_chain.invoke(query)
            else:
                response = db_chain(query)

            # Show result
            st.markdown("### Answer:")
            if isinstance(response, list) and all(isinstance(row, (list, tuple)) for row in response):
                st.dataframe(response)
            else:
                st.markdown(response)

            # Save to session history
            st.session_state.chat_history.append({
                "user": query,
                "bot": response
            })

        except Exception as e:
            st.error(f"Error: {str(e)}")

# Show chat history
if st.session_state.chat_history:
    st.markdown("---")
    st.markdown("### Chat History")
    for chat in reversed(st.session_state.chat_history[-5:]):  # last 5 exchanges
        st.markdown(f"**You:** {chat['user']}")
        st.markdown(f"**Bot:** {chat['bot']}")
