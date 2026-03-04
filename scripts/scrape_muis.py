#!/usr/bin/env python3
"""
Fixed MUIS API scraper - Addresses 200-result API limit bug.

Key fixes:
1. Detects and handles 200-result API cap
2. Increased max_prefix_len default to 6
3. Fixed metadata field names (totalRecords)
4. Better deduplication using ID as primary key
5. Forces prefix splitting when hitting 200-result cap

Usage:
  python3 muis_api_scrape_fixed.py --insecure --out-csv muis_complete.csv
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
import warnings

import pandas as pd
import requests
from requests import Response
import urllib3

# Suppress InsecureRequestWarning when using --insecure flag
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


DEFAULT_OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "muis_complete.csv")
DEFAULT_OUTPUT_JSON = os.path.join(os.path.dirname(__file__), "muis_complete_raw.json")

# SSL verification toggle
VERIFY: bool = os.getenv("MUIS_VERIFY_SSL", "1") != "0"


def coerce_int(value: Optional[str], fallback: int) -> int:
    if value is None:
        return fallback
    try:
        return int(value)
    except ValueError:
        return fallback


def polite_sleep(seconds: float) -> None:
    if seconds > 0:
        time.sleep(seconds)


def get_csrf_token(session: requests.Session, base_page_url: str) -> str:
    """Fetch CSRF token from the base page."""
    resp = session.get(base_page_url, timeout=45, verify=VERIFY)
    resp.raise_for_status()

    token_marker = 'name="__RequestVerificationToken"'
    idx = resp.text.find(token_marker)
    if idx == -1:
        raise RuntimeError("Could not find __RequestVerificationToken on base page")

    val_idx = resp.text.find('value="', idx)
    if val_idx == -1:
        raise RuntimeError("Could not locate token value attribute")
    val_idx += len('value="')

    end_idx = resp.text.find('"', val_idx)
    if end_idx == -1:
        raise RuntimeError("Malformed token input element")

    return resp.text[val_idx:end_idx]


def adaptive_search_mode_harvest_fixed(
    session: requests.Session,
    search_url: str,
    base_page_url: str,
    alphabet: str,
    min_prefix_len: int,
    max_prefix_len: int,
    split_threshold: int,
    seed_terms: Optional[List[str]],
    rate_limit_per_sec: float,
    max_records: Optional[int],
) -> List[Dict[str, Any]]:
    """
    FIXED: Adaptive prefix enumeration with 200-result cap detection.

    Key improvements:
    - Detects when API returns 200 results (hard cap)
    - Forces prefix splitting when cap is hit, even if below split_threshold
    - Uses ID as primary deduplication key
    - Fixed metadata field names
    """
    # Acquire CSRF token and headers once
    token = get_csrf_token(session, base_page_url)
    headers = {
        "Content-Type": "application/json",
        "X-CSRF-TOKEN": token,
        "Referer": base_page_url,
        "Origin": os.path.dirname(base_page_url.rstrip('/')),
        "User-Agent": "HalalFoodLandscape/1.0 (+contact@example.com)",
    }
    sleep_seconds = 1.0 / rate_limit_per_sec if rate_limit_per_sec > 0 else 0.0

    # Prepare queue
    alpha_list = [ch for ch in alphabet]
    queue: List[str] = []
    visited_prefixes: Set[str] = set()
    pad_char = alpha_list[0] if alpha_list else 'a'

    # Seed with explicit terms first
    if seed_terms:
        for s in seed_terms:
            s = s.strip()
            if not s:
                continue
            if len(s) < min_prefix_len:
                s = s + (pad_char * (min_prefix_len - len(s)))
            queue.append(s)

    # Seed with alphabet prefixes
    for ch in alpha_list:
        if min_prefix_len <= 1:
            queue.append(ch)
        else:
            queue.append(ch + (pad_char * (min_prefix_len - 1)))

    all_items: List[Dict[str, Any]] = []
    seen_keys: Set[str] = set()

    # Track statistics
    total_queries = 0
    capped_queries = 0

    def post_and_collect(prefix: str) -> Tuple[List[Dict[str, Any]], bool, int]:
        """
        Fetch results for a prefix and detect if we hit the 200-result cap.

        Returns: (new_items, was_capped, total_returned)
        """
        collected: List[Dict[str, Any]] = []

        payload = {"text": prefix}
        try:
            resp = session.post(search_url, headers=headers, json=payload, timeout=45, verify=VERIFY)
            resp.raise_for_status()
            data = resp.json() or {}
        except Exception as e:
            print(f"  WARNING: Query '{prefix}' failed: {e}", file=sys.stderr)
            return [], False, 0

        items = data.get("data") or []

        # FIXED: Use correct field name 'totalRecords' instead of 'total'
        total_records = data.get("totalRecords", 0)

        # If we get exactly 200 results OR totalRecords says 200 AND we have items, the API likely capped us
        was_capped = (len(items) >= 200) or (total_records >= 200 and len(items) > 0)

        # Collect new items with deduplication
        for it in items:
            # FIXED: Use ID as primary key (UUIDs are more reliable than certificate numbers)
            item_id = str(it.get("id") or "")
            item_name = it.get("name") or ""
            item_address = it.get("address") or ""

            # Create composite key for deduplication
            key = f"{item_id}|{item_name}|{item_address}"

            if key not in seen_keys:
                seen_keys.add(key)
                collected.append(it)

        return collected, was_capped, len(items)

    print("Starting adaptive search with 200-cap detection...", file=sys.stderr)

    while queue:
        prefix = queue.pop(0)

        if prefix in visited_prefixes:
            continue
        visited_prefixes.add(prefix)

        # Ensure minimum query length
        effective_prefix = prefix
        if len(effective_prefix) < min_prefix_len:
            effective_prefix = effective_prefix + (pad_char * (min_prefix_len - len(effective_prefix)))

        total_queries += 1
        new_items, was_capped, total_returned = post_and_collect(effective_prefix)

        if was_capped:
            capped_queries += 1

        # Progress reporting
        if total_queries % 50 == 0:
            print(f"  Progress: {total_queries} queries, {len(all_items)} items, {capped_queries} capped", file=sys.stderr)

        all_items.extend(new_items)

        if max_records is not None and len(all_items) >= max_records:
            print(f"  Reached max_records limit: {max_records}", file=sys.stderr)
            break

        # CRITICAL FIX: Force split if we hit the 200-cap, regardless of split_threshold
        should_split = False

        if was_capped:
            # We hit the API cap - MUST split to get complete coverage
            should_split = True
            reason = "hit 200-cap"
        elif len(new_items) >= split_threshold:
            # Traditional split threshold
            should_split = True
            reason = f"≥{split_threshold} results"

        # Only split if we haven't reached max prefix length
        if should_split and len(prefix) < max_prefix_len:
            # Expand this prefix with all alphabet characters
            for ch in alpha_list:
                child = prefix + ch
                if child not in visited_prefixes:
                    queue.append(child)

            if total_queries % 10 == 0 or was_capped:
                print(f"  '{prefix}': {len(new_items)} items, {reason} → splitting", file=sys.stderr)

        polite_sleep(sleep_seconds)

    print(f"\nCompleted: {total_queries} queries, {len(all_items)} unique items, {capped_queries} capped queries", file=sys.stderr)

    return all_items


def map_item_to_schema(item: Dict[str, Any], source_url: str) -> Dict[str, Any]:
    """Map API response item to standardized schema."""
    # FIXED: API uses 'number' for certificate, not 'certificateNumber'
    name = item.get("name") or ""
    address = item.get("address") or ""
    postal = item.get("postal") or ""
    cert_number = item.get("number") or ""

    record = {
        "source": "muis",
        "place_id": item.get("id") or "",
        "name": name,
        "outlet_name": "",  # Not in API response
        "address": address,
        "postal_code": postal,
        "latitude": "",  # Not in API response
        "longitude": "",  # Not in API response
        "muis_halal_status": "MUIS Halal Certified",
        "cuisine": "",  # Not in API response
        "website": "",  # Not in API response
        "phone": "",  # Not in API response
        "last_scraped": datetime.now(timezone.utc).isoformat(),
        "source_url": source_url,
        "notes": cert_number,
        "certificate_number": cert_number,
        "type": item.get("type", 0),
        "scheme": item.get("scheme", ""),
        "sub_scheme": item.get("subScheme", ""),
    }
    return record


def to_dataframe(records: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert records to pandas DataFrame with standardized columns."""
    columns = [
        "source",
        "place_id",
        "name",
        "outlet_name",
        "address",
        "postal_code",
        "latitude",
        "longitude",
        "muis_halal_status",
        "cuisine",
        "website",
        "phone",
        "last_scraped",
        "source_url",
        "notes",
        "certificate_number",
        "type",
        "scheme",
        "sub_scheme",
    ]
    df = pd.DataFrame(records)

    # Add missing columns
    missing = [c for c in columns if c not in df.columns]
    for c in missing:
        df[c] = None

    return df[columns]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="FIXED MUIS scraper with 200-cap detection.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with defaults
  python3 muis_api_scrape_fixed.py --insecure

  # Custom output location
  python3 muis_api_scrape_fixed.py --insecure --out-csv my_output.csv

  # Faster scraping (careful not to overload server)
  python3 muis_api_scrape_fixed.py --insecure --rate 3

  # Limit total records (for testing)
  python3 muis_api_scrape_fixed.py --insecure --max-records 100
        """
    )

    parser.add_argument("--base-page",
                       default=os.getenv("MUIS_BASE_PAGE", "https://halal.muis.gov.sg/halal/establishments"),
                       help="Base page URL to fetch CSRF token")
    parser.add_argument("--search-url",
                       default=os.getenv("MUIS_SEARCH_URL", "https://halal.muis.gov.sg/api/halal/establishments"),
                       help="Search POST endpoint")
    parser.add_argument("--alphabet",
                       default=os.getenv("MUIS_SEARCH_ALPHABET", "abcdefghijklmnopqrstuvwxyz0123456789"),
                       help="Alphabet for adaptive prefix search")
    parser.add_argument("--min-prefix-len", type=int,
                       default=coerce_int(os.getenv("MUIS_MIN_PREFIX_LEN"), 1),
                       help="Minimum prefix length (default: 1)")
    parser.add_argument("--max-prefix-len", type=int,
                       default=coerce_int(os.getenv("MUIS_MAX_PREFIX_LEN"), 6),  # FIXED: Increased from 4 to 6
                       help="Maximum prefix length (default: 6, increased from 4)")
    parser.add_argument("--split-threshold", type=int,
                       default=coerce_int(os.getenv("MUIS_SPLIT_THRESHOLD"), 150),  # FIXED: Lowered from 180 to 150
                       help="Split threshold (default: 150, lowered for safety)")
    parser.add_argument("--brand-seeds",
                       default=os.getenv("MUIS_BRAND_SEEDS", "mcdon,kfc,subw,starbucks,burger king,pizza hut,domino,old chang kee,popeyes,texas chicken,nando,swensen,sakae sushi,sushi tei,din tai fung,crystal jade,soup restaurant,jollibee,long john,subway,mos burger,seoul garden,tang tea,nasty cookie"),
                       help="Comma-separated brand seed terms")
    parser.add_argument("--rate", type=float,
                       default=float(os.getenv("MUIS_API_RATE_PER_SEC", "2")),
                       help="Requests per second (default: 2)")
    parser.add_argument("--max-records", type=int,
                       default=coerce_int(os.getenv("MUIS_API_MAX_RECORDS"), 0),
                       help="Stop after N records, 0=unlimited (default: 0)")
    parser.add_argument("--out-csv",
                       default=os.getenv("MUIS_API_OUT_CSV", DEFAULT_OUTPUT_CSV),
                       help="Output CSV path")
    parser.add_argument("--out-json",
                       default=os.getenv("MUIS_API_OUT_JSON", DEFAULT_OUTPUT_JSON),
                       help="Output raw JSON path")
    parser.add_argument("--insecure", action="store_true",
                       help="Disable TLS certificate verification")

    args = parser.parse_args(argv)

    # Apply TLS verification override if requested
    global VERIFY
    if args.insecure:
        VERIFY = False

    max_records = None if args.max_records <= 0 else args.max_records
    rate = max(0.5, float(args.rate))

    print(f"FIXED MUIS Scraper - Starting...", file=sys.stderr)
    print(f"  Base page: {args.base_page}", file=sys.stderr)
    print(f"  Search URL: {args.search_url}", file=sys.stderr)
    print(f"  Max prefix length: {args.max_prefix_len} (FIXED: increased from 4)", file=sys.stderr)
    print(f"  Split threshold: {args.split_threshold} (FIXED: lowered from 180)", file=sys.stderr)
    print(f"  Rate limit: {rate} req/sec", file=sys.stderr)
    print(f"  200-cap detection: ENABLED (CRITICAL FIX)", file=sys.stderr)
    print("", file=sys.stderr)

    all_records: List[Dict[str, Any]] = []

    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
        })

        seed_terms = [s.strip() for s in (args.brand_seeds or "").split(',') if s.strip()]

        raw_items = adaptive_search_mode_harvest_fixed(
            session=session,
            search_url=args.search_url,
            base_page_url=args.base_page,
            alphabet=args.alphabet,
            min_prefix_len=max(1, args.min_prefix_len),
            max_prefix_len=max(1, args.max_prefix_len),
            split_threshold=max(1, args.split_threshold),
            seed_terms=seed_terms,
            rate_limit_per_sec=rate,
            max_records=max_records,
        )

        # Persist raw JSON
        try:
            with open(args.out_json, "w", encoding="utf-8") as f:
                json.dump({"items": raw_items, "count": len(raw_items)}, f, indent=2)
            print(f"\nWrote raw data to {args.out_json}", file=sys.stderr)
        except Exception as e:
            print(f"WARNING: Could not write JSON: {e}", file=sys.stderr)

        # Map to schema
        for item in raw_items:
            all_records.append(map_item_to_schema(item, args.search_url))

    except Exception as exc:
        print(f"ERROR during scraping: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

    # Create DataFrame and save CSV
    df = to_dataframe(all_records)
    df.to_csv(args.out_csv, index=False)

    print(f"\n{'='*80}", file=sys.stderr)
    print(f"SUCCESS: Wrote {len(df)} rows to {args.out_csv}", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
