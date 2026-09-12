from pathlib import Path

# Domyślne wartości konfiguracyjne (natywne)
# Przechowujemy bazowy adres bez dopisku /5@ — dopisek dodawany jest runtime'owo
DEFAULT_START_URL = "https://scrow.fyi"
START_URL = DEFAULT_START_URL
DEFAULT_QUERY = "small cats"
DEFAULT_OLLAMA_MODEL = "gemma4:31b-cloud"
DEFAULT_MAX_DEPTH = 3

CONFIG_PATH = Path(__file__).with_name("config.ini")

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = DEFAULT_OLLAMA_MODEL

REQUEST_TIMEOUT = 10
OLLAMA_TIMEOUT = 180

# Tor proxy for .onion pages.
# If Tor is not running locally, normal HTTP pages still work.
TOR_SOCKS_PROXY = "socks5h://127.0.0.1:9050"

# Maksymalna liczba poziomów:
#
# /5@
#   └── znaleziony-link/5@
#         └── kolejny-link/5@
#
MAX_DEPTH = DEFAULT_MAX_DEPTH

USER_AGENT = "SpiderAI/1.0"


def load_config():

    global OLLAMA_MODEL, MAX_DEPTH, START_URL

    if not CONFIG_PATH.exists():
        save_config()
        return

    try:
        content = CONFIG_PATH.read_text(encoding="utf-8")
    except OSError:
        return

    values = {}
    current_section = None

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1].strip().lower()
            continue
        if "=" not in line:
            continue
        key, value = [part.strip() for part in line.split("=", 1)]
        if current_section:
            values[(current_section, key.lower())] = value

    if ("spider", "ollama_model") in values:
        OLLAMA_MODEL = values[("spider", "ollama_model")]
    if ("spider", "max_depth") in values:
        try:
            MAX_DEPTH = int(values[("spider", "max_depth")])
        except ValueError:
            MAX_DEPTH = DEFAULT_MAX_DEPTH
    if ("spider", "start_url") in values:
        # Usuń ewentualny dopisek '/5@' jeśli użytkownik go podał
        raw = values[("spider", "start_url")].strip()
        if raw.endswith("/5@"):
            raw = raw[:-3]
        START_URL = raw.rstrip("/")


def save_config():

    # Zapisujemy bazowy adres bez '/5@'
    start_to_write = START_URL
    if start_to_write.endswith("/5@"):
        start_to_write = start_to_write[:-3]

    text = (
        "[spider]\n"
        f"start_url = {start_to_write}\n"
        f"ollama_model = {OLLAMA_MODEL}\n"
        f"max_depth = {MAX_DEPTH}\n"
    )

    try:
        CONFIG_PATH.write_text(text, encoding="utf-8")
    except OSError:
        pass


load_config()

