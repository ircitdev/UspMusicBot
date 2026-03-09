import hashlib
import hmac
import json
from urllib.parse import parse_qs, unquote
from typing import Optional, Dict

from config import settings


def validate_telegram_data(init_data: str) -> Optional[Dict]:
    try:
        parsed = parse_qs(init_data)
        hash_value = parsed.get("hash", [None])[0]
        if not hash_value:
            return None

        data_check_parts = []
        for key, values in sorted(parsed.items()):
            if key != "hash":
                data_check_parts.append(f"{key}={values[0]}")
        data_check_string = "\n".join(data_check_parts)

        secret_key = hmac.new(b"WebAppData", settings.bot_token.encode(), hashlib.sha256).digest()
        computed = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(computed, hash_value):
            return None

        user_str = parsed.get("user", [None])[0]
        if user_str:
            return json.loads(unquote(user_str))
        return {}

    except Exception:
        return None
