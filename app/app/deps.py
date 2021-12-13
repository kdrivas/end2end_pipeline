from app.database import SessionLocal

def get_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()