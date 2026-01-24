#!/usr/bin/env python3
"""
HalalTag Food Scraper - Single File MVP
========================================

Scrapes halal food establishments from https://www.halaltag.com

Usage:
    python halal_food_scraper.py
    python halal_food_scraper.py --alpha A,B,C --max-pages 5
    python halal_food_scraper.py --alpha ALL --max-pages 2

Outputs:
    - halaltag_places.csv (flattened data)
    - halaltag_places.json (structured data)
"""

import argparse
import csv
import json
import logging
import re
import sys
import time
from datetime import datetime
from typing import Dict, List, Set, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HalalTagScraper:
    """
    Scraper for HalalTag food directory website.
    
    Crawls alphabetical listings and extracts detailed information
    about halal food establishments in Singapore.
    """
    
    def __init__(self, delay: float = 0.5, max_pages: int = 10):
        """
        Initialize the scraper.
        
        Args:
            delay: Seconds to wait between requests (default 0.5)
            max_pages: Maximum pages to crawl per alphabet letter (default 10)
        """
        self.base_url = "https://www.halaltag.com"
        self.delay = delay
        self.max_pages = max_pages
        
        # Setup HTTP session with polite headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HalalTag Research Bot/1.0 (Educational Purpose)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        # Storage for results
        self.places: List[Dict] = []
        self.visited_urls: Set[str] = set()
    
    def scrape_all_alphabets(self, alphabets: List[str] = None) -> List[Dict]:
        """
        Scrape places for specified alphabet letters.
        
        Args:
            alphabets: List of letters to scrape (default: A-Z, 0-9, #)
            
        Returns:
            List of place dictionaries
        """
        if alphabets is None:
            # Default: all letters, numbers, and special
            alphabets = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + list('0123456789') + ['#']
        
        logger.info(f"Starting scrape for alphabets: {', '.join(alphabets)}")
        
        total_places = 0
        total_detail_pages = 0
        
        for alpha in alphabets:
            logger.info(f"\n{'='*50}")
            logger.info(f"Scraping alphabet: {alpha}")
            logger.info(f"{'='*50}")
            
            # Get all place URLs for this alphabet
            place_urls = self._scrape_alphabet_listings(alpha)
            logger.info(f"Found {len(place_urls)} unique place URLs for '{alpha}'")
            total_places += len(place_urls)
            
            # Scrape each place detail page
            for i, place_url in enumerate(place_urls, 1):
                logger.info(f"Scraping place {i}/{len(place_urls)}: {place_url}")
                
                try:
                    place_data = self._scrape_place_detail(place_url)
                    if place_data:
                        self.places.append(place_data)
                        total_detail_pages += 1
                        logger.info(f"  ✓ Extracted: {place_data['name']}")
                    else:
                        logger.warning(f"  ✗ Failed to extract data from {place_url}")
                        
                except Exception as e:
                    logger.error(f"  ✗ Error scraping {place_url}: {e}")
                
                # Polite delay between requests
                time.sleep(self.delay)
        
        logger.info(f"\n{'='*50}")
        logger.info(f"SCRAPING COMPLETE")
        logger.info(f"{'='*50}")
        logger.info(f"Total place URLs found: {total_places}")
        logger.info(f"Successfully scraped detail pages: {total_detail_pages}")
        logger.info(f"Success rate: {total_detail_pages/total_places*100:.1f}%" if total_places > 0 else "N/A")
        
        return self.places
    
    def _scrape_alphabet_listings(self, alpha: str) -> List[str]:
        """
        Scrape all place URLs for a specific alphabet letter.
        
        Args:
            alpha: Alphabet letter (A-Z, 0-9, or #)
            
        Returns:
            List of unique place URLs
        """
        place_urls = set()
        page = 1
        
        while page <= self.max_pages:
            logger.info(f"  Scraping {alpha} page {page}...")
            
            # Construct listing URL
            listing_url = f"{self.base_url}/place/index?alpha={alpha}&page={page}"
            
            try:
                response = self.session.get(listing_url, timeout=30)
                response.raise_for_status()
                
                # Parse listing page
                soup = BeautifulSoup(response.text, 'html.parser')
                page_urls = self._extract_place_urls_from_listing(soup)
                
                if not page_urls:
                    logger.info(f"    No place URLs found on page {page}, stopping pagination")
                    break
                
                place_urls.update(page_urls)
                logger.info(f"    Found {len(page_urls)} place URLs on page {page}")
                
                # Check if there's a next page
                if not self._has_next_page(soup, response.text):
                    logger.info(f"    No next page available, stopping pagination")
                    break
                    
                page += 1
                time.sleep(self.delay)  # Polite delay between listing pages
                
            except Exception as e:
                logger.error(f"    Error scraping listing page {page}: {e}")
                break
        
        return list(place_urls)
    
    def _extract_place_urls_from_listing(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract place URLs from a listing page.
        
        Args:
            soup: BeautifulSoup object of the listing page
            
        Returns:
            List of absolute place URLs
        """
        place_urls = []
        
        # Find all links that match place URL pattern
        # Pattern: href="/place/123" or similar
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            
            # Match place URL pattern: /place/ followed by digits or alphanumeric
            if re.match(r'^/place/[\w-]+/?$', href):
                full_url = urljoin(self.base_url, href)
                place_urls.append(full_url)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in place_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        return unique_urls
    
    def _has_next_page(self, soup: BeautifulSoup, page_text: str) -> bool:
        """
        Check if there's a next page available.
        
        Args:
            soup: BeautifulSoup object of current page
            page_text: Raw text content of the page
            
        Returns:
            True if next page exists, False otherwise
        """
        # Method 1: Look for "Showing X-Y of N" pattern
        showing_match = re.search(r'Showing\s+(\d+)[-–]\s*(\d+)\s+of\s+(\d+)', page_text)
        if showing_match:
            start, end, total = map(int, showing_match.groups())
            return end < total
        
        # Method 2: Look for next page navigation links
        next_indicators = [
            'a:contains("Next")',
            'a:contains("»")', 
            'a[href*="page="]',
            '.pagination a'
        ]
        
        for selector in next_indicators:
            if soup.select(selector):
                return True
        
        # Method 3: Look for page numbers higher than current
        page_links = soup.find_all('a', href=re.compile(r'page=\d+'))
        if len(page_links) > 1:  # More than just current page
            return True
        
        return False
    
    def _scrape_place_detail(self, place_url: str) -> Dict:
        """
        Scrape detailed information from a place page.
        
        Args:
            place_url: URL of the place detail page
            
        Returns:
            Dictionary containing place information
        """
        try:
            response = self.session.get(place_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract place information
            place_data = {
                'place_id': self._extract_place_id(place_url),
                'name': self._extract_name(soup),
                'halal_status': self._extract_halal_status(soup),
                'url': place_url,
                'outlets': self._extract_outlets(soup),
                'scraped_at': datetime.now().isoformat()
            }
            
            return place_data
            
        except Exception as e:
            logger.error(f"Error scraping place detail {place_url}: {e}")
            return None
    
    def _extract_place_id(self, url: str) -> str:
        """Extract place ID from URL."""
        path = urlparse(url).path
        # Extract ID from /place/123 or /place/name-123
        match = re.search(r'/place/([\w-]+)', path)
        return match.group(1) if match else 'unknown'
    
    def _extract_name(self, soup: BeautifulSoup) -> str:
        """
        Extract place name from detail page.
        
        Args:
            soup: BeautifulSoup object of the detail page
            
        Returns:
            Place name string
        """
        # Try multiple selectors for place name
        name_selectors = [
            'h1',  # Most common
            'h2',  # Fallback
            '.place-name',
            '.restaurant-name', 
            'title'
        ]
        
        for selector in name_selectors:
            elements = soup.select(selector)
            for element in elements:
                name = element.get_text().strip()
                
                # Clean up title tags (remove site name, etc.)
                if selector == 'title':
                    # Split on common separators and take first part
                    for sep in [' | ', ' - ', ' – ', ' :: ']:
                        if sep in name:
                            name = name.split(sep)[0].strip()
                            break
                
                # Validate name (not empty, reasonable length)
                if name and 3 <= len(name) <= 100:
                    return name
        
        return "Unknown Place"
    
    def _extract_halal_status(self, soup: BeautifulSoup) -> str:
        """
        Extract halal certification status.
        
        Args:
            soup: BeautifulSoup object of the detail page
            
        Returns:
            Halal status string
        """
        # Get all text content to search for status phrases
        page_text = soup.get_text()
        
        # Define halal status patterns (case insensitive)
        status_patterns = [
            (r'MUIS\s+Halal\s+Certified', 'MUIS Halal Certified'),
            (r'Halal\s*[-–]\s*Muslim\s+Owned', 'Halal - Muslim Owned'),
            (r'Muslim\s+Owned', 'Muslim Owned'),
            (r'Halal\s+Certified', 'Halal Certified'),
            (r'Certified\s+Halal', 'Certified Halal'),
            (r'Halal', 'Halal')
        ]
        
        # Search for patterns in order of specificity
        for pattern, status in status_patterns:
            if re.search(pattern, page_text, re.IGNORECASE):
                return status
        
        return "Status Unknown"
    
    def _extract_outlets(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract outlet information (addresses) from detail page.
        
        Args:
            soup: BeautifulSoup object of the detail page
            
        Returns:
            List of outlet dictionaries with 'label' and 'address' keys
        """
        outlets = []
        
        # Strategy 1: Find "View Map" links and extract nearby text
        map_links = soup.find_all('a', href=re.compile(r'maps|directions', re.I))
        map_links.extend(soup.find_all('a', string=re.compile(r'view\s+map', re.I)))
        
        for map_link in map_links:
            outlet = self._extract_outlet_from_map_link(map_link)
            if outlet:
                outlets.append(outlet)
        
        # Strategy 2: Look for address-like text patterns
        if not outlets:
            outlets = self._extract_outlets_from_text_patterns(soup)
        
        # Strategy 3: Look for structured address blocks
        if not outlets:
            outlets = self._extract_outlets_from_structure(soup)
        
        # Deduplicate outlets based on address
        seen_addresses = set()
        unique_outlets = []
        for outlet in outlets:
            addr_key = outlet.get('address', '').lower().strip()
            if addr_key and addr_key not in seen_addresses:
                seen_addresses.add(addr_key)
                unique_outlets.append(outlet)
        
        return unique_outlets
    
    def _extract_outlet_from_map_link(self, map_link) -> Dict:
        """Extract outlet info from a 'View Map' link context."""
        outlet = {'label': '', 'address': ''}
        
        # Get surrounding text context
        parent = map_link.parent
        if parent:
            # Look for address in parent text
            parent_text = parent.get_text().strip()
            
            # Remove the "View Map" text itself
            clean_text = re.sub(r'view\s+map', '', parent_text, flags=re.I).strip()
            
            # Split into lines and find address-like content
            lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
            
            for line in lines:
                if self._looks_like_address(line):
                    outlet['address'] = line
                    break
            
            # Use first non-address line as label if available
            for line in lines:
                if line != outlet['address'] and len(line) > 3:
                    outlet['label'] = line
                    break
        
        return outlet if outlet['address'] else None
    
    def _extract_outlets_from_text_patterns(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract outlets using text pattern matching."""
        outlets = []
        
        # Get all text and split into lines
        page_text = soup.get_text()
        lines = [line.strip() for line in page_text.split('\n') if line.strip()]
        
        for line in lines:
            if self._looks_like_address(line):
                outlets.append({
                    'label': '',
                    'address': line
                })
        
        return outlets[:5]  # Limit to reasonable number
    
    def _extract_outlets_from_structure(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract outlets from structured HTML elements."""
        outlets = []
        
        # Look for common structural patterns
        address_selectors = [
            '.address',
            '.location', 
            '.outlet',
            '.branch',
            '[class*="address"]',
            '[class*="location"]'
        ]
        
        for selector in address_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                if self._looks_like_address(text):
                    outlets.append({
                        'label': '',
                        'address': text
                    })
        
        return outlets
    
    def _looks_like_address(self, text: str) -> bool:
        """
        Check if text looks like a Singapore address.
        
        Args:
            text: Text string to check
            
        Returns:
            True if text appears to be an address
        """
        if not text or len(text) < 10:
            return False
        
        # Singapore address indicators
        address_indicators = [
            r'\d+.*(?:road|street|avenue|drive|lane|place|way|park|close|crescent|terrace)',
            r'singapore\s+\d{6}',
            r'#\d+-\d+',  # Unit numbers like #01-23
            r'\d{6}',  # Postal codes
            r'blk\s+\d+',  # Block numbers
            r'(?:north|south|east|west|central)\s+(?:road|street|avenue)'
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in address_indicators)
    
    def save_to_csv(self, filename: str = 'halaltag_places.csv'):
        """
        Save scraped data to CSV file.
        
        Args:
            filename: Output CSV filename
        """
        if not self.places:
            logger.warning("No data to save to CSV")
            return
        
        logger.info(f"Saving {len(self.places)} places to {filename}...")
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Create flattened rows (one row per place-outlet combination)
            fieldnames = ['place_id', 'name', 'halal_status', 'url', 'outlet_label', 'outlet_address', 'scraped_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            total_rows = 0
            for place in self.places:
                if place.get('outlets'):
                    # One row per outlet
                    for outlet in place['outlets']:
                        writer.writerow({
                            'place_id': place['place_id'],
                            'name': place['name'],
                            'halal_status': place['halal_status'],
                            'url': place['url'],
                            'outlet_label': outlet.get('label', ''),
                            'outlet_address': outlet.get('address', ''),
                            'scraped_at': place['scraped_at']
                        })
                        total_rows += 1
                else:
                    # Place without outlets
                    writer.writerow({
                        'place_id': place['place_id'],
                        'name': place['name'],
                        'halal_status': place['halal_status'],
                        'url': place['url'],
                        'outlet_label': '',
                        'outlet_address': '',
                        'scraped_at': place['scraped_at']
                    })
                    total_rows += 1
            
            logger.info(f"✓ Saved {total_rows} rows to {filename}")
    
    def save_to_json(self, filename: str = 'halaltag_places.json'):
        """
        Save scraped data to JSON file.
        
        Args:
            filename: Output JSON filename
        """
        if not self.places:
            logger.warning("No data to save to JSON")
            return
        
        logger.info(f"Saving {len(self.places)} places to {filename}...")
        
        output_data = {
            'scraping_info': {
                'timestamp': datetime.now().isoformat(),
                'total_places': len(self.places),
                'total_outlets': sum(len(p.get('outlets', [])) for p in self.places),
                'source_url': self.base_url
            },
            'places': self.places
        }
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(output_data, jsonfile, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Saved {len(self.places)} places to {filename}")
    
    def print_summary(self):
        """Print a summary of scraped data."""
        if not self.places:
            logger.info("No data scraped.")
            return
        
        total_outlets = sum(len(p.get('outlets', [])) for p in self.places)
        halal_status_counts = {}
        
        for place in self.places:
            status = place.get('halal_status', 'Unknown')
            halal_status_counts[status] = halal_status_counts.get(status, 0) + 1
        
        logger.info(f"\n{'='*50}")
        logger.info("SCRAPING SUMMARY")
        logger.info(f"{'='*50}")
        logger.info(f"Total places scraped: {len(self.places)}")
        logger.info(f"Total outlets found: {total_outlets}")
        logger.info(f"Average outlets per place: {total_outlets/len(self.places):.1f}")
        
        logger.info(f"\nHalal Status Breakdown:")
        for status, count in sorted(halal_status_counts.items()):
            logger.info(f"  {status}: {count}")
        
        # Show sample places
        logger.info(f"\nSample Places:")
        for i, place in enumerate(self.places[:3], 1):
            logger.info(f"  {i}. {place['name']} ({place['halal_status']})")
            for outlet in place.get('outlets', [])[:2]:  # Max 2 outlets per sample
                addr = outlet.get('address', 'No address')[:50] + ('...' if len(outlet.get('address', '')) > 50 else '')
                logger.info(f"     - {addr}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Scrape halal food establishments from HalalTag.com'
    )
    
    parser.add_argument(
        '--alpha',
        default='ALL',
        help='Alphabet letters to scrape (e.g., "A,B,C" or "ALL" for all). Default: ALL'
    )
    
    parser.add_argument(
        '--max-pages',
        type=int,
        default=10,
        help='Maximum pages to scrape per alphabet letter. Default: 10'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=0.5,
        help='Delay between requests in seconds. Default: 0.5'
    )
    
    parser.add_argument(
        '--output-csv',
        default='halaltag_places.csv',
        help='Output CSV filename. Default: halaltag_places.csv'
    )
    
    parser.add_argument(
        '--output-json', 
        default='halaltag_places.json',
        help='Output JSON filename. Default: halaltag_places.json'
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Parse alphabet argument
    if args.alpha.upper() == 'ALL':
        alphabets = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + list('0123456789') + ['#']
    else:
        alphabets = [a.strip().upper() for a in args.alpha.split(',')]
    
    logger.info("HalalTag Food Scraper Starting...")
    logger.info(f"Target alphabets: {', '.join(alphabets)}")
    logger.info(f"Max pages per alphabet: {args.max_pages}")
    logger.info(f"Request delay: {args.delay}s")
    
    try:
        # Initialize scraper
        scraper = HalalTagScraper(delay=args.delay, max_pages=args.max_pages)
        
        # Scrape data
        places = scraper.scrape_all_alphabets(alphabets)
        
        if not places:
            logger.error("No data was scraped. This could mean:")
            logger.error("1. The website structure has changed")
            logger.error("2. The site is blocking requests") 
            logger.error("3. Network connectivity issues")
            logger.error("\nTip: Try using Selenium/Playwright for JavaScript-heavy content")
            sys.exit(1)
        
        # Save results
        scraper.save_to_csv(args.output_csv)
        scraper.save_to_json(args.output_json)
        
        # Print summary
        scraper.print_summary()
        
        logger.info(f"\n✓ Scraping completed successfully!")
        logger.info(f"✓ Results saved to {args.output_csv} and {args.output_json}")
        
    except KeyboardInterrupt:
        logger.info("\n\nScraping interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()