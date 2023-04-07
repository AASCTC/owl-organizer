import pyodbc
import json

def read_metadata_from_db(connection_string, table_name, article_id):
    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()
        query = f"SELECT * FROM {table_name} WHERE article_id = ?"
        cursor.execute(query, article_id)
        row = cursor.fetchone()
        if row is not None:
            metadata = json.loads(row.metadata)
            return metadata
    return None

def write_metadata_to_db(connection_string, table_name, metadata):
    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()
        query = f"INSERT INTO {table_name} (article_id, metadata) VALUES (?, ?)"
        cursor.execute(query, metadata["@id"], json.dumps(metadata))
        conn.commit()

