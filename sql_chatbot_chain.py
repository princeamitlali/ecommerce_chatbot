from langchain.agents import AgentExecutor
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
import os
import re
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

db = SQLDatabase.from_uri("sqlite:///db/ecommerce.db")

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
memory = ConversationBufferMemory(return_messages=True)

agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=False,
    return_intermediate_steps=True,
    handle_parsing_errors=True,
    memory=memory  # 
)

DESTRUCTIVE_PATTERN = re.compile(r"\b(DELETE|DROP|UPDATE|INSERT|TRUNCATE|ALTER|REPLACE)\b", re.IGNORECASE)

def get_db_schema():
    from sqlalchemy import inspect
    inspector = inspect(db)
    schema = {}
    for table_name in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns(table_name)]
        schema[table_name] = columns
    return schema

def db_chain(user_query: str, raw_output=False):
    result = None

    try:
        result = agent_executor.invoke({"input": user_query})
        sql_steps = [step['tool_input'] for step in result.get('intermediate_steps', []) if 'tool_input' in step]

        for sql in sql_steps:
            print(sql)
            if DESTRUCTIVE_PATTERN.search(sql):
                return "Query blocked: Destructive statements are not allowed."

        output = result.get("output", "")

        if raw_output and isinstance(output, list):
            return output

        if isinstance(output, str) and output.strip().lower() in ["i don't know", "i do not know", "idk"]:
            return "Sorry, I couldn't find an answer to that in the database."

        return output

    except Exception as e:
        if "Could not parse LLM output" in str(e):
            return "I'm not sure how to answer that. Could you rephrase it?"
        return f"SQL agent error: {str(e)}"


