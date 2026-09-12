import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import re
import time


# ============================================================
# KONFIGURACJA
# ============================================================

START_URL = "https://scrow.fyi/5@"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"

MAX_DEPTH = 2
REQUEST_TIMEOUT = 10

HEADERS = {
    "User-Agent": "SpiderAI/1.0"
}


# ============================================================
# OLLAMA
# ============================================================

def ask_ollama(user_query, link_text, link_url):
    """
    Asks Ollama whether a given link may match the user's needs.
    """

    prompt = f"""
You are a web link classifier.

The user is looking for:
"{user_query}"

Found link:

Link text:
"{link_text}"

Address:
"{link_url}"

Evaluate whether this link MAY lead to information
needed by the user.

Respond with ONLY valid JSON:

{{
    "match": true,
    "reason": "short explanation"
}}

or:

{{
    "match": false,
    "reason": "short explanation"
}}

Do not add any text outside the JSON.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        answer = result.get("response", "").strip()

        # Ollama czasami zwraca ```json ... ```
        answer = re.sub(r"```json|```", "", answer).strip()

        return json.loads(answer)

    except Exception as e:
        print(f"[OLLAMA ERROR] {e}")

        return {
            "match": False,
            "reason": "Nie udało się skontaktować z Ollamą."
        }


# ============================================================
# POBIERANIE STRONY
# ============================================================

def get_page(url):
    """
    Pobiera stronę i zwraca BeautifulSoup.
    """

    try:
        print(f"\n[Fetching] {url}")

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code != 200:
            print(
                f"[HTTP {response.status_code}] "
                f"{url}"
            )

            return None

        # Sprawdzamy czy mamy HTML
        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        if "html" not in content_type:
            print("[SKIP] This is not HTML.")

            return None

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        return soup

    except requests.RequestException as e:
        print(f"[REQUEST ERROR] {e}")

        return None


# ============================================================
# SPRAWDZANIE CZY /VA ISTNIEJE
# ============================================================

def get_va_url(url):
    """
    Tworzy adres /5@ dla danej domeny.

    Przykład:

    https://example.com/test
    ->
    https://example.com/5@
    """

    parsed = urlparse(url)

    if not parsed.scheme or not parsed.netloc:
        return None

    return f"{parsed.scheme}://{parsed.netloc}/5@"


def va_exists(url):
    """
    Sprawdza czy /5@ działa.
    """

    va_url = get_va_url(url)

    if not va_url:
        return False

    try:
        response = requests.get(
            va_url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code != 200:
            return False

        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        if "html" not in content_type:
            return False

        return True

    except requests.RequestException:
        return False


# ============================================================
# WYCIĄGANIE LINKÓW
# ============================================================

def extract_links(soup, base_url):
    """
    Wyciąga wszystkie linki <a href=""> oraz <a href=''>.
    """

    links = []

    if not soup:
        return links

    for a in soup.find_all("a", href=True):

        href = a.get("href")

        if href is None:
            raw_tag = str(a)
            match = re.search(
                r'href=(?:["\'])(.*?)(?:["\'])',
                raw_tag,
                flags=re.IGNORECASE | re.DOTALL
            )
            href = match.group(1).strip() if match else ""

        href = str(href).strip()

        if not href:
            continue

        # Pomijamy:
        # javascript:
        # mailto:
        # tel:
        if href.startswith("javascript:"):
            continue

        if href.startswith("mailto:"):
            continue

        if href.startswith("tel:"):
            continue

        # Zamiana względnego URL na pełny
        full_url = urljoin(
            base_url,
            href
        )

        # Usuwamy fragment #...
        full_url = full_url.split("#")[0]

        text = a.get_text(
            " ",
            strip=True
        )

        links.append({
            "url": full_url,
            "text": text
        })

    return links


# ============================================================
# SPRAWDZANIE LINKÓW
# ============================================================

def search_links(
    soup,
    current_url,
    user_query
):
    """
    Sprawdza każdy link przy pomocy Ollamy.

    Jeśli Ollama uzna, że link pasuje,
    pytamy użytkownika.
    """

    links = extract_links(
        soup,
        current_url
    )

    print(
        f"[INFO] Found {len(links)} links."
    )

    for link in links:

        link_url = link["url"]
        link_text = link["text"]

        print(
            f"\n[Analyzing] "
            f"{link_text or '(no text)'}"
        )

        result = ask_ollama(
            user_query,
            link_text,
            link_url
        )

        if result.get("match") is True:

            print("\n================================")
            print("POSSIBLE MATCH")
            print("================================")

            print(
                f"Text: {link_text}"
            )

            print(
                f"URL: {link_url}"
            )

            print(
                f"Reason: {result.get('reason')}"
            )

            print("================================")

            answer = input(
                "Is this what you're looking for? [y/n]: "
            ).strip().lower()

            if answer in ("t", "tak", "y", "yes"):

                print(
                    "\nFOUND:"
                )

                print(link_url)

                return link_url

            print(
                "[NO] Continuing the search..."
            )

    return None


# ============================================================
# SPIDER
# ============================================================

def spider(
    start_url,
    user_query
):

    visited = set()

    queue = [
        (start_url, 0)
    ]

    while queue:

        current_url, depth = queue.pop(0)

        if current_url in visited:
            continue

        if depth > MAX_DEPTH:
            continue

        visited.add(current_url)

        print("\n")
        print("================================")
        print(f"DEPTH: {depth}")
        print(f"URL: {current_url}")
        print("================================")

        soup = get_page(
            current_url
        )

        if not soup:
            continue

        # ----------------------------------------------------
        # 1. SZUKAMY W AKTUALNEJ STRONIE
        # ----------------------------------------------------

        result = search_links(
            soup,
            current_url,
            user_query
        )

        if result:
            return result

        # ----------------------------------------------------
        # 2. NIE ZNALEŹLIŚMY
        #
        # Szukamy stron, do których można wejść
        # i następnie sprawdzić ich /5@
        # ----------------------------------------------------

        links = extract_links(
            soup,
            current_url
        )

        for link in links:

            target_url = link["url"]

            if target_url in visited:
                continue

            # ------------------------------------------------
            # Sprawdzamy /5@ dla znalezionego adresu
            # ------------------------------------------------

            va_url = get_va_url(
                target_url
            )

            if not va_url:
                continue

            if va_url in visited:
                continue

            print(
                f"\n[CHECK /va] {va_url}"
            )

            if va_exists(target_url):

                print(
                    f"[OK] /va exists: "
                    f"{va_url}"
                )

                queue.append(
                    (
                        va_url,
                        depth + 1
                    )
                )

            else:

                print(
                    f"[NO /va] "
                    f"{target_url}"
                )

    return None


# ============================================================
# PROGRAM
# ============================================================

def main():

    print("================================")
    print("        SPIDER AI")
    print("================================")

    user_query = input(
        "\nWhat are you looking for?\n> "
    ).strip()

    if not user_query:

        print(
            "No query was provided."
        )

        return

    print(
        "\nStarting the search..."
    )

    result = spider(
        START_URL,
        user_query
    )

    print("\n")
    print("================================")

    if result:

        print(
            "FOUND:"
        )

        print(result)

    else:

        print(
            "No answer found."
        )

    print("================================")


if __name__ == "__main__":
    main()

