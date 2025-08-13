import bcrypt
import jwt
from datetime import datetime, timedelta
import os
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, DecodeError

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def hash_password(password : str) -> str :
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password : str, hashed_password : str) -> bool :
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data : dict, expires_delta : timedelta = None) :
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp" : expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt

def decode_access_token(token : str) :
    try : 
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise ExpiredSignatureError("토큰이 만료되었습니다.")
    except DecodeError:
        raise DecodeError("토큰 디코딩에 실패했습니다.")
    except InvalidTokenError:
        raise InvalidTokenError("유효하지 않은 토큰입니다.")
    except Exception as e:
        raise Exception(f"토큰 검증 중 오류가 발생했습니다: {str(e)}")

def is_token_expired(token: str) -> bool:
    """토큰 만료 여부 확인"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        if exp is None:
            return True
        return datetime.utcnow().timestamp() > exp
    except:
        return True