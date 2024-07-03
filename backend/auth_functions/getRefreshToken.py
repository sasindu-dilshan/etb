import os
import jwt
import time

def get_refresh_token(user_id, auth_level, plan):
    refresh_secret_key = os.environ.get("REFRESH_TOKEN_SECRET")  # Replace with your actual secret key
    timestamp = time.time()
    expiration_time = timestamp + 7 * 24 * 60 * 60  # expires after 7 days
    payload = {
        "user_id": user_id,
        "auth_level": auth_level,
        "plan": plan,
        "timestamp": timestamp,
        "exp": expiration_time,
        "token_type": "refresh"
    }
    token = jwt.encode(payload, refresh_secret_key, algorithm="HS256")
    return token
