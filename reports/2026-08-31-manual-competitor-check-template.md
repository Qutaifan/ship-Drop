# Manual Competitor Check — electric pepper grinder

Date: 2026-08-31
Markets: DE, FR, NL, IT, ES
Backend: Manual Facebook Ad Library review (https://www.facebook.com/ads/library/)
Reason: Metapi.io API returning HTTP 404 on all documented endpoints as of 2026-08-31

## Instructions
1. Go to https://www.facebook.com/ads/library/
2. Select country: Germany → search "electric pepper grinder" → filter "Active"
3. Record: advertiser name, ad count, start date, reach
4. Repeat for: FR, NL, IT, ES
5. Count distinct advertisers (need 5-10)
6. Count ads running 30+ days (need 3+)

## Manual Data Collection

### Germany (DE)
| Advertiser | Ad Count | Oldest Active Ad | Reach |
|------------|----------|------------------|-------|
|  |  |  |  |
|  |  |  |  |

### France (FR)
| Advertiser | Ad Count | Oldest Active Ad | Reach |
|------------|----------|------------------|-------|
|  |  |  |  |

### Netherlands (NL)
| Advertiser | Ad Count | Oldest Active Ad | Reach |
|------------|----------|------------------|-------|
|  |  |  |  |

### Italy (IT)
| Advertiser | Ad Count | Oldest Active Ad | Reach |
|------------|----------|------------------|-------|
|  |  |  |  |

### Spain (ES)
| Advertiser | Ad Count | Oldest Active Ad | Reach |
|------------|----------|------------------|-------|
|  |  |  |  |

## Aggregated Results
- Total distinct advertisers: ___
- Total ads running 30+ days: ___
- VERDICT: ___ (need 5+ advertisers AND 3+ aged ads to PASS)

## Notes
- "Active" filter shows currently running ads
- "Inactive" filter shows stopped ads (don't count for aged-ads check)
- Reach is shown per ad, sum by advertiser
- If a brand shows the same ad across multiple countries, count advertiser once
