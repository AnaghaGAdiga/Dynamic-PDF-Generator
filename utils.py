import os
import re


def ensure_dirs(paths):
    for p in paths:
        if not os.path.exists(p):
            os.makedirs(p, exist_ok=True)


def safe_filename(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9._-]", "_", s)
    return s