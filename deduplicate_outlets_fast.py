#!/usr/bin/env python3
"""
Fast Outlet-Level Deduplication Script
=======================================

Optimized version using postal code matching only.

Strategy:
1. Exact postal code match → SAME OUTLET
2. No postal code or different postal → DIFFERENT OUTLETS

This is safe because:
- Singapore postal codes are unique to buildings
- Same postal + similar name = same location
- Different postal = different location (even if same brand)

Usage:
    python3 deduplicate_outlets_fast.py
"""

import argparse
import re
import sys
from typing import Set

import pandas as pd


def normalize_name(name: str) -> str:
    """Normalize restaurant name for comparison."""
    if pd.isna(name):
        return ""

    name = str(name).lower().strip()
    name = re.sub(r'\b(pte\.?|ltd\.?|llp|singapore|sg)\b', '', name)
    name = re.sub(r'[^\w\s]', ' ', name)
    name = ' '.join(name.split())
    return name


def names_similar(name1: str, name2: str, threshold: float = 0.75) -> bool:
    """
    Check if two names are similar enough to be the same restaurant.

    Uses 75% threshold to avoid false positives in food courts/hawker centers
    where multiple stalls share the same postal code but have similar generic
    words like 'nasi', 'chicken', 'rice', etc.

    Args:
        name1: First restaurant name
        name2: Second restaurant name
        threshold: Minimum word overlap percentage (default: 0.75)

    Returns:
        True if names are similar enough
    """
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)

    if not n1 or not n2:
        return False

    # Extract main words (ignoring very common words)
    stopwords = {'restaurant', 'cafe', 'food', 'kitchen', 'house', 'stall'}
    words1 = set(w for w in n1.split() if len(w) > 2 and w not in stopwords)
    words2 = set(w for w in n2.split() if len(w) > 2 and w not in stopwords)

    if not words1 or not words2:
        # Fall back to full name comparison
        return n1 in n2 or n2 in n1

    # Check if significant overlap in words
    overlap = len(words1 & words2)
    min_words = min(len(words1), len(words2))

    # Use 75% threshold for safety (avoids false positives)
    return overlap >= max(1, min_words * threshold)


