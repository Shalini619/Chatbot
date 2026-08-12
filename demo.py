from google import genai
from dotenv import load_dotenv
from google.genai import types
import json
from pydantic import BaseModel
from database import execute_query, get_schema
load_dotenv()
class QueryResult(BaseModel):
    sql: str
    question: str
client=genai.Client()
schema= get_schema("orders")
while True:
    user_input=input("Enter your question:")
    if user_input=='exit':
        break
    else:
        prompt=f"""You are a Microsoft SQL Server expert.
        Write ONE SQL query based on the question below.
        Question:
        {user_input}
        use below orders table schema
        {schema} STRICT RULES: 
        1. The database is Microsoft SQL Server.
        2. Use Microsoft SQL Server / T-SQL syntax.
        3. NEVER use LIMIT.
        4. If you need to limit rows, use TOP.
        5. Only use the columns listed above.
        6. Return only a SELECT statement.
        """
        response=client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types. GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=QueryResult
                )
            )
        json_response=json.loads(response.text)
        final_sql=json_response['sql']
        final_result=execute_query(final_sql)
        #print(final_sql)
        print(final_result)