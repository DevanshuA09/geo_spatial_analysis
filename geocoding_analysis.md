# Geocoding Analysis Report

## Overview
Geocoding analysis of 6,897 halal-certified outlets in Singapore using postal code and address matching against the Building2025_PC dataset.

## Data Filtering
- **Excluded**: Records with scheme = 200 and sub_scheme in [201, 202]
- **Removed columns**: cuisine, website, phone, latitude, longitude

## Geocoding Methodology

### Primary Match: Postal Code (Exact)
- Matched 6,539 records (94.8%) using exact postal code lookup
- Coordinates extracted from Building2025_PC dataset (SVY21 projection)

### Secondary Match: Address Fuzzy Matching
- Applied to 358 unmatched records
- Matched 56 additional records (0.8%) using substring matching on address fields
- Limited to first 500 unmatched records to optimize runtime

## Results

### Coverage
- **Total records**: 6,897
- **Successfully geocoded**: 6,595 (95.6%)
- **Unmatched**: 302 (4.4%)

### Match Distribution
| Method | Count | Percentage |
|--------|-------|------------|
| Postal (Exact) | 6,539 | 94.8% |
| Address (Fuzzy) | 56 | 0.8% |
| Unmatched | 302 | 4.4% |

### Coordinate Validation
- **X range**: 3,608.99 to 46,249.72 meters (SVY21)
- **Y range**: 24,251.56 to 49,992.30 meters (SVY21)
- All coordinates within valid Singapore boundaries

## Unmatched Records Analysis
- **Total unmatched**: 302 outlets
- **Primary source**: 295 from HalalTag, 7 from MUIS
- **Common issues**:
  - Missing postal codes (NaN values)
  - Invalid or non-standard postal codes
  - Address formatting inconsistencies

## Quality Assurance
- ✓ Row count preserved throughout processing
- ✓ Coordinate ranges validated against Singapore geography
- ✓ No duplicate coordinates introduced
- ✓ Source tracking maintained via geocode_source field

## Output Fields
- `X`, `Y`: SVY21 projected coordinates (meters)
- `geocode_source`: Match method (postal_exact, address_fuzzy, unmatched)
