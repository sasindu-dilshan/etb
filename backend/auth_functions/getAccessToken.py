import os
import jwt
import time


def get_access_token(user_id, auth_level, plan):
    access_secret_key = os.environ.get("ACCESS_TOKEN_SECRET")
    timestamp = time.time()
    expiration_time = timestamp + 5 * 60 # expires in 5 minutes
    payload = {
        "user_id": user_id,
        "auth_level": auth_level,
        "plan": plan,
        "timestamp": timestamp,
        "exp": expiration_time,
        "token_type": "access"
    }
    token = jwt.encode(payload, access_secret_key, algorithm="HS256")
    return token
