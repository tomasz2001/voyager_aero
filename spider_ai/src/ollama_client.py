import json
import re
import requests

from config import (
    OLLAMA_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT
)


def analyze_links(user_query, links):

    if not links:
        return []


    resources = []

    for index, link in enumerate(links):

        resources.append(
            f"""
[{index}]

Opis:
{link["text"]}

URL:
{link["url"]}
"""
        )

    resources_text = "\n".join(resources)


    prompt = f"""
You are the Spider AI search engine.

The user is looking for:

"{user_query}"


You have a list of resources found on the page.

The text between <a>...</a> is the description of
what is available at that address.

Your task is to find ALL resources that may match
the user's needs.

Do not require identical words.

Consider meaning, synonyms, and context.

If a resource is not relevant to the query,
do not select it.

Resources:

{resources_text}


Respond ONLY with valid JSON in the following format:

{{
    "matches": [
        {{
            "index": 0,
            "reason": "why the resource matches"
        }}
    ]
}}

If nothing matches:

{{
    "matches": []
}}
"""


    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=OLLAMA_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        answer = data.get(
            "response",
            ""
        ).strip()


        # Usuwamy ewentualne markdownowe ```json
        answer = re.sub(
            r"```json\s*",
            "",
            answer
        )

        answer = re.sub(
            r"```\s*",
            "",
            answer
        )

        result = json.loads(answer)

        return result.get(
            "matches",
            []
        )


    except Exception:

        return []
