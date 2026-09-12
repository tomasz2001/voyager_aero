from ollama_client import analyze_links


def find_matches(
    user_query,
    links,
    found_urls
):

    matches = analyze_links(
        user_query,
        links
    )

    results = []

    for match in matches:

        index = match.get("index")

        if not isinstance(index, int):
            continue

        if index < 0 or index >= len(links):
            continue

        link = links[index]

        url = link["url"]

        if url in found_urls:
            continue

        found_urls.add(url)

        results.append({
            "url": url,
            "text": link["text"],
            "reason": match.get(
                "reason",
                ""
            )
        })

    return results
