#!/usr/bin/env python3
"""
Data Quality Fix Script
=======================

Fixes data quality issues in both MUIS and HalalTag datasets:
1. Extracts postal codes from HalalTag addresses
2. Geocodes addresses to add lat/long coordinates (optional)
3. Validates and cleans the data
4. Prepares data for OUTLET-LEVEL deduplication

IMPORTANT: place_id in both datasets represents BRANDS, not individual outlets.
Each ROW represents a unique physical outlet location.

Usage:
    python3 fix_data_quality.py
    python3 fix_data_quality.py --geocode  # Enable geocoding (slow, uses free OneMap API)
"""

import argparse
import re
import sys
import time
from typing import Optional, Tuple

import pandas as pd
import requests

# Singapore postal code regex - 6 digits
POSTAL_CODE_PATTERN = re.compile(r'\b(\d{6})\b')


class DataQualityFixer:
    """Fixes data quality issues in scraped datasets."""

    def __init__(self, use_geocoding: bool = False, rate_limit: float = 0.5):
        """
        Initialize the fixer.

        Args:
            use_geocoding: Whether to geocode addresses (requires API)
            rate_limit: Seconds between API calls
        """
        self.use_geocoding = use_geocoding
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DataQualityFixer/1.0 (Educational Purpose)'
        })

    def extract_postal_code(self, address: str) -> Optional[str]:
        """
        Extract 6-digit Singapore postal code from address string.

        Args:
            address: Address string

        Returns:
            Postal code string or None
        """
        if not address or pd.isna(address):
            return None

        match = POSTAL_CODE_PATTERN.search(str(address))
        if match:
            return match.group(1)
        return None

    def geocode_address_onemap(self, address: str, postal_code: Optional[str] = None) -> Tuple[Optional[float], Optional[float]]:
        """
        Geocode address using Singapore OneMap API (free, no key required).

        Args:
            address: Full address
            postal_code: Postal code (preferred for accuracy)

        Returns:
            (latitude, longitude) tuple or (None, None)
        """
        if not self.use_geocoding:
            return None, None

        # Prefer postal code for accuracy
        search_val = postal_code if postal_code else address
        if not search_val or pd.isna(search_val):
            return None, None

        url = "https://www.onemap.gov.sg/api/common/elastic/search"
        params = {
            'searchVal': str(search_val),
            'returnGeom': 'Y',
            'getAddrDetails': 'Y'
        }

        try:
            time.sleep(self.rate_limit)  # Rate limiting
            resp = self.session.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if data.get('found', 0) > 0:
                results = data.get('results', [])
                if results:
                    first = results[0]
                    lat = float(first.get('LATITUDE', 0))
                    lon = float(first.get('LONGITUDE', 0))
                    if lat and lon:
                        return lat, lon
        except Exception as e:
            print(f"  Warning: Geocoding failed for '{search_val}': {e}", file=sys.stderr)

        return None, None

    def fix_halaltag_data(self, input_csv: str, output_csv: str) -> pd.DataFrame:
        """
        Fix HalalTag dataset issues.

        IMPORTANT: Each row is a unique outlet. place_id represents the brand.

        Args:
            input_csv: Input CSV file path
            output_csv: Output CSV file path

        Returns:
            Fixed DataFrame
        """
        print("Processing HalalTag dataset...")
        df = pd.read_csv(input_csv)

        print(f"  Loaded {len(df)} outlet records")
        print(f"  Representing {df['place_id'].nunique()} brands")

        # Extract postal codes
        print("  Extracting postal codes from addresses...")
        df['postal_code'] = df['outlet_address'].apply(self.extract_postal_code)
        extracted = df['postal_code'].notna().sum()
        print(f"  Extracted {extracted}/{len(df)} postal codes ({100*extracted/len(df):.1f}%)")

        # Add latitude/longitude columns if they don't exist
        if 'latitude' not in df.columns:
            df['latitude'] = None
        if 'longitude' not in df.columns:
            df['longitude'] = None

        # Geocode if enabled
        if self.use_geocoding:
            print("  Geocoding addresses (this will take a while - ~4000 requests)...")
            print(f"  Estimated time: {len(df) * self.rate_limit / 60:.1f} minutes")

            for idx, row in df.iterrows():
                if idx % 100 == 0:
                    print(f"    Progress: {idx}/{len(df)} ({100*idx/len(df):.1f}%)")

                # Skip if already geocoded
                if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
                    continue

                lat, lon = self.geocode_address_onemap(
                    row.get('outlet_address'),
                    row.get('postal_code')
                )
                df.at[idx, 'latitude'] = lat
                df.at[idx, 'longitude'] = lon

            geocoded = df['latitude'].notna().sum()
            print(f"  Geocoded {geocoded}/{len(df)} addresses ({100*geocoded/len(df):.1f}%)")

        # Save
        df.to_csv(output_csv, index=False)
        print(f"  Saved to {output_csv}")

        return df

    def fix_muis_data(self, input_csv: str, output_csv: str) -> pd.DataFrame:
        """
        Fix MUIS dataset issues.

        IMPORTANT: Each row is a unique outlet. place_id represents the brand.

        Args:
            input_csv: Input CSV file path
            output_csv: Output CSV file path

        Returns:
            Fixed DataFrame
        """
        print("Processing MUIS dataset...")
        df = pd.read_csv(input_csv)

        print(f"  Loaded {len(df)} outlet records")
        print(f"  Representing {df['place_id'].nunique()} brands")

        # MUIS already has postal codes
        existing_postal = df['postal_code'].notna().sum()
        print(f"  Existing postal codes: {existing_postal}/{len(df)} ({100*existing_postal/len(df):.1f}%)")

        # Geocode if enabled
        if self.use_geocoding:
            print("  Geocoding addresses (this will take a while - ~4500 requests)...")
            print(f"  Estimated time: {len(df) * self.rate_limit / 60:.1f} minutes")

            # Convert empty strings to None for lat/long
            df['latitude'] = df['latitude'].replace('', None)
            df['longitude'] = df['longitude'].replace('', None)

            for idx, row in df.iterrows():
                if idx % 100 == 0:
                    print(f"    Progress: {idx}/{len(df)} ({100*idx/len(df):.1f}%)")

                # Skip if already geocoded
                if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
                    continue

                postal = row.get('postal_code')
                address = row.get('address')

                lat, lon = self.geocode_address_onemap(address, postal)
                df.at[idx, 'latitude'] = lat
                df.at[idx, 'longitude'] = lon

            geocoded = df['latitude'].notna().sum()
            print(f"  Geocoded {geocoded}/{len(df)} addresses ({100*geocoded/len(df):.1f}%)")

        # Save
        df.to_csv(output_csv, index=False)
        print(f"  Saved to {output_csv}")

        return df


