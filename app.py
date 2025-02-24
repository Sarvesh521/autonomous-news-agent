import workflow 
import database as db
import time

TOPIC_NAME = "Fantasy Football" 

def main(topic):
    if db.check_topic_exists(topic):
        print(f"Topic {topic} already exists in the database.")
        conn,cur = db.connect_to_db(db.DB_NAME)
        print("Fetching topic summary from the database...")
        db.query_topic(cur,topic)
        cur.close()
        conn.close()
    else:
        print(f"Topic {topic} does not exist in the database.")
        workflow.main(topic)

if __name__ == "__main__":
    start_time = time.time()
    main(TOPIC_NAME)
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time:.2f} seconds.")