import streamlit as st
from sql_chatbot_chain import db_chain, get_db_schema
from rag_chain import rag_chain
import re

st.set_page_config(page_title="E-commerce Chat Assistant", layout="wide")
st.title("💬 E-commerce Chat Assistant")
st.warning("🔁 Please avoid making more than 1 query per minute to avoid rate limit errors.", icon="⚠️")

with st.expander("Why this is important?"):
    st.markdown("""
    - LLM APIs like **OpenAI** or **Gemini Pro** have usage quotas.
    - Too many queries in a short time may trigger rate limit blocks or fail with errors.
    - If you're using a **free-tier key**, throttling is even more likely.
    - ✅ For best results, wait at least **60 seconds** between queries.
    """)

# Predefined sample questions
sample_questions = [
    "What does shipping mean?",
    "What is pending order status?",
    "What is the return policy?",
    "Show top 5 customers by total spend",
    "Which product has the lowest stock?",
    "List all orders with 'PENDING' status",
    "How does the refund process work?",
    "Top 5 cities by order volume"
]

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Smart logic to detect whether to use RAG
def is_rag_query(query: str) -> bool:
    q = query.lower()
    rag_keywords = [
        "explain", "what does", "how does", "define", "meaning of",
        "status of", "policy", "return", "workflow", "terms", "guidelines"
    ]
    return any(kw in q for kw in rag_keywords)

# Sidebar – Schema Viewer
st.sidebar.header("🧱 Database Tables")
try:
    schema = get_db_schema()
    for table, columns in schema.items():
        with st.sidebar.expander(f"📦 {table}", expanded=False):
            st.markdown("**Columns:**")
            for col in columns:
                st.markdown(f"- {col}")
except Exception as e:
    st.sidebar.error(f"Could not load schema: {e}")

# Input box with suggestions
st.markdown("### Ask your question")
query = st.selectbox("Choose a predefined question or type your own:", options=[""] + sample_questions, index=0)
custom_input = st.text_input("Or enter a new question:")

# Use input from dropdown if custom not entered
final_query = custom_input.strip() if custom_input.strip() else query

if final_query:
    with st.spinner("🤖 Thinking..."):
        try:
            if is_rag_query(final_query):
                response = rag_chain.invoke(final_query)
            else:
                response = db_chain(final_query)

            # Display answer
            st.markdown("### 🧠 Answer")
            if isinstance(response, list) and all(isinstance(row, (list, tuple)) for row in response):
                st.dataframe(response)
            else:
                st.markdown(response)

            # Update history
            st.session_state.chat_history.append({
                "user": final_query,
                "bot": response
            })

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Chat history
if st.session_state.chat_history:
    st.markdown("---")
    st.markdown("### 📜 Chat History")
    for chat in reversed(st.session_state.chat_history[-5:]):
        st.markdown(f"**You:** {chat['user']}")
        st.markdown(f"**Bot:** {chat['bot']}")
