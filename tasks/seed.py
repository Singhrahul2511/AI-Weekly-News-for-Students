# tasks/seed.py
from modules.storage import add_subscriber, get_db

def seed_database():
    """Adds some initial data to the database for testing."""
    print("Seeding database with test subscribers...")
    subscribers_to_add = [
        "test1@example.com",
        "student.ai@university.edu",
        "another-tester@domain.com"
    ]
    with get_db():
        for email in subscribers_to_add:
            if add_subscriber(email):
                print(f"Added subscriber: {email}")
            else:
                print(f"Subscriber already exists: {email}")
    print("Seeding complete.")

if __name__ == "__main__":
    seed_database()