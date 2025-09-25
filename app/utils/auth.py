import jwt
from datetime import datetime, timezone, timedelta
from decouple import config
from passlib.context import CryptContext

SECRET_KEY = config('SECRET_KEY')
ALGORITHM = config('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(config('ACCESS_TOKEN_EXPIRE_MINUTES'))

pwd_content = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(pwd: str):
    return pwd_content.hash(pwd)


def verify_password(plain_pwd: str, hashed_pwd: str):
    return pwd_content.verify(plain_pwd, hashed_pwd)


def create_access_token(data: dict):
    to_encode = data.copy()    
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        
        if username is None:
            return None
        return username
    except jwt.PyJWTError:
        return None


