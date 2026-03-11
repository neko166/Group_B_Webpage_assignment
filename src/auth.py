from datetime import datetime, timedelta, timezone
import os
import bcrypt
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from exceptions import AppException, ErrorCode
from schemas import TokenData
import jwt
import models

# --- JWT設定 ---
# 環境変数を読み込みます。設定されていない場合は、安全なデフォルト値を使用するか、エラーを発生させます。

# トークンの有効期限（分）。デフォルトは30分。
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# JWTの署名に使用する秘密鍵。これは必須であり、設定されていない場合はエラーで起動を停止します。
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("環境変数 'JWT_SECRET_KEY' が設定されていません。")

# 署名アルゴリズム。デフォルトはHS256。
ALGORITHM = os.getenv("ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_hashed_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict) -> str:
    data.update({"exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise AppException(ErrorCode.INVALID_TOKEN)
        token_data = TokenData(username=username)
        db_user = db.query(models.User).filter(models.User.username == token_data.username).first()
        if not db_user:
            raise AppException(ErrorCode.INVALID_TOKEN)
        return db_user
    except jwt.ExpiredSignatureError:
        raise AppException(ErrorCode.TOKEN_HAS_EXPIRED)
    except jwt.InvalidTokenError:
        raise AppException(ErrorCode.INVALID_TOKEN)
