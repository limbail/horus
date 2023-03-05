from pathlib import Path

def horus_root() -> Path:
    return str(Path(__file__).parent.parent.parent) + "/"
