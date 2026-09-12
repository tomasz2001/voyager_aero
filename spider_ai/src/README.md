# Spider AI

Spider AI is a local web-crawler and compatibility checker designed to discover and validate pages that match a specific internal protocol pattern.

The application is built to:

- crawl public and Tor-backed sites
- inspect links and resource pages
- validate whether pages match the expected compatibility signal
- evaluate whether a page is a valid `/5@` endpoint candidate
- use Ollama for AI-based matching

---

## Requirements

Before running the app, make sure the following are available:

- Python 3.10+
- Ollama installed and running locally
- Optional but recommended: Tor installed and running locally for `.onion` support

---

## Install dependencies

From the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install requests beautifulsoup4 rich "requests[socks]"
```

The launcher script will also try to install missing dependencies automatically if possible.

---

## Ollama setup

Spider AI works through Ollama. The model must be downloaded and available locally.

Check whether Ollama is running:

```bash
curl http://127.0.0.1:11434/api/tags
```

If it is not working, start Ollama:

```bash
ollama serve
```

Then pull the model configured in the app:

```bash
ollama pull gemma4:31b-cloud
```

If you changed the model in [config.ini](config.ini), then pull that model instead.

Important:

- Spider AI does not work correctly if the model is missing
- the configured model must be available in Ollama locally
- if the model is not downloaded, requests to Ollama will fail

---

## Tor setup

For `.onion` support, Tor must be running locally and exposing SOCKS on port `9050`.

Check Tor:

```bash
nc -z 127.0.0.1 9050
```

If Tor is not installed, install it and run it.

Typical Linux installation:

```bash
sudo apt-get update
sudo apt-get install -y tor
```

Then start it:

```bash
tor
```

---

## Configuration file

The app reads its user settings from [config.ini](config.ini).

Current default content looks like this:

```ini
[spider]
ollama_model = gemma4:31b-cloud
max_depth = 3
```

You can update this file manually if needed.

---

## Launching the application

The easiest way is to use the launcher script:

```bash
chmod +x spider.sh
./spider.sh
```

You can also launch directly:

```bash
python3 main.py
```

If you want to run a direct query without the setup screen:

```bash
python3 main.py "small cats"
```

---

## Typical startup checklist

Before using Spider AI, verify:

- [ ] Python is installed
- [ ] Ollama is installed and running
- [ ] the required model is downloaded with `ollama pull ...`
- [ ] your model name matches the value in [config.ini](config.ini)
- [ ] Tor is running if you want `.onion` page support

---

## Notes

Spider AI is not a general-purpose web search engine in the Google sense. It is a targeted compatibility crawler built around a specific protocol pattern and validation rules.

The app is designed to work correctly only when:

- the target model in Ollama is present and working
- the configured compatibility rules match the target environment
- the runtime environment is properly set up

---

## Troubleshooting

### Ollama connection fails

Check:

```bash
curl http://127.0.0.1:11434/api/tags
```

If this fails:

```bash
ollama serve
```

### Tor connection fails

Check whether Tor is listening on port 9050:

```bash
nc -z 127.0.0.1 9050
```

If not, start Tor manually.

### Model not found

Run:

```bash
ollama pull gemma4:31b-cloud
```

or the model configured in [config.ini](config.ini).

---

## Example valid endpoint for the Voyager-Aero ecosystem

This is an example of the kind of page the crawler should recognize as a valid compatible endpoint:

```html
<!doctype html>
<html lang='5@'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1.0' />
  <title>scrow.fyi</title>
  <link rel='icon' type='image/png' href='/logo.png' />
</head>
<body>
  <a href='http://zqktqfoeepjarikwyaw2j5f7rscyeb7bx62a2u2o2ajmxcl46c7xeiid.onion/'> dark web hidden wiki </a>
</body>
</html>
```

The important compatibility signal is:

```html
<html lang='5@'>
```

This is the marker that tells the crawler the page belongs to the expected ecosystem and is not a random or unrelated page.
