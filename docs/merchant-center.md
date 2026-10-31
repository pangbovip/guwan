# Google Merchant Center — Wen Gu Hall

Account: **Wen Gu Hall** · ID `5876782157` · `pangbo.vip@gmail.com`  
Live feeds: https://wenguhall.com/feed.xml · https://wenguhall.com/feed.tsv

## Strategy (2026-10-31)

| Topic | Decision |
| --- | --- |
| Product price currency | **USD only** (matches the English storefront) |
| Free listings target country | **United States only** |
| Shipping in feed | Free (`0.00 USD`), handling **3–5** days, transit **7–15** days (matches `policies.html` North America) |
| Website sales | Still ship **worldwide** via PayPal; that is separate from free listings |
| Korea / Japan / EU free listings | **Deferred** until local-currency feeds (KRW / JPY / EUR) exist |

Do **not** re-add 100+ sell-to countries while the feed is USD-only. That combination caused the Oct 2026 full rejection: missing shipping for some countries + unsupported currency.

## Regenerate the feed

After product edits in `index.html`:

```bash
python3 tools/build-product-pages.py
python3 tools/build-merchant-feed.py
```

Commit and push `feed.xml` / `feed.tsv`. Merchant Center fetches on its schedule (or use **Fetch now**).

## Merchant Center UI checklist (browser)

Do these under the Wen Gu Hall account so destinations match the feed:

1. **Products → Feeds**  
   Confirm the primary feed URL is `https://wenguhall.com/feed.xml` (or the TSV). Fetch/refresh after this deploy.

2. **Tools / Business information → Shipping and returns → Shipping**  
   - Remove or disable country groups that are **not** United States (especially **South Korea**, Japan, EU, and any leftover “100+ countries” / worldwide row from Oct 18).  
   - Keep or add **one** United States row:
     - Country: **United States**
     - Currency: **USD** (must match product prices)
     - Price: **0** (free standard shipping)
     - Transit time: **7–15** business days (or “order processing 3–5” + “delivery 7–15” if the UI splits handling vs transit — align with the feed attributes)
   - Shipping currency must stay **USD**. Do not leave KRW/JPY/EUR shipping rows active for this feed.

3. **Destinations / countries of sale (Free listings)**  
   - Enable free listings for **United States** only.  
   - Turn **off** South Korea and every other non-USD country for this feed.  
   - Website can still accept PayPal orders from anywhere; only Google free listings are US-scoped.

4. **Returns** (unchanged intent)  
   - 14 days after delivery, buyer-paid return shipping (except damaged / not as described), refund within 14 days of receiving the return — same as `policies.html`.

5. **After saving**  
   - Request a review / wait for automatic re-check. Expect **24–72 hours** for shipping and currency issues to clear.  
   - Diagnostics should stop showing “missing shipping for some countries” and “unsupported currency” once destinations ⊆ US and shipping is USD free for US.

## Sample feed shipping snippet

```xml
<g:price>499.00 USD</g:price>
...
<g:shipping>
  <g:country>US</g:country>
  <g:price>0.00 USD</g:price>
  <g:min_handling_time>3</g:min_handling_time>
  <g:max_handling_time>5</g:max_handling_time>
  <g:min_transit_time>7</g:min_transit_time>
  <g:max_transit_time>15</g:max_transit_time>
</g:shipping>
```

## Later: more countries

To list in Korea / Japan / EU on Google, add separate feeds (or supplemental feeds) with **local currency prices** and matching local-currency shipping rows, then enable those countries as destinations.
