#!/usr/bin/env python3
"""Generate event-specific social pages and host public event posters on GitHub Pages.

Only events/<id>/ is written. Existing pages and links are preserved.
"""

import html
import json
import os
import pathlib
import re
import urllib.parse
import urllib.request

API = os.environ.get(
    "EVENT_API_URL",
    "https://script.google.com/macros/s/AKfycbzq4EDX6gfB20LN0F071kj2ysbCUX-PETlIlzF7y0dbwIW7WBO23m7vy6xTlB189g4wuQ/exec",
)
BASE = "https://nckageshwori1.github.io/members/"
ROOT = pathlib.Path("events")
MAX_IMAGE_BYTES = 8 * 1024 * 1024


def escape(value):
    return html.escape(str(value), quote=True)


def download_poster(url, destination):
    """Return a public filename only when actual supported image bytes are obtained."""
    if not url.startswith("https://"):
        return None

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; EventPreviewPublisher/1.1)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            content_type = response.headers.get("Content-Type", "").split(";", 1)[0].lower()
            data = response.read(MAX_IMAGE_BYTES + 1)

        if len(data) > MAX_IMAGE_BYTES:
            raise ValueError("Poster is larger than 8 MB")

        # Verify file signatures, not merely the response Content-Type.
        if data.startswith(b"\xff\xd8\xff"):
            extension = "jpg"
        elif data.startswith(b"\x89PNG\r\n\x1a\n"):
            extension = "png"
        elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            extension = "webp"
        else:
            raise ValueError(f"Response is not a supported image ({content_type})")

        filename = f"poster.{extension}"
        (destination / filename).write_bytes(data)
        for old in destination.glob("poster.*"):
            if old.name != filename:
                old.unlink()
        return filename
    except Exception as error:
        print(f"WARNING: Could not publish poster from {url}: {error}")
        # Preserve a previously published photo if this run cannot fetch a new one.
        for extension in ("jpg", "png", "webp"):
            filename = f"poster.{extension}"
            if (destination / filename).is_file():
                return filename
        return None


def render_page(title, description, page_url, detail_url, image_url):
    image_tags = ""
    if image_url:
        image_tags = f"""
    <meta property="og:image" content="{escape(image_url)}">
    <meta property="og:image:secure_url" content="{escape(image_url)}">
    <meta name="twitter:image" content="{escape(image_url)}">"""

    # No immediate meta refresh: some social crawlers follow it before reading OG tags.
    # Normal visitors are redirected by JavaScript, with a no-JS fallback link.
    return f"""<!DOCTYPE html>
<html lang="ne">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)}</title>
    <meta name="description" content="{escape(description)}">

    <!-- Social media preview metadata -->
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="नेपाली कांग्रेस वडा नं. १">
    <meta property="og:title" content="{escape(title)}">
    <meta property="og:description" content="{escape(description)}">
    <meta property="og:url" content="{escape(page_url)}">{image_tags}
    <meta name="twitter:card" content="summary_large_image">
    <link rel="canonical" href="{escape(page_url)}">
</head>
<body>
    <main>
        <p>कार्यक्रमको पूरा विवरण खोलिँदैछ...</p>
        <p><a href="{escape(detail_url)}">{escape(title)} — विवरण हेर्नुहोस्</a></p>
    </main>
    <script>
        window.location.replace({json.dumps(detail_url, ensure_ascii=False)});
    </script>
</body>
</html>
"""


def main():
    request = urllib.request.Request(
        API,
        data=json.dumps({"action": "publicHome"}).encode("utf-8"),
        headers={"Content-Type": "text/plain;charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = json.load(response)

    if not payload.get("ok") or not isinstance(payload.get("notices"), list):
        raise RuntimeError("Public notices API returned invalid data")

    ROOT.mkdir(exist_ok=True)
    count = 0
    photo_count = 0

    for notice in payload["notices"]:
        event_id = str(notice.get("ID", "")).strip()
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,100}", event_id):
            continue

        title = str(notice.get("शीर्षक") or "कार्यक्रम सूचना").strip()[:180]
        summary = " • ".join(
            str(notice.get(key, "")).strip()
            for key in ("मिति", "समय", "स्थान")
            if notice.get(key)
        )
        description = (summary + " — " + str(notice.get("विवरण") or "")).strip(" —")[:280]
        detail_url = BASE + "event.html?id=" + urllib.parse.quote(event_id, safe="")
        page_url = BASE + "events/" + urllib.parse.quote(event_id, safe="") + "/"

        destination = ROOT / event_id
        destination.mkdir(parents=True, exist_ok=True)
        poster = download_poster(str(notice.get("ImageURL") or ""), destination)
        image_url = page_url + poster if poster else ""
        if poster:
            photo_count += 1
        else:
            print(f"WARNING: No public poster for event {event_id}; preview may be text-only")

        (destination / "index.html").write_text(
            render_page(title, description, page_url, detail_url, image_url),
            encoding="utf-8",
        )
        count += 1

    print(f"Generated {count} event pages; {photo_count} with GitHub-hosted posters")


if __name__ == "__main__":
    main()