def main():
    parser = argparse.ArgumentParser(
        description="Fix data quality issues in MUIS and HalalTag datasets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract postal codes only (fast)
  python3 fix_data_quality.py

  # Extract postal codes AND geocode (slow, ~45 minutes)
  python3 fix_data_quality.py --geocode

  # Geocode with faster rate (less polite to API)
  python3 fix_data_quality.py --geocode --rate-limit 0.2
        """
    )

    parser.add_argument(
        '--muis-input',
        default='muis_complete_final.csv',
        help='Input MUIS CSV file (default: muis_complete_final.csv)'
    )
    parser.add_argument(
        '--halaltag-input',
        default='halaltag_places.csv',
        help='Input HalalTag CSV file (default: halaltag_places.csv)'
    )
    parser.add_argument(
        '--muis-output',
        default='muis_fixed.csv',
        help='Output MUIS CSV file (default: muis_fixed.csv)'
    )
    parser.add_argument(
        '--halaltag-output',
        default='halaltag_fixed.csv',
        help='Output HalalTag CSV file (default: halaltag_fixed.csv)'
    )
    parser.add_argument(
        '--geocode',
        action='store_true',
        help='Enable geocoding using OneMap API (free but slow, ~45 mins total)'
    )
    parser.add_argument(
        '--rate-limit',
        type=float,
        default=0.5,
        help='Seconds between API calls (default: 0.5, min 0.2)'
    )

    args = parser.parse_args()

    print("="*70)
    print("DATA QUALITY FIXER")
    print("="*70)
    print(f"MUIS input: {args.muis_input}")
    print(f"HalalTag input: {args.halaltag_input}")
    print(f"Geocoding: {'ENABLED (using OneMap API)' if args.geocode else 'DISABLED'}")
    if args.geocode:
        print(f"Rate limit: {args.rate_limit} seconds/request")
        print("WARNING: Geocoding ~8700 addresses will take significant time!")
    print()

    fixer = DataQualityFixer(
        use_geocoding=args.geocode,
        rate_limit=max(0.2, args.rate_limit)  # Minimum 0.2s to be polite
    )

    # Fix HalalTag data
    print("\n" + "="*70)
    halaltag_df = fixer.fix_halaltag_data(args.halaltag_input, args.halaltag_output)

    # Fix MUIS data
    print("\n" + "="*70)
    muis_df = fixer.fix_muis_data(args.muis_input, args.muis_output)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"HalalTag: {len(halaltag_df)} outlet records processed ({halaltag_df['place_id'].nunique()} brands)")
    print(f"  Postal codes: {halaltag_df['postal_code'].notna().sum()}/{len(halaltag_df)}")
    if args.geocode:
        print(f"  Geocoded: {halaltag_df['latitude'].notna().sum()}/{len(halaltag_df)}")

    print(f"\nMUIS: {len(muis_df)} outlet records processed ({muis_df['place_id'].nunique()} brands)")
    print(f"  Postal codes: {muis_df['postal_code'].notna().sum()}/{len(muis_df)}")
    if args.geocode:
        print(f"  Geocoded: {muis_df['latitude'].notna().sum()}/{len(muis_df)}")

    print("\nNext steps:")
    if not args.geocode:
        print("  1. Run with --geocode to add lat/long coordinates (optional but recommended)")
        print("  2. Use the fixed files for outlet-level deduplication")
    else:
        print("  1. Use the fixed files for outlet-level deduplication")
    print("="*70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
