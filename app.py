
import streamlit as st
from sql_chatbot_chain import db_chain, get_db_schema
from rag_chain import rag_chain
import re

st.set_page_config(page_title="E-commerce Chat Assistant", layout="wide")
st.title("💬 E-commerce Chat Assistant")

# Predefined sample questions
sample_questions = [
    "What does shipping mean?",
    "What is pending order status?",
    "What is the return policy?",
    "Show top 5 customers by total spend",
    "Which product has the lowest stock?",
    "List all orders with 'PENDING' status",
    "How does the refund process work?",
    "Top 5 cities by order volume",
    "Type your own..."
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
# st.sidebar.header("🧱 Database Tables")
# try:
#     schema = get_db_schema()
#     for table, columns in schema.items():
#         with st.sidebar.expander(f"📦 {table}", expanded=False):
#             for col in columns:
#                 st.markdown(f"- {col}")
# except Exception as e:
#     st.sidebar.error(f"Could not load schema: {e}")

# Input Section (Dropdown + Text Input)
st.markdown("### Ask your question")
selected = st.selectbox("Choose a predefined question or type your own:", sample_questions)

if selected == "Type your own...":
    custom_query = st.text_input("Enter your question here:")
    final_query = custom_query.strip()
else:
    final_query = selected

# Process query
if final_query:
    with st.spinner("🤖 Thinking..."):
        try:
            if is_rag_query(final_query):
                response = rag_chain.invoke(final_query)
            else:
                response = db_chain(final_query)

            # Display response
            st.markdown("### 🧠 Answer")
            if isinstance(response, list) and all(isinstance(row, (list, tuple)) for row in response):
                st.dataframe(response)
            else:
                st.markdown(response)

            # Save to session history
            st.session_state.chat_history.append({
                "user": final_query,
                "bot": response
            })

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Chat History Section
if st.session_state.chat_history:
    st.markdown("---")
    st.markdown("### 📜 Chat History")
    for chat in reversed(st.session_state.chat_history[-5:]):
        st.markdown(f"**You:** {chat['user']}")
        st.markdown(f"**Bot:** {chat['bot']}")
