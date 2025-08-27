import os
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
SALT = "session-cookie"

serializer = URLSafeTimedSerializer(SECRET_KEY, salt=SALT)

#세션 토크 생성
def make_session_token(user_id: int) -> str:
    return serializer.dumps({"uid": user_id})

#세션 토크 유효성 검증 (현재:24시간 유효)
def parse_session_token(token: str, max_age_seconds: int = 60 * 60 * 24) -> int | None:
    try:
        data = serializer.loads(token, max_age=max_age_seconds)
        return int(data["uid"])
    except (SignatureExpired, BadSignature, KeyError):
        return None
