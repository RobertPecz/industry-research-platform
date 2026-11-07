"""Validated, versioned, data-only keyword configuration."""

import hashlib
import json
from pathlib import Path

import yaml


def load_taxonomy(path: str | Path = "config/taxonomy.yaml") -> dict:
    try:
        config = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError("A taxonómia nem olvasható vagy hibás YAML") from exc
    if not isinstance(config, dict) or set(config) != {"version", "industry", "topics"}:
        raise ValueError("Taxonómia: version, industry és topics mezők szükségesek")
    for key in ("version", "industry"):
        if not isinstance(config[key], str) or not config[key].strip():
            raise ValueError(f"A {key} nem üres szöveg legyen")
    topics = config["topics"]
    if not isinstance(topics, dict) or not topics or len(topics) > 100:
        raise ValueError("1–100 téma szükséges")
    for topic, words in topics.items():
        if not isinstance(topic, str) or not topic.strip() or len(topic) > 100:
            raise ValueError("Érvénytelen témanév")
        if not isinstance(words, list) or not words or len(words) > 100:
            raise ValueError("Minden témához 1–100 keresőkifejezés szükséges")
        if any(not isinstance(w, str) or not w.strip() or len(w) > 100 for w in words):
            raise ValueError("A keresőkifejezés 1–100 karakteres szöveg legyen")
    serialized = json.dumps(config, sort_keys=True, ensure_ascii=False)
    return dict(
        config,
        hash=hashlib.sha256(serialized.encode()).hexdigest(),
        serialized=serialized,
    )
