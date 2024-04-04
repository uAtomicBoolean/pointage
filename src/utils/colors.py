RED = "\033[91m"
GREEN = "\033[92m"
BOLD = "\033[1m"
RES = "\033[0m"

def red(text: str) -> str:
    return f"{RED}{text}{RES}"

def green(text: str) -> str:
    return f"{GREEN}{text}{RES}"

def bold(text: str) -> str:
    return f"{BOLD}{text}{RES}"