def deduplicate_fast(muis_csv: str, halaltag_csv: str) -> pd.DataFrame:
    """
    Fast deduplication using postal code matching only.

    Args:
        muis_csv: Path to MUIS CSV file
        halaltag_csv: Path to HalalTag CSV file

    Returns:
        Deduplicated DataFrame
    """
    print("Loading datasets...")
    muis_df = pd.read_csv(muis_csv)
    halaltag_df = pd.read_csv(halaltag_csv)

    print(f"  MUIS: {len(muis_df)} outlets")
    print(f"  HalalTag: {len(halaltag_df)} outlets")

    # Rename HalalTag columns
    halaltag_df = halaltag_df.rename(columns={
        'outlet_address': 'address',
        'outlet_label': 'outlet_name',
        'halal_status': 'muis_halal_status'
    })

    # Build postal code index for MUIS
    print("\nBuilding postal code index...")
    muis_postal_index = {}
    for idx, row in muis_df.iterrows():
        postal_raw = row.get('postal_code')
        if pd.notna(postal_raw):
            # Normalize to string (handle both int and float)
            postal = str(int(float(postal_raw)))
            if postal not in muis_postal_index:
                muis_postal_index[postal] = []
            muis_postal_index[postal].append(idx)

    print(f"  Indexed {len(muis_postal_index)} unique postal codes from MUIS")

    # Track results
    merged_records = []
    muis_matched: Set[int] = set()
    halaltag_matched: Set[int] = set()
    exact_matches = 0

    # Match HalalTag to MUIS by postal code
    print("\nMatching by postal code...")
    for ht_idx, ht_row in halaltag_df.iterrows():
        if ht_idx % 500 == 0:
            print(f"  Progress: {ht_idx}/{len(halaltag_df)} ({100*ht_idx/len(halaltag_df):.1f}%)")

        ht_postal_raw = ht_row.get('postal_code')

        # Only match if HalalTag has postal code
        if pd.isna(ht_postal_raw):
            continue

        # Normalize to string (handle both int and float)
        ht_postal = str(int(float(ht_postal_raw)))

        # Check if MUIS has this postal code
        if ht_postal not in muis_postal_index:
            continue

        # Find best match among MUIS outlets with same postal
        best_match = None
        best_match_idx = None

        for muis_idx in muis_postal_index[ht_postal]:
            if muis_idx in muis_matched:
                continue

            muis_row = muis_df.iloc[muis_idx]

            # Check if names are similar
            if names_similar(ht_row['name'], muis_row['name']):
                best_match = muis_row
                best_match_idx = muis_idx
                break  # Take first match

        # If found a match, merge
        if best_match is not None:
            merged_record = {
                'name': best_match['name'],
                'outlet_name': best_match.get('outlet_name') or ht_row.get('outlet_name'),
                'address': best_match['address'],
                'postal_code': best_match['postal_code'],
                'latitude': best_match.get('latitude') or ht_row.get('latitude'),
                'longitude': best_match.get('longitude') or ht_row.get('longitude'),
                'muis_halal_status': 'MUIS Halal Certified',
                'cuisine': best_match.get('cuisine') or ht_row.get('cuisine'),
                'website': best_match.get('website') or ht_row.get('website'),
                'phone': best_match.get('phone') or ht_row.get('phone'),
                'certificate_number': best_match.get('certificate_number'),
                'type': best_match.get('type'),
                'scheme': best_match.get('scheme'),
                'sub_scheme': best_match.get('sub_scheme'),
                'data_sources': 'muis,halaltag',
                'muis_place_id': best_match.get('place_id'),
                'halaltag_place_id': ht_row.get('place_id'),
            }
            merged_records.append(merged_record)
            muis_matched.add(best_match_idx)
            halaltag_matched.add(ht_idx)
            exact_matches += 1

    print(f"\n  Matched {exact_matches} outlets by postal code")

    # Add unmatched HalalTag outlets
    print("\nAdding unmatched HalalTag outlets...")
    for ht_idx, ht_row in halaltag_df.iterrows():
        if ht_idx in halaltag_matched:
            continue

        merged_record = {
            'name': ht_row['name'],
            'outlet_name': ht_row.get('outlet_name'),
            'address': ht_row.get('address'),
            'postal_code': ht_row.get('postal_code'),
            'latitude': ht_row.get('latitude'),
            'longitude': ht_row.get('longitude'),
            'muis_halal_status': ht_row.get('muis_halal_status'),
            'cuisine': ht_row.get('cuisine'),
            'website': ht_row.get('website'),
            'phone': ht_row.get('phone'),
            'certificate_number': None,
            'type': None,
            'scheme': None,
            'sub_scheme': None,
            'data_sources': 'halaltag',
            'muis_place_id': None,
            'halaltag_place_id': ht_row.get('place_id'),
        }
        merged_records.append(merged_record)

    # Add unmatched MUIS outlets
    print("Adding unmatched MUIS outlets...")
    for muis_idx, muis_row in muis_df.iterrows():
        if muis_idx in muis_matched:
            continue

        merged_record = {
            'name': muis_row['name'],
            'outlet_name': muis_row.get('outlet_name'),
            'address': muis_row['address'],
            'postal_code': muis_row['postal_code'],
            'latitude': muis_row.get('latitude'),
            'longitude': muis_row.get('longitude'),
            'muis_halal_status': 'MUIS Halal Certified',
            'cuisine': muis_row.get('cuisine'),
            'website': muis_row.get('website'),
            'phone': muis_row.get('phone'),
            'certificate_number': muis_row.get('certificate_number'),
            'type': muis_row.get('type'),
            'scheme': muis_row.get('scheme'),
            'sub_scheme': muis_row.get('sub_scheme'),
            'data_sources': 'muis',
            'muis_place_id': muis_row.get('place_id'),
            'halaltag_place_id': None,
        }
        merged_records.append(merged_record)

    return pd.DataFrame(merged_records)


def main():
    parser = argparse.ArgumentParser(
        description="Fast outlet deduplication using postal code matching"
    )

    parser.add_argument('--muis-input', default='muis_fixed.csv')
    parser.add_argument('--halaltag-input', default='halaltag_fixed.csv')
    parser.add_argument('--output', default='deduplicated_outlets.csv')

    args = parser.parse_args()

    print("="*70)
    print("FAST OUTLET-LEVEL DEDUPLICATION")
    print("="*70)
    print("Strategy: Postal code + name matching only")
    print(f"MUIS input: {args.muis_input}")
    print(f"HalalTag input: {args.halaltag_input}")
    print()

    result_df = deduplicate_fast(args.muis_input, args.halaltag_input)

    # Save
    result_df.to_csv(args.output, index=False)

    # Summary
    print("\n" + "="*70)
    print("DEDUPLICATION SUMMARY")
    print("="*70)
    print(f"Total unique outlets: {len(result_df)}")
    print(f"\nBreakdown by source:")
    print(f"  Both MUIS & HalalTag: {len(result_df[result_df['data_sources'] == 'muis,halaltag'])}")
    print(f"  MUIS only: {len(result_df[result_df['data_sources'] == 'muis'])}")
    print(f"  HalalTag only: {len(result_df[result_df['data_sources'] == 'halaltag'])}")

    print(f"\nData completeness:")
    print(f"  With postal codes: {result_df['postal_code'].notna().sum()} ({100*result_df['postal_code'].notna().sum()/len(result_df):.1f}%)")

    print(f"\nOutput saved to: {args.output}")
    print("="*70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
