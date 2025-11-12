cat > ~/kogia/coreon-edu-api/app/api/v1/auth/router.py <<'EOF'
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.security import verify_password, create_access_token
from app.db.session import get_db
from app import models

# No local prefix here; main.py adds /api/v1/auth
router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(sub=str(user.id), role=user.role)
    return {"access_token": token, "token_type": "bearer"}
EOF
