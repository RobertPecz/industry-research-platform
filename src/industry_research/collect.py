import io
import json
import re
import sqlite3
import time
from collections.abc import Callable
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader

from .db import store

USER_AGENT = "IndustryResearchPilot/0.1"


def extract(content: bytes, content_type: str) -> tuple[str, str]:
    if "pdf" in content_type:
        return "PDF", "\n".join(
            page.extract_text() or "" for page in PdfReader(io.BytesIO(content)).pages
        )
    soup = BeautifulSoup(content, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else "Ismeretlen cím"
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return title, (soup.find("main") or soup.find("article") or soup).get_text(
        " ", strip=True
    )


def collect(
    db: sqlite3.Connection,
    sources: list[dict],
    limit: int,
    sleep: Callable[[float], None] | None = None,
) -> dict[str, int]:
    if limit < 1:
        raise ValueError("A limit pozitív legyen")
    pause = sleep or time.sleep
    counts: dict[str, int] = {}
    attempted = 0
    halted_hosts: set[str] = set()
    robots_cache: dict[str, RobotFileParser] = {}
    with httpx.Client(
        timeout=25, headers={"User-Agent": USER_AGENT}, follow_redirects=False
    ) as client:
        for source in sources:
            for url in source.get("urls", []):
                if attempted >= limit:
                    return counts
                attempted += 1
                status, error = "blocked", ""
                try:
                    if source["status"] != "allowed":
                        raise ValueError("A forrás gyűjtési engedélye nem tisztázott")
                    root = urlsplit(url)
                    if root.netloc in halted_hosts:
                        raise ValueError(
                            "A domain lekérései korábbi HTTP-hiba miatt halasztva"
                        )
                    if root.netloc not in robots_cache:
                        robots = client.get(f"{root.scheme}://{root.netloc}/robots.txt")
                        parser = RobotFileParser()
                        if robots.status_code == 404:
                            parser.parse(["User-agent: *", "Allow: /"])
                        else:
                            robots.raise_for_status()
                            parser.parse(robots.text.splitlines())
                        robots_cache[root.netloc] = parser
                    parser = robots_cache[root.netloc]
                    if not parser.can_fetch(USER_AGENT, url):
                        raise ValueError("robots.txt tiltás")
                    pause(max(2, int(parser.crawl_delay(USER_AGENT) or 0)))
                    response = client.get(url)
                    if response.status_code in {403, 429, 503}:
                        halted_hosts.add(root.netloc)
                    response.raise_for_status()
                    title, text = extract(
                        response.content, response.headers.get("content-type", "")
                    )
                    if len(text.strip()) < 30:
                        raise ValueError("Üres vagy túl rövid tartalom")
                    if (
                        source.get("required_text")
                        and source["required_text"].lower() not in text.lower()
                    ):
                        raise ValueError("A dokumentum relevanciája nem igazolt")
                    status = store(
                        db,
                        url,
                        source["name"],
                        title,
                        text[: source.get("max_chars", 500)],
                    )
                    match = re.search(r"Közzététel: (\d{4})\. (\w+) (\d{1,2})\.", text)
                    months = "január február március április május június július augusztus szeptember október november december".split()
                    if match and match[2] in months:
                        published = f"{match[1]}-{months.index(match[2]) + 1:02}-{int(match[3]):02}"
                        with db:
                            db.execute(
                                "UPDATE documents SET published=? WHERE url=?",
                                (published, url),
                            )
                except Exception as exc:
                    error = f"{type(exc).__name__}: {exc}"
                    if not isinstance(exc, ValueError):
                        status = "error"
                with db:
                    db.execute(
                        "INSERT INTO attempts(url,status,error) VALUES(?,?,?)",
                        (url, status, error),
                    )
                counts[status] = counts.get(status, 0) + 1
                print(
                    json.dumps(
                        {
                            "event": "fetch",
                            "url": url,
                            "status": status,
                            "error": error,
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
                if counts.get("stored", 0) >= limit:
                    return counts
    return counts
