def format_duration(seconds: int) -> str:
    if not seconds:
        return "0:00"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def truncate_text(text: str, max_len: int = 100, suffix: str = "...") -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - len(suffix)] + suffix


def escape_markdown(text: str) -> str:
    special = r"_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in special else c for c in text)
