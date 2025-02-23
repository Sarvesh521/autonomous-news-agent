import Model as model
import web_scraping as scraper
import database as db
import time

TOPIC_NAME = "Tennis"

def run_web_scraping(topic):
    scraper.main(topic)
    print("Web scraping completed successfully.")

def run_model():
    model.main(model.NO_OF_ARTICLES,model.NO_OF_CHUNKS)
    print("Model processing completed successfully.")

def run_database(topic):
    db.main(topic)
    print("Database processing completed successfully.")

def main(TOPIC_NAME):
    print(f"Starting workflow for topic: {TOPIC_NAME}")

    run_web_scraping(TOPIC_NAME)
    run_model()
    run_database(TOPIC_NAME)

    print("Workflow completed successfully.")

if __name__ == "__main__":
    start_time = time.time()
    main(TOPIC_NAME)
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time:.2f} seconds.")