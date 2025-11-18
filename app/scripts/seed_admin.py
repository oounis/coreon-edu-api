from app.db.session import get_db
from app.core.security import hash_password
from app import models

def run():
    db = next(get_db())
    user = db.query(models.User).filter(models.User.username == "admin").first()
    if not user:
        user = models.User(
            username="admin",
            role="admin",
            password_hash=hash_password("admin123"),  # FIXED HERE
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print("✅ Created default admin user (admin / admin123)")
    else:
        print("ℹ️ Admin user already exists")

if __name__ == "__main__":
    run()
