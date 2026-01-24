# MUIS Halal Establishments CSV Documentation

This CSV file contains halal-certified establishments in Singapore scraped from the MUIS (Majlis Ugama Islam Singapura) API.

## Column Descriptions

| Column | Type | Description |
|--------|------|-------------|
| `source` | string | Data source identifier (always "muis") |
| `place_id` | string | Unique UUID identifier for the establishment |
| `name` | string | Name of the halal-certified establishment |
| `outlet_name` | string | Specific outlet name (currently empty - not provided by API) |
| `address` | string | Full street address of the establishment |
| `postal_code` | string | Singapore postal code |
| `latitude` | string | Latitude coordinate (currently empty - not provided by API) |
| `longitude` | string | Longitude coordinate (currently empty - not provided by API) |
| `muis_halal_status` | string | Halal certification status (always "MUIS Halal Certified") |
| `cuisine` | string | Type of cuisine (currently empty - not provided by API) |
| `website` | string | Establishment website (currently empty - not provided by API) |
| `phone` | string | Contact phone number (currently empty - not provided by API) |
| `last_scraped` | string | ISO 8601 timestamp (UTC) when the data was scraped |
| `source_url` | string | API endpoint URL used for scraping |
| `notes` | string | Additional notes (contains the certificate number) |
| `certificate_number` | string | MUIS halal certificate number (format: EEFK/EERN followed by numbers) |
| `type` | integer | Establishment type: `0` = Default (physical establishment), `1` = Virtual Brand (ghost kitchen) |
| `scheme` | integer | Certification scheme code (e.g., `100` = Eating Establishment) |
| `sub_scheme` | integer | Sub-scheme classification code (e.g., `104` = Food Kiosk, `106` = Restaurant) |

## Notes

- Empty columns (outlet_name, latitude, longitude, cuisine, website, phone) are included for schema consistency but not populated by the MUIS API
- The `type` field distinguishes between regular physical establishments (0) and virtual/ghost kitchen brands (1)
- Certificate numbers follow MUIS's format conventions (e.g., EEFK = Eating Establishment Food Kiosk, EERN = Eating Establishment Restaurant)
