import sys

import config
from crawler import Spider
from analyzer import find_matches
from config import DEFAULT_QUERY, DEFAULT_OLLAMA_MODEL, DEFAULT_MAX_DEPTH

import ui


def main():

    ui.clear()

    ui.show_logo()

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:]).strip()
    else:
        model, max_depth, start_url = ui.show_startup_config(
            config.OLLAMA_MODEL,
            config.MAX_DEPTH,
            config.START_URL
        )

        config.OLLAMA_MODEL = model
        config.MAX_DEPTH = max_depth
        # Normalizujemy w main: usuń ewentualny '/5@' i końcowy '/'
        s = start_url.strip()
        if s.endswith("/5@"):
            s = s[:-3]
        s = s.rstrip("/")
        config.START_URL = s
        config.save_config()

        try:
            import ollama_client
            ollama_client.OLLAMA_MODEL = model
        except Exception:
            pass

        ui.status(
            "Configuration saved to config.ini. Exiting for the next run."
        )
        return

    if not query:
        return


    # Dopisujemy '/5@' w runtime — nie zapisujemy tej części w konfiguracji
    start_with_va = config.START_URL.rstrip("/") + "/5@"
    spider = Spider(
        start_with_va
    )

    spider.start()


    results_count = 0

    try:

        while True:

            page = spider.next_page()

            if page is None:
                break


            url, depth = page


            with ui.searching("Searching..."):
                soup = spider.visit(
                    url
                )

            if soup is None:

                ui.status(
                    "Page skipped."
                )

                continue


            links = spider.extract_links(
                soup,
                url
            )


            if not links:

                #ui.status(
                #    "No links found on this page."
                #)

                continue


            ui.status(
                f"Reviewing {len(links)} candidates..."
            )


            matches = find_matches(
                query,
                links,
                spider.found_urls
            )


            # -------------------------------------------------
            # WYNIKI
            # -------------------------------------------------

            for match in matches:

                results_count += 1

                ui.result(
                    match
                )


            # -------------------------------------------------
            # SZUKAMY KOLEJNYCH /va
            # -------------------------------------------------

            for link in links:

                target = link["url"]


                if target in spider.visited:
                    continue


                va_url = spider.check_va(
                    target
                )


                if va_url:

                    spider.add_to_queue(
                        va_url,
                        depth + 1
                    )


    except KeyboardInterrupt:

        ui.stopped()

        return


    ui.finished(
        results_count
    )


if __name__ == "__main__":

    main()
