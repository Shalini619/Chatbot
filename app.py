import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel
import json

from database import execute_query, get_schema

load_dotenv()


# -----------------------------
# Gemini response structure
# -----------------------------
class QueryResult(BaseModel):
    sql: str
    question: str


# -----------------------------
# Gemini client
# -----------------------------
client = genai.Client()


# -----------------------------
# Get database schema
# -----------------------------
schema = get_schema("orders")


# -----------------------------
# Streamlit page configuration
# -----------------------------
st.set_page_config(
    page_title="SQL Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 CHATBOT")
st.write("Ask questions about your orders database.")


# -----------------------------
# Chat history
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -----------------------------
# User input
# -----------------------------
user_input = st.chat_input("Ask a question about your orders...")


if user_input:

    # Display user question
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # -----------------------------
    # Generate SQL with Gemini
    # -----------------------------
    prompt = f"""
You are a Microsoft SQL Server expert.

Write ONE SQL query based on the question below.

Question:
{user_input}

Use the following orders table schema:

{schema}

STRICT RULES:

1. The database is Microsoft SQL Server.
2. Use Microsoft SQL Server / T-SQL syntax.
3. NEVER use LIMIT.
4. If you need to limit rows, use TOP.
5. Only use the columns listed in the schema.
6. Return only a SELECT statement.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=QueryResult
            )
        )

        json_response = json.loads(response.text)

        final_sql = json_response["sql"]

        # -----------------------------
        # Execute SQL
        # -----------------------------
        final_result = execute_query(final_sql)

        columns, rows = final_result

        # -----------------------------
        # Display result
        # -----------------------------
        with st.chat_message("assistant"):

            st.subheader("Generated SQL")

            st.code(final_sql, language="sql")

            st.subheader("Result")

            if rows:
                # Convert database rows into dictionaries
                data = [
                    dict(zip(columns, row))
                    for row in rows
                ]

                st.dataframe(
                    data,
                    use_container_width=True
                )

            else:
                st.info("No results found.")

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": f"```sql\n{final_sql}\n```\n\nNo. of rows returned: {len(rows)}"
            }
        )

    except Exception as e:

        with st.chat_message("assistant"):
            st.error(f"Error: {e}")