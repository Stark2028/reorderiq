# Data card

Source: Chen, D. (2012), Online Retail II, UCI, DOI:10.24432/C5CG6D, CC BY 4.0. Official dataset page: https://archive.ics.uci.edu/dataset/502/online+retail+ii . Official archive: https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip . Source workbook SHA-256: `bcbe73b35f5b7babf197fb0cb983a11f5d9ff929078d4aa53d171b1f2df2e980`.

## Population and observation

UK non-store giftware retailer, December 2009 to December 2011. Source documentation says many customers are wholesalers. Customer IDs are pseudonymous observed buyers, not verified business entities or new registrations. Currency is GBP. Historical behavior does not establish current Indian B2B behavior.

The two source sheets contain 1,067,371 invoice lines. The complete observation ends at 2011-12-09 00:00, excluding the final partial day. Result: 775,972 accepted merchandise lines aggregated to 36,553 orders across 5,851 observed buyers. First accepted order: 2009-12-01 07:45. Last: 2011-12-08 20:01. Source timezone is unspecified; calculations retain its local wall time.

## Sequential exclusions

Counts are mutually exclusive in processing order, not independent source prevalence estimates.

| Reason | Lines excluded |
|---|---:|
| Invalid timestamp | 0 |
| Outside complete observation (including whole incomplete invoices) | 1,633 |
| Exact duplicate line | 34,328 |
| Missing/invalid customer ID | 234,143 |
| Cancellation invoice | 18,383 |
| Invalid invoice ID | 0 |
| Invalid/nonpositive quantity | 0 |
| Invalid/nonpositive price | 70 |
| Non-merchandise stock code | 2,842 |

Accepted + excluded lines equal the source line count. Exact duplicate removal is an operational cleaning decision; identical legitimate purchases could be removed. Stock codes must match five digits plus optional letters, removing postal/manual adjustment codes; this policy may also omit unusual legitimate products. Customer-ID exclusions change the represented population.

## Invoice boundary

Invoice lines aggregate into one order. Sixty-four accepted invoices span multiple timestamps, at most two minutes. Allow same-day spans <=5 minutes; timestamp the aggregate at its last line so later amounts are never visible early. Multiple-customer, cross-day or longer-span conflicts stop ingestion. If any invoice line lies beyond the complete observation end, the entire invoice is excluded.

## Target and eligibility

At a Monday snapshot, an eligible buyer has a qualifying purchase strictly before the cutoff and a most recent order no more than 180 days earlier. The target is at least one qualifying positive merchandise order in [Monday, next Monday). Only fully observed windows enter evaluation.

Returns do not retroactively erase placed orders. The target is not net revenue, retained orders, loyalty, permanent churn or profit. Source missingness, duplicates, extreme baskets, seasonality, left-truncated histories and historical cohort changes remain limitations. First observed purchase is not account registration. Observed invoices omit shopping and purchase activity outside this retailer.
