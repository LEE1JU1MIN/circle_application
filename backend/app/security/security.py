from passlib.context import CryptContext

_pwd = CryptContext(schemes=["bcrypt", "pbkdf2_sha256"], deprecated="auto")

#비밀번호 해쉬화 
def hash_pw(p: str) -> str:
    return _pwd.hash(p)

#해쉬 비밀번호 해석
def verify_pw(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain, hashed)