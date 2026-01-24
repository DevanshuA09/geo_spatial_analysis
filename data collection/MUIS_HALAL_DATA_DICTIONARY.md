# MUIS Halal Certification Data Dictionary

**Document Purpose:** This data dictionary explains the meaning of codes in the `scheme` and `sub_scheme` columns from the MUIS Halal establishment dataset.

**Data Source:** MUIS (Majlis Ugama Islam Singapura) Halal API
**Last Updated:** December 2025
**Prepared:** December 4, 2025

---

## IMPORTANT DISCLAIMER

⚠️ **Validation Status:** The scheme and sub_scheme codes documented below are based on data pattern analysis and publicly available MUIS documentation. **The specific numerical codes (0, 1, 100, 200) and their sub-codes are NOT explicitly defined in publicly accessible MUIS documentation.** These interpretations are inferred from data patterns and should be verified with MUIS directly for official confirmation.

**For Official Information Contact:**
- MUIS Email: info@muis.gov.sg
- MUIS Phone: +65 6359 1199
- MUIS Halal Portal: https://halal.muis.gov.sg/

---

## Schema Overview

The dataset contains two key classification fields:
- **`scheme`**: Primary certification scheme type
- **`sub_scheme`**: Sub-category or operational classification within the scheme

---

## SCHEME CODES

### Scheme 0 - **Eating Establishment (Inactive/Legacy)**
**Inferred Meaning:** Appears to represent eating establishments that may have inactive certifications or are in a transitional state.

