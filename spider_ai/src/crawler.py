import re
import requests

from bs4 import BeautifulSoup
from urllib.parse import (
    urljoin,
    urlparse
)

from config import (
    REQUEST_TIMEOUT,
    USER_AGENT,
    MAX_DEPTH,
    TOR_SOCKS_PROXY
)


HEADERS = {
    "User-Agent": USER_AGENT
}


class Spider:

    def __init__(self, start_url):

        self.start_url = start_url

        self.visited = set()

        self.queue = []

        self.found_urls = set()

    @staticmethod
    def is_onion_url(url):

        host = urlparse(url).hostname or ""
        return host.endswith(".onion")

    @staticmethod
    def build_session(url):

        session = requests.Session()
        session.headers.update(HEADERS)

        if Spider.is_onion_url(url):
            try:
                session.proxies.update({
                    "http": TOR_SOCKS_PROXY,
                    "https": TOR_SOCKS_PROXY
                })
            except Exception:
                pass

        return session

    @staticmethod
    def is_compatible_five_at_page(response):

        if response is None:
            return False

        if response.status_code != 200:
            return False

        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        if "html" not in content_type:
            return False

        try:
            text = response.text or ""
        except Exception:
            return False

        try:
            soup = BeautifulSoup(
                text,
                "html.parser"
            )
        except Exception:
            return False

        html_tag = soup.find("html")
        if html_tag is None:
            return False

        lang = html_tag.get("lang")
        if lang is None:
            return False

        normalized = str(lang).strip().lower()

        return normalized in ("5@", "5%40")


    # ---------------------------------------------------------
    # POBIERANIE STRONY
    # ---------------------------------------------------------

    def get_page(self, url):

        try:

            session = self.build_session(url)
            response = session.get(
                url,
                timeout=REQUEST_TIMEOUT
            )

            if response.status_code != 200:
                return None

            content_type = response.headers.get(
                "Content-Type",
                ""
            ).lower()

            if "html" not in content_type:
                return None

            return BeautifulSoup(
                response.text,
                "html.parser"
            )

        except requests.RequestException:

            return None


    # ---------------------------------------------------------
    # LINK TAGS
    # ---------------------------------------------------------

    def extract_links(
        self,
        soup,
        base_url
    ):

        links = []

        for tag in soup.find_all(
            "a",
            href=True
        ):

            href = tag.get("href")

            if href is None:
                raw_tag = str(tag)
                match = re.search(
                    r'href=(?:["\'])(.*?)(?:["\'])',
                    raw_tag,
                    flags=re.IGNORECASE | re.DOTALL
                )
                href = match.group(1).strip() if match else ""

            href = str(href).strip()

            if not href:
                continue


            # Pomijamy nie-webowe linki

            if href.startswith(
                (
                    "javascript:",
                    "mailto:",
                    "tel:",
                    "#"
                )
            ):
                continue


            url = urljoin(
                base_url,
                href
            )

            # Usuwamy #fragment

            url = url.split("#")[0]


            parsed = urlparse(url)

            if parsed.scheme not in (
                "http",
                "https"
            ):
                continue


            text = tag.get_text(
                " ",
                strip=True
            )


            # Link bez opisu nie jest dla nas
            # szczególnie interesujący.

            if not text:
                continue


            links.append({
                "url": url,
                "text": text
            })


        return links


    # ---------------------------------------------------------
    # TWORZENIE /va
    # ---------------------------------------------------------

    def get_va_url(self, url):

        parsed = urlparse(url)

        if not parsed.netloc:
            return None

        return (
            f"{parsed.scheme}://"
            f"{parsed.netloc}/5@"
        )


    # ---------------------------------------------------------
    # SPRAWDZANIE /va
    # ---------------------------------------------------------

    def check_va(self, url):

        va_url = self.get_va_url(url)

        if not va_url:
            return None


        if va_url in self.visited:
            return None


        try:

            session = self.build_session(va_url)
            response = session.get(
                va_url,
                timeout=REQUEST_TIMEOUT
            )

            if not self.is_compatible_five_at_page(response):
                return None

            return va_url


        except requests.RequestException:

            return None


    # ---------------------------------------------------------
    # DODAJ DO KOLEJKI
    # ---------------------------------------------------------

    def add_to_queue(
        self,
        url,
        depth
    ):

        if depth > MAX_DEPTH:
            return

        if url in self.visited:
            return

        if any(
            item[0] == url
            for item in self.queue
        ):
            return

        self.queue.append(
            (
                url,
                depth
            )
        )


    # ---------------------------------------------------------
    # START
    # ---------------------------------------------------------

    def start(self):

        self.add_to_queue(
            self.start_url,
            0
        )


    # ---------------------------------------------------------
    # NASTĘPNA STRONA
    # ---------------------------------------------------------

    def next_page(self):

        if not self.queue:
            return None

        return self.queue.pop(0)


    # ---------------------------------------------------------
    # ODWIEDŹ STRONĘ
    # ---------------------------------------------------------

    def visit(
        self,
        url
    ):

        if url in self.visited:
            return None

        self.visited.add(url)

        return self.get_page(url)
