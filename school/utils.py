from pathlib import Path


def get_extension(path: str | Path) -> str:
    if isinstance(path, str):
        path = Path(path)

    suffixes = path.suffixes

    # If it is tar, return whole extension
    if len(suffixes) > 1 and suffixes[-2] == ".tar":
        return suffixes[-2] + suffixes[-1]
    elif len(suffixes) > 0:
        return suffixes[-1]

    return ""