**Data Pattern Observations:**
- Associated with major chains (McDonald's, KFC, Burger King, Pizza Hut)
- Many entries show `type=0` (suggesting inactive or legacy status)
- Often paired with sub_scheme 100

**Typical Establishments:**
- Fast food restaurants
- Food court stalls
- Quick service restaurants

---

### Scheme 1 - **Eating Establishment (Virtual Brands/Special Category)**
**Inferred Meaning:** Eating establishments with special operational characteristics, possibly virtual brands, cloud kitchens, or multi-brand operations.

**Data Pattern Observations:**
- Lower frequency (approximately 20-30 establishments)
- Associated with entries noting "No virtual brand", "N.A", or "NO VIRTUAL BRANDS"
- Examples: Fish & Co., Bok Bok Chicken, Hotto Neko, Mana Lagi

**Typical Establishments:**
- Restaurants with delivery-only brands
- Multi-concept operations
- Cloud kitchens

**Sub_Scheme 100:** Standard operational category

---

### Scheme 100 - **Eating Establishment (Active/Standard)**
**Inferred Meaning:** The primary and most common certification scheme for retail eating establishments currently in operation.

**Official MUIS Definition (from research):**
The Eating Establishment Scheme is issued to retail food establishments such as restaurants, school canteen stalls, snack bars, Halal corners, confectioneries, bakery shops, stalls within a foodcourt and temporary stalls.

**Data Pattern Observations:**
- Represents the majority of establishments (~800+ entries)
- Active certifications with `type=0`
- Diverse sub_scheme categories

**Typical Establishments:**
- Restaurants
- Food stalls
- Cafes
- Bakeries
- School canteens
- Food court outlets

---

### Scheme 200 - **Food Preparation Area (Catering/Central Kitchen)**
**Inferred Meaning:** Certification for establishments primarily engaged in bulk food preparation, catering services, or central kitchen operations.

**Official MUIS Definition (from research):**
The Food Preparation Area Scheme is issued to catering establishments and central kitchen facilities.

**Key Differences from Scheme 100:**
- Requires minimum 3 Muslim staff (vs. 2 for Eating Establishment)
- Focuses on bulk preparation and off-site service
- Supplies food to multiple locations or events

**Data Pattern Observations:**
- Companies include catering services, central kitchens
- Examples: Robert Catering Services, Old Chang Kee (central kitchen), various catering companies
- Lower number of locations compared to Scheme 100

**Typical Establishments:**
- Catering companies
- Central kitchens
- Commissary operations
- Food production facilities

---

## SUB_SCHEME CODES (for Scheme 100)

The sub_scheme codes appear to classify eating establishments by their operational format and location characteristics.

### Sub_Scheme 101 - **[Interpretation Uncertain]**
**Inferred Meaning:** Specific operational category, possibly related to standalone outlets or specific venue types.

**Confidence Level:** ⚠️ LOW - Cannot be validated from available data

---

### Sub_Scheme 102 - **[Interpretation Uncertain]**
**Inferred Meaning:** Specific operational category.

**Confidence Level:** ⚠️ LOW - Cannot be validated from available data

---

### Sub_Scheme 103 - **[Interpretation Uncertain]**
**Inferred Meaning:** Specific operational category.

**Confidence Level:** ⚠️ LOW - Cannot be validated from available data

---

### Sub_Scheme 104 - **Petrol Station Outlets / Drive-Through Locations**
**Inferred Meaning:** Eating establishments located at petrol stations or with drive-through facilities.

**Data Pattern Observations:**
- McDonald's outlets at Shell, Mobil, Caltex service stations
- Stand-alone drive-through locations

**Typical Establishments:**
- Fast food at petrol stations
- Drive-through outlets
- Service station convenience stores

**Confidence Level:** ⚠️ MEDIUM - Based on data patterns, not official documentation

---

### Sub_Scheme 105 - **[Interpretation Uncertain]**
**Inferred Meaning:** Specific operational category.

**Confidence Level:** ⚠️ LOW - Cannot be validated from available data

---

### Sub_Scheme 106 - **Shopping Malls / Food Courts / Community Centers**
**Inferred Meaning:** Eating establishments located within shopping centers, malls, food courts, community clubs, and similar venues.

**Data Pattern Observations:**
- Most common sub_scheme code
- McDonald's at Marina Square, Suntec City, Parco Bugis Junction, Changi Airport
- Food court stalls
- Community center locations
- Educational institutions

**Typical Establishments:**
- Shopping mall restaurants
- Food court stalls
- Community center cafeterias
- Airport terminals
- Educational institutions
- Sports/recreation centers

**Confidence Level:** ⚠️ MEDIUM-HIGH - Strong data pattern correlation

---

### Sub_Scheme 108 - **[Interpretation Uncertain]**
**Inferred Meaning:** Specific operational category.

**Confidence Level:** ⚠️ LOW - Cannot be validated from available data

---

### Sub_Scheme 109 - **[Interpretation Uncertain]**
**Inferred Meaning:** Specific operational category.

**Confidence Level:** ⚠️ LOW - Cannot be validated from available data

---

## SUB_SCHEME CODES (for Scheme 200)

### Sub_Scheme 201 - **[Interpretation Uncertain]**
**Inferred Meaning:** Catering/central kitchen operational sub-category.

**Confidence Level:** ⚠️ LOW - Cannot be validated from available data

---

### Sub_Scheme 202 - **[Interpretation Uncertain]**
**Inferred Meaning:** Catering/central kitchen operational sub-category.

**Confidence Level:** ⚠️ LOW - Cannot be validated from available data

---

## ADDITIONAL CONTEXT

### MUIS Halal Certification Schemes

MUIS offers **7 main certification schemes:**

1. **Eating Establishment Scheme (EE)** - Retail food operations
2. **Food Preparation Area Scheme (FPA)** - Catering & central kitchens
3. **Product Scheme** - Manufactured food products
4. **Whole Plant Scheme** - Manufacturing facilities
5. **Endorsement Scheme** - Foreign-certified products
6. **Storage Facility Scheme** - Warehousing operations
7. **Poultry Abattoir Scheme** - Halal slaughterhouses

**Note:** The numerical codes in the dataset (0, 1, 100, 200) do NOT directly map to the 7 official scheme names above. These appear to be internal database classification codes.

---

## DATA QUALITY NOTES

1. **Incomplete Data:** Some records show certificate numbers in the sub_scheme field, indicating possible data quality issues
2. **Legacy Records:** Scheme 0 may represent outdated or transitional records
3. **Type Field:** The `type` field often shows `0` for most records; its meaning is unclear

---

## VERIFICATION REQUIRED

❌ **The following require official MUIS verification:**
- Exact meaning of scheme codes 0, 1, 100, 200
- Precise definitions of sub_scheme codes 101-109, 201-202
- Relationship between these codes and the 7 official MUIS schemes
- Meaning of the `type` field in the dataset

---

## RESEARCH SOURCES

This data dictionary was compiled using:
- Pattern analysis of the MUIS halal establishment dataset
- Official MUIS website documentation
- Singapore government GoBusiness portal information
- Industry documentation from halal certification consultants

### Key References:

1. [MUIS Halal Scheme Types & Eligibility Criteria](https://www.muis.gov.sg/halal/halal-certification/scheme-types-eligibility-criteria-hcc)
2. [GoBusiness Halal Certification Information](https://www.gobusiness.gov.sg/licensing-faqs/halal-certification/)
3. [Dollars and Sense - Halal Certification Guide](https://dollarsandsense.sg/business/how-apply-halal-certification-fb-singapore/)
4. [QuikQuality Halal Singapore Guide](https://www.quikquality.com/halal-sg)

---

## RECOMMENDATIONS

For applications requiring high accuracy:

1. **Contact MUIS directly** for official code definitions
2. **Cross-reference** with MUIS API documentation (if available)
3. **Validate interpretations** with certified halal establishments
4. **Monitor** for updates to MUIS classification systems

---

**Document Version:** 1.0
**Confidence Level:** PARTIAL - Some interpretations are data-driven inferences, not officially validated
**Next Update:** Upon receipt of official MUIS code definitions
