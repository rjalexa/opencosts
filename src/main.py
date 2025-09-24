from __future__ import annotations

import concurrent.futures as cf
from dataclasses import dataclass
from typing import Iterable, List, Dict, Any
import requests
from urllib.parse import quote
import os
import re
from bs4 import BeautifulSoup

BASE = "https://openrouter.ai"
LIST_MODELS_URL = f"{BASE}/api/v1/models"


def _load_search_terms() -> List[str]:
    """Load search terms from model_strings.txt file"""
    try:
        with open("data/input/models_strings.txt", "r") as f:
            terms = [line.strip() for line in f if line.strip()]
            return terms
    except FileNotFoundError:
        print(
            "Warning: data/input/models_strings.txt not found, using default search terms"
        )
        return [
            "Gemini 2.5",
            "Sonnet 4",
            "Opus 4",
            "Kimi K2",
            "Deepseek R1",
        ]


# ---- data structures ----
@dataclass(frozen=True)
class ModelHit:
    name: str
    model_id: str
    canonical_slug: str
    creation_date: str | None = None

    @property
    def url(self) -> str:
        # Build website URL from canonical_slug.
        # Encode the path segment after the first '/' to be safe if a ':' ever appears.
        author, slug = self.canonical_slug.split("/", 1)
        return f"{BASE}/{author}/{quote(slug, safe='')}"


@dataclass(frozen=True)
class ProviderRow:
    model_name: str
    model_url: str
    model_id: str
    provider: str
    context_length: int | None
    price_input_token: str | None
    price_output_token: str | None
    latency: float | None  # not currently available via API
    throughput: float | None  # not currently available via API
    creation_date: str | None = None


# ---- helpers ----
def _fetch_json(url: str) -> Dict[str, Any]:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def _list_models() -> List[Dict[str, Any]]:
    return _fetch_json(LIST_MODELS_URL)["data"]


def _is_free(model: Dict[str, Any]) -> bool:
    name = (model.get("name") or "").lower()
    mid = (model.get("id") or "").lower()
    return ":free" in mid or "(free" in name


def _name_matches(name: str, needles: Iterable[str]) -> bool:
    name_lower = name.lower()
    return any(n.lower() in name_lower for n in needles)


def _list_endpoints(canonical_slug: str) -> List[Dict[str, Any]]:
    # API path uses author/slug as-is (colons allowed if present).
    url = f"{BASE}/api/v1/models/{canonical_slug}/endpoints"
    return _fetch_json(url)["data"]["endpoints"]


def _fetch_creation_date(canonical_slug: str) -> str | None:
    """Fetch the creation date from a model's detail page."""
    try:
        # Build the model detail page URL
        author, slug = canonical_slug.split("/", 1)
        url = f"{BASE}/{author}/{quote(slug, safe='')}"
        
        # Fetch the HTML page
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse HTML to find the creation date
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for text containing "Created "
        # The pattern is: "Created Sep 23, 2025"
        text = soup.get_text()
        match = re.search(r'Created\s+([A-Za-z]{3}\s+\d{1,2},\s+\d{4})', text)
        
        if match:
            return match.group(1)  # Return just the date part (e.g., "Sep 23, 2025")
        
        return None
    except Exception as e:
        print(f"Warning: Could not fetch creation date for {canonical_slug}: {e}")
        return None


# ---- main API ----
def find_models_by_name_parts(parts: Iterable[str]) -> List[ModelHit]:
    hits: List[ModelHit] = []
    for m in _list_models():
        if _is_free(m):
            continue
        if not _name_matches(m.get("name", ""), parts):
            continue
        slug = m.get("canonical_slug") or m["id"].split(":")[0]
        hits.append(ModelHit(name=m["name"], model_id=m["id"], canonical_slug=slug))
    
    # optional: de‑dupe by model_id
    seen = set()
    unique = []
    for h in hits:
        if h.model_id in seen:
            continue
        seen.add(h.model_id)
        unique.append(h)
    
    # Fetch creation dates for all unique models
    def fetch_creation_date_for_model(model_hit: ModelHit) -> ModelHit:
        creation_date = _fetch_creation_date(model_hit.canonical_slug)
        return ModelHit(
            name=model_hit.name,
            model_id=model_hit.model_id,
            canonical_slug=model_hit.canonical_slug,
            creation_date=creation_date
        )
    
    # Use threading to fetch creation dates in parallel
    with cf.ThreadPoolExecutor(max_workers=8) as pool:
        unique_with_dates = list(pool.map(fetch_creation_date_for_model, unique))
    
    return unique_with_dates


def expand_providers(models: Iterable[ModelHit]) -> List[ProviderRow]:
    rows: List[ProviderRow] = []

    def work(h: ModelHit) -> List[ProviderRow]:
        out: List[ProviderRow] = []
        for ep in _list_endpoints(h.canonical_slug):
            pricing = ep.get("pricing", {}) or {}
            # context length can be either 'context_length' or 'max_prompt_tokens'
            ctx = ep.get("context_length") or ep.get("max_prompt_tokens")
            provider_name = ep.get("provider_name")
            if provider_name:
                out.append(
                    ProviderRow(
                        model_name=h.name,
                        model_url=h.url,
                        model_id=h.model_id,
                        provider=provider_name,
                        context_length=int(ctx)
                        if isinstance(ctx, (int, float))
                        else (
                            int(ctx) if isinstance(ctx, str) and ctx.isdigit() else None
                        ),
                        price_input_token=pricing.get("prompt"),
                        price_output_token=pricing.get("completion"),
                        # These are not in the documented API as of 2025‑07‑26; leave None.
                        latency=ep.get("latency") if "latency" in ep else None,
                        throughput=ep.get("throughput") if "throughput" in ep else None,
                        creation_date=h.creation_date,
                    )
                )
        return out

    with cf.ThreadPoolExecutor(max_workers=8) as pool:
        for batch in pool.map(work, models):
            rows.extend(batch)
    return rows


if __name__ == "__main__":
    SUBSTRINGS = _load_search_terms()
    models = find_models_by_name_parts(SUBSTRINGS)
    rows = expand_providers(models)

    # Print a compact report
    from textwrap import shorten

    print(f"Found {len(models)} matching models; emitting {len(rows)} provider rows.\n")
    for r in rows:
        print(
            f"{shorten(r.model_name, 60)} | {r.provider:>12} | ctx={r.context_length} | "
            f"in={r.price_input_token} | out={r.price_output_token} | "
            f"lat={r.latency} | tps={r.throughput} | {r.model_url}"
        )

    # Optional: write CSV
    import csv

    output_dir = "frontend/public"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "openrouter_models_providers.csv")
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "Model name",
                "Model URL",
                "OpenRouter model ID",
                "Provider",
                "Context length",
                "Price/input token",
                "Price/output token",
                "Latency",
                "Throughput",
                "Creation date",
            ]
        )
        for r in rows:
            w.writerow(
                [
                    r.model_name,
                    r.model_url,
                    r.model_id,
                    r.provider,
                    r.context_length,
                    r.price_input_token,
                    r.price_output_token,
                    r.latency,
                    r.throughput,
                    r.creation_date,
                ]
            )
