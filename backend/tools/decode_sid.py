# decode_sid.py
import os
import time
import argparse
from pathlib import Path
from typing import Optional

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired


SALT = "session-cookie"          # 서버에서 signer.py와 동일해야 함
DEFAULT_MAX_AGE = 60 * 60 * 24   # 24h


def load_sid_from_cookies(cookies_path: Path) -> Optional[str]:
    """
    curl의 cookies.txt(Netscape 포맷)에서 sid 값을 읽어옵니다.
    마지막 라인의 sid를 우선 사용합니다.
    """
    if not cookies_path.exists():
        return None
    sid = None
    with cookies_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            # Netscape 포맷: domain, flag, path, secure, expires, name, value
            if len(parts) >= 7:
                name = parts[5]
                value = parts[6]
                if name == "sid":
                    sid = value
    return sid


def decode_sid(token: str, secret_key: str, max_age: int = DEFAULT_MAX_AGE):
    s = URLSafeTimedSerializer(secret_key, salt=SALT)
    data = s.loads(token, max_age=max_age)  # 만료 검사 포함
    return data  # 예: {"uid": 4}


def show_once(cookies_path: Path, secret_key: str, max_age: int):
    sid = load_sid_from_cookies(cookies_path)
    if not sid:
        print("cookies.txt에서 sid를 찾지 못했습니다.")
        return
    try:
        data = decode_sid(sid, secret_key, max_age)
        print(f"[OK] sid 디코드: {data}  (token={sid})")
    except SignatureExpired:
        print("[만료] 토큰이 만료되었습니다.")
    except BadSignature:
        print("[오류] 서명이 유효하지 않습니다.(SECRET_KEY 또는 토큰 불일치)")
    except Exception as e:
        print(f"[예외] {type(e).__name__}: {e}")


def watch(cookies_path: Path, secret_key: str, max_age: int, interval: float = 1.0):
    last_sid = None
    last_mtime = 0.0
    print(f"Watching {cookies_path} ... (Ctrl+C to stop)")
    while True:
        try:
            mtime = cookies_path.stat().st_mtime if cookies_path.exists() else 0.0
            if mtime != last_mtime:
                last_mtime = mtime
                sid = load_sid_from_cookies(cookies_path)
                if sid and sid != last_sid:
                    last_sid = sid
                    print("\n[변경 감지] 새로운 sid:")
                    try:
                        data = decode_sid(sid, secret_key, max_age)
                        print(f"  디코드: {data}  (token={sid})")
                    except SignatureExpired:
                        print("  [만료] 토큰이 만료되었습니다.")
                    except BadSignature:
                        print("  [오류] 서명이 유효하지 않습니다.(SECRET_KEY 또는 토큰 불일치)")
                    except Exception as e:
                        print(f"  [예외] {type(e).__name__}: {e}")
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n종료합니다.")
            break


def main():
    parser = argparse.ArgumentParser(description="sid 쿠키 실시간 디코더")
    parser.add_argument("--cookies", default="cookies.txt", help="cookies.txt 경로")
    parser.add_argument("--secret", default=os.getenv("SECRET_KEY"), help="서버 SECRET_KEY(환경변수로 주는 것을 권장)")
    parser.add_argument("--max-age", type=int, default=DEFAULT_MAX_AGE, help="토큰 만료(초)")
    parser.add_argument("--watch", action="store_true", help="파일 변경 감시 모드")
    args = parser.parse_args()

    if not args.secret:
        print("SECRET_KEY가 필요합니다. 환경변수 SECRET_KEY 또는 --secret 로 전달하세요.")
        raise SystemExit(1)

    cookies_path = Path(args.cookies)

    if args.watch:
        watch(cookies_path, args.secret, args.max_age)
    else:
        show_once(cookies_path, args.secret, args.max_age)


if __name__ == "__main__":
    main()