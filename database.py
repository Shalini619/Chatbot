import mssql_python

def execute_query(query):
    conn = mssql_python.connect(
        "Server=localhost;Database=salesdb;Trusted_Connection=yes;Encrypt=no"
    )

    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description] if cur.description else []
            return columns, rows

def get_schema(table_name):
    query=f"""Select column_name,data_type
     from information_schema.columns
      where
       table_schema='dbo'
        and table_name='{table_name}'"""
    schema=execute_query(query)
    return schema
#result = get_schema("orders")
#print(result)