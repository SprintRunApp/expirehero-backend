import time
from datetime import datetime
from app.db import SessionLocal
from app.services.reminder_engine import run_reminders


def start_worker():
    print("🚀 Worker started...")

    while True:
        print("⏰ Running reminder job:", datetime.utcnow())

        db = SessionLocal()

        try:
            result = run_reminders(db)
            print("✅ RESULT:", result)
        except Exception as e:
            print("❌ ERROR:", e)
        finally:
            db.close()

        # co 1h
        time.sleep(3600)


if __name__ == "__main__":
    start_worker()