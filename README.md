# Wen Gu Hall · 问古堂

**Curated Chinese antiquities & fine crafts — Hetian jade, Yixing zisha teapots, porcelain, ink painting, calligraphy and scholar curios.**

🌐 **Visit the store: [wenguhall.com](https://wenguhall.com/)**
🇯🇵 日本語: [wenguhall.com/ja.html](https://wenguhall.com/ja.html)

- One-of-a-kind curated pieces across six categories · [browse all pieces](https://wenguhall.com/p/)
- Worldwide insured shipping · [Store policies](https://wenguhall.com/policies.html)
- Contact: 86886779@qq.com · WhatsApp +86 139 1004 9069

## Maintaining the site

Product data lives in the `products` array in `index.html` (English, USD) and `ja.html` (Japanese, JPY).
After changing products, run `python tools/build-product-pages.py` from the repo root. It regenerates
`p/{SKU}.html`, the category landing pages in `c/` (categories and their copy: `tools/seo_content.py`),
`p/index.html`, `sitemap.xml`, and the category links in `index.html` / `ja.html` (between `<!--seo:...-->` markers).
