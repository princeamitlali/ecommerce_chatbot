# from langchain.chains import RetrievalQA
# from langchain_community.vectorstores import FAISS
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# import os
# from dotenv import load_dotenv

# load_dotenv()
# embedding = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))


# vectorstore = FAISS.load_local(
#     folder_path="vectorstore/schema_knowledge",
#     embeddings=embedding,
#     allow_dangerous_deserialization=True
# )

# retriever = vectorstore.as_retriever()
# llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))

# rag_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")  # optional if already in env

# Use Gemini embeddings
embedding = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",  # Gemini 1.5 embedding model
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Load FAISS vector store
vectorstore = FAISS.load_local(
    folder_path="vectorstore/schema_knowledge",
    embeddings=embedding,
    allow_dangerous_deserialization=True
)

# Create retriever
retriever = vectorstore.as_retriever()

# Use Gemini LLM (chat model)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest", temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Build RAG chain
rag_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
