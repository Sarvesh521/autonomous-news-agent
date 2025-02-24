import sys
import psycopg2
import json
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = "mydb"
USER = "postgres"
PASSWORD = os.getenv("DB_PASSWORD")
HOST = "localhost"
PORT = "5432"

DB_LOAD_FILE = "summarized_articles.json"


def check_topic_exists(topic):
    # Check if the topic exists in the database
    conn, cur = connect_to_db(DB_NAME)
    try:
        cur.execute("SELECT 1 FROM topic_summaries WHERE main_topic = %s;", (topic,))
        exists = cur.fetchone()
        return bool(exists)
    except Exception as e:
        print("Error checking topic:", e)
        return False
    
    cur.close()
    conn.close()

def connect_default():
    """Connect to the default 'postgres' database."""
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        )
        conn.autocommit = True
        cur = conn.cursor()
        print("Connected to default database 'postgres'.")
        return conn, cur
    except Exception as e:
        print("Error connecting to PostgreSQL default database:", e)
        exit(1)

def create_database_if_not_exists(db_name):
    """Check if the target database exists. If not, create it."""
    conn, cur = connect_default()
    try:
        cur.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s;"), [db_name])
        exists = cur.fetchone()
        if not exists:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
            print(f"Database '{db_name}' created.")
        else:
            print(f"Database '{db_name}' already exists.")
    except Exception as e:
        print("Error checking/creating database:", e)
    finally:
        cur.close()
        conn.close()

def connect_to_db(db_name):
    """Connect to the target database."""
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        )
        cur = conn.cursor()
        print(f"Connected to PostgreSQL database '{db_name}'.")
        return conn, cur
    except Exception as e:
        print(f"Error connecting to PostgreSQL database '{db_name}':", e)
        exit(1)

def create_table(cur, conn):
    """Create the topic_summaries table if it does not exist."""
    create_table_query = """
        CREATE TABLE IF NOT EXISTS topic_summaries (
            main_topic TEXT PRIMARY KEY,
            content JSONB
        );
    """
    try:
        cur.execute(create_table_query)
        conn.commit()
        print("Table 'topic_summaries' created (or already exists).")
    except Exception as e:
        print("Error creating table:", e)
        conn.rollback()
        cur.close()
        conn.close()
        exit(1)

def load_data_from_json(file_path=DB_LOAD_FILE):
    """Load summarized articles from the JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("Data loaded from summarized_articles.json.")
        return data
    except Exception as e:
        print("Error loading JSON file:", e)
        exit(1)

def insert_topic_summary(cur, conn, main_topic, subtopics):
    """Insert or update the topic summary for the main topic."""
    try:
        cur.execute("""
            INSERT INTO topic_summaries (main_topic, content)
            VALUES (%s, %s)
            ON CONFLICT (main_topic)
            DO UPDATE SET content = EXCLUDED.content;
        """, (main_topic, json.dumps(subtopics)))
        conn.commit()
        print(f"Data for main topic '{main_topic}' inserted/updated successfully.")
    except Exception as e:
        print(f"Error inserting data for main topic '{main_topic}':", e)
        conn.rollback()

def query_topic(cur, topic):
    """Query and print the document for the given topic."""
    try:
        cur.execute("SELECT * FROM topic_summaries WHERE main_topic = %s;", (topic,))
        result = cur.fetchone()
        if result:
            print("\nFound document for main topic:", topic)
            print(json.dumps(result[1], indent=4))
            # write this to summarized_articles.json file 
            with open("summarized_articles.json", "w") as file:
                json.dump(result[1], file, indent=4)
            return result[1]
        else:
            print(f"\nNo document found for main topic: {topic}")
    except Exception as e:
        print("Error querying data:", e)

def setup_database(db_name):
    """
    Setup database by creating it if it doesn't exist,
    connecting to it, creating the table, and returning the connection and cursor.
    """
    create_database_if_not_exists(db_name)
    conn, cur = connect_to_db(db_name)
    create_table(cur, conn)
    return conn, cur

def main(topic_name):
    conn, cur = setup_database(DB_NAME)
    data = load_data_from_json()
    subtopics = []

    for record in data:
        subtopics.append({
            "topic_name": record.get("topic_name", ""),
            "title": record.get("title", ""),
            "summary": record.get("summary", ""),
            "location": record.get("location", "")
        })
    

    if not subtopics:
        print(f"No summarized records found for topic '{topic_name}'.")
    else:
        insert_topic_summary(cur, conn,topic_name, subtopics)
        print("Data inserted successfully.")
        query_topic(cur,topic_name)
        print("Database processing completed successfully.")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main("Tennis")