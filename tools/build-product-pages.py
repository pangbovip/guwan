# -*- coding: utf-8 -*-
"""Generate one static page per product from the product array in index.html.

Run from the repo root:  python tools/build-product-pages.py
Output: p/{SKU}.html for every product, c/{slug}.html category landing pages
(categories and their copy live in tools/seo_content.py), p/index.html
(crawlable hub of all pieces), the category link blocks inside index.html and
ja.html (between <!--seo:...--> markers) and a refreshed sitemap.xml.
"""
import io
import os
import re
import sys
import html
import json
import datetime
from string import Template

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seo_content import CATEGORIES, MISC, BUYING, ORDERING, JA_LABELS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://wenguhall.com'
OUT = os.path.join(ROOT, 'p')
CAT_OUT = os.path.join(ROOT, 'c')
BEACON = ("<script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"c97ee3e3bfcf4fbcba47268174152587\"}'></script>")
FAVICON = ("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' "
           "viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='10' fill='%239E2B25'/%3E"
           "%3Ctext x='32' y='45' text-anchor='middle' font-family='serif' font-size='38' "
           "font-weight='900' fill='%23F1E8D6'%3E问%3C/text%3E%3C/svg%3E")


def unescape(v):
    return v.replace("\\'", "'").replace('\\"', '"').replace('\\\\', '\\')


def parse_products(path):
    """Read the product objects out of the page's inline products array."""
    src = io.open(path, encoding='utf-8').read()
    start = src.index('const products = [')
    body = src[start:src.index('\n];', start)]
    items = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith('{id:'):
            continue
        p = {}
        for key in ('id', 'sku', 'name', 'origin', 'type', 'desc', 'image', 'specs', 'video'):
            m = re.search(key + r":'((?:[^'\\]|\\.)*)'", line)
            if m:
                p[key] = unescape(m.group(1))
        m = re.search(r'price:(\d+)', line)
        p['price'] = int(m.group(1)) if m else 0
        m = re.search(r'gallery:\[([^\]]*)\]', line)
        p['gallery'] = re.findall(r"'([^']+)'", m.group(1)) if m else []
        items.append(p)
    return items


def clip(text, limit):
    """Cut text at a word boundary so the result is at most `limit` chars."""
    text = ' '.join(text.split())
    if len(text) <= limit:
        return text
    cut = text[:limit - 1].rsplit(' ', 1)[0].rstrip(' ,;:-')
    return cut + '\u2026'


def meta_desc(p):
    """~150-160 character description: start of the catalogue text + price."""
    tail = ' US$%s, free insured worldwide shipping.' % format(p['price'], ',')
    desc = p['desc'].strip()
    first = re.split(r'(?<=[.!?])\s', desc)
    head = ''
    for sent in first:
        cand = (head + ' ' + sent).strip()
        if len(cand) + len(tail) > 160:
            break
        head = cand
    if not head:
        head = clip(desc, 160 - len(tail))
    if not head.endswith(('.', '!', '?', '\u2026')):
        head += '.'
    return head + tail


def ld_script(obj):
    txt = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    return '<script type="application/ld+json">%s</script>' % txt.replace('</', '<\\/')


def json_ld(p):
    imgs = [p['image']] + p['gallery']
    return ld_script({
        '@context': 'https://schema.org/', '@type': 'Product',
        'name': p['name'], 'sku': p['sku'], 'category': p['type'],
        'image': ['%s/%s' % (SITE, i) for i in imgs],
        'description': p['desc'],
        'brand': {'@type': 'Brand', 'name': 'Wen Gu Hall'},
        'offers': {'@type': 'Offer', 'url': '%s/p/%s.html' % (SITE, p['sku']),
                   'priceCurrency': 'USD', 'price': str(p['price']),
                   'availability': 'https://schema.org/InStock',
                   'itemCondition': 'https://schema.org/NewCondition',
                   'seller': {'@type': 'Organization', 'name': 'Wen Gu Hall'}},
    })


def breadcrumb_ld(trail):
    return ld_script({
        '@context': 'https://schema.org/', '@type': 'BreadcrumbList',
        'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u}
                            for i, (n, u) in enumerate(trail)]})


def cat_of(p):
    for c in CATEGORIES:
        if p['type'] in c['types']:
            return c
    return None


def cat_url(c):
    return '%s/c/%s.html' % (SITE, c['slug'])


def esc(v):
    return html.escape(v, quote=True)


def topnav(prefix):
    links = ''.join('<a href="%sc/%s.html">%s</a>' % (prefix, c['slug'], esc(c['nav']))
                    for c in CATEGORIES)
    return links + '<a href="%sp/">All pieces</a>' % prefix


def sections_html(sections, extra=None):
    out = []
    for h, paras in sections:
        out.append('    <h2>%s</h2>' % esc(h))
        for para in paras:
            out.append('    <p>%s</p>' % esc(para))
        if extra and h in extra:
            out.append('    <p>%s</p>' % esc(extra[h]))
    return '\n'.join(out)


def card(p, prefix):
    return ('      <a class="card" href="%sp/%s.html"><img src="%s%s" alt="%s" loading="lazy" '
            'width="400" height="500"><span class="cn">%s</span><span class="co">%s</span>'
            '<span class="cp">$%s</span></a>') % (
        prefix, p['sku'], prefix, esc(p['image']), esc(p['name']), esc(p['name']),
        esc(p['origin']), format(p['price'], ','))


SHARED_CSS = """
  .bar{background:var(--ink);color:var(--paper-light);padding:14px 24px;display:flex;justify-content:space-between;align-items:center;gap:10px 22px;flex-wrap:wrap;}
  .bar a{text-decoration:none;letter-spacing:1px;font-size:13px;}
  .bar .brand{font-family:'Cormorant Garamond',serif;font-size:21px;letter-spacing:3px;color:var(--gold);}
  .bar nav{display:flex;flex-wrap:wrap;gap:6px 18px;}
  .bar nav a{opacity:.85;}
  .bar nav a:hover{color:var(--gold);opacity:1;}
  .crumb{font-size:12px;letter-spacing:1.2px;text-transform:uppercase;opacity:.6;margin-bottom:14px;}
  .crumb a{text-decoration:none;}
  .crumb a:hover{color:var(--cinnabar);}
  .cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:18px;}
  .card{display:block;text-decoration:none;background:var(--paper-light);border:1px solid rgba(42,33,26,.12);padding:12px 12px 14px;transition:border-color .2s;}
  .card:hover{border-color:var(--cinnabar);}
  .card img{width:100%;height:auto;aspect-ratio:4/5;object-fit:cover;display:block;margin-bottom:10px;background:var(--paper);}
  .card .cn{display:block;font-family:'Cormorant Garamond',serif;font-size:18px;font-weight:600;line-height:1.25;margin-bottom:4px;}
  .card .co{display:block;font-size:12px;opacity:.65;margin-bottom:6px;}
  .card .cp{display:block;font-family:'Cormorant Garamond',serif;font-size:18px;font-weight:600;color:var(--cinnabar);}
  footer{background:var(--ink);color:var(--paper-light);padding:30px 24px;font-size:12.5px;text-align:center;line-height:2;}
  footer a{color:var(--gold);}
"""


def footer_html(prefix):
    cats = ' &middot; '.join('<a href="%sc/%s.html">%s</a>' % (prefix, c['slug'], esc(c['nav']))
                             for c in CATEGORIES)
    return ('<footer>\n  <div>%s</div>\n  <div><a href="%s">Wen Gu Hall</a> &middot; <a href="%sp/">All pieces</a> &middot; '
            '<a href="%spolicies.html">Shipping &amp; Returns</a> &middot; <a href="%sja.html">日本語</a></div>\n'
            '  <div>&copy; 2026 Wen Gu Hall &middot; 86886779@qq.com &middot; WhatsApp +86 139 1004 9069</div>\n</footer>') % (
        cats, prefix or './', prefix, prefix, prefix)


PAGE = Template('''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>$title</title>
<link rel="icon" href="$favicon">
<meta name="description" content="$desc_meta">
<link rel="canonical" href="$url">
<meta property="og:type" content="product">
<meta property="og:site_name" content="Wen Gu Hall">
<meta property="og:title" content="$title">
<meta property="og:description" content="$desc_meta">
<meta property="og:url" content="$url">
<meta property="og:image" content="$ogimg">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500&family=Cormorant+Garamond:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500&family=Cormorant+Garamond:wght@400;500;600;700&display=swap" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500&family=Cormorant+Garamond:wght@400;500;600;700&display=swap"></noscript>
$ld
$ld_crumb
<style>
  :root{--ink:#1A1714;--paper:#E8DCC4;--paper-light:#F1E8D6;--cinnabar:#9E2B25;--cinnabar-dark:#7A211C;--gold:#B08D57;--text-dark:#2A211A;}
  *{margin:0;padding:0;box-sizing:border-box;}
  body{background:var(--paper);color:var(--text-dark);font-family:'Noto Sans SC',sans-serif;font-size:15px;line-height:1.75;-webkit-font-smoothing:antialiased;}
  a{color:inherit;}
$shared_css
  .wrap{max-width:1080px;margin:0 auto;padding:40px 24px 40px;display:grid;grid-template-columns:1fr 1fr;gap:48px;}
  .media img,.media video{width:100%;height:auto;display:block;margin-bottom:14px;border:1px solid rgba(42,33,26,.14);background:var(--paper-light);}
  h1{font-family:'Cormorant Garamond',serif;font-size:36px;line-height:1.2;font-weight:600;margin-bottom:14px;}
  .origin{font-size:13.5px;opacity:.7;margin-bottom:22px;}
  .price{font-family:'Cormorant Garamond',serif;font-size:32px;font-weight:600;color:var(--cinnabar);margin-bottom:6px;}
  .ship{font-size:12.5px;opacity:.6;margin-bottom:24px;}
  .desc{margin-bottom:20px;}
  .spec{font-size:13px;opacity:.75;border-top:1px solid rgba(42,33,26,.14);border-bottom:1px solid rgba(42,33,26,.14);padding:12px 0;margin-bottom:26px;}
  .btn{display:block;text-align:center;text-decoration:none;padding:15px;font-size:12.5px;letter-spacing:2px;text-transform:uppercase;margin-bottom:11px;transition:background .25s,color .25s;}
  .btn-primary{background:var(--cinnabar);color:var(--paper-light);}
  .btn-primary:hover{background:var(--cinnabar-dark);}
  .btn-alt{border:1px solid var(--text-dark);}
  .btn-alt:hover{background:var(--ink);color:var(--paper-light);}
  .note{font-size:12.5px;opacity:.6;margin-top:22px;line-height:1.7;}
  .more{max-width:1080px;margin:0 auto;padding:0 24px 70px;}
  .more .cols{display:grid;grid-template-columns:1fr 1fr;gap:10px 48px;}
  .more h2{font-family:'Cormorant Garamond',serif;font-size:24px;font-weight:600;margin:26px 0 8px;}
  .more p{margin-bottom:12px;}
  .glance{display:grid;grid-template-columns:max-content 1fr;gap:6px 18px;font-size:14px;}
  .glance dt{opacity:.6;}
  .related{margin-top:30px;border-top:1px solid rgba(42,33,26,.14);padding-top:6px;}
  .related .all{display:inline-block;margin-top:16px;color:var(--cinnabar);text-decoration:none;font-size:14px;}
  @media(max-width:820px){.wrap,.more .cols{grid-template-columns:1fr;gap:30px;}.wrap{padding-top:26px;}h1{font-size:29px;}}
</style>
</head>
<body>
<div class="bar">
  <a class="brand" href="../">问古堂 Wen Gu Hall</a>
  <nav aria-label="Categories">$topnav</nav>
</div>
<div class="wrap">
  <div class="media">
$gallery
  </div>
  <div class="info">
    <nav class="crumb" aria-label="Breadcrumb"><a href="../">Home</a> / <a href="$cat_href">$cat_name</a> / $name</nav>
    <h1>$name</h1>
    <div class="origin">$origin &middot; SKU $sku</div>
    <div class="price">$$$price</div>
    <div class="ship">Free insured worldwide shipping &middot; one of a kind, only one available</div>
    <p class="desc">$desc</p>
    $specs
    <a class="btn btn-primary" href="../?p=$sku">Add to treasure box &rarr;</a>
    <a class="btn btn-alt" href="$wa" target="_blank" rel="noopener">Ask on WhatsApp</a>
    <a class="btn btn-alt" href="$mail">Ask by email</a>
    <section class="spec" aria-label="Documentation before purchase">
      <h2>Before you purchase</h2>
      <p>Please quote SKU $sku when requesting close-up photographs, dimensions, weight, condition details, and any available maker or provenance records.</p>
      <p>Ask whether this specific piece has a laboratory report or other supporting documentation. A catalogue description is not an independent authentication certificate; material, age and maker claims should be assessed against the available evidence.</p>
      <p><a href="../policies.html">Review shipping and return terms</a> and confirm the details of this piece before payment.</p>
    </section>
  </div>
</div>
<div class="more">
  <div class="cols">
  <section>
    <h2>At a glance</h2>
    <dl class="glance">
$glance
    </dl>
$guide
  </section>
  <section>
    <h2>Ordering and shipping</h2>
$ordering
    <p>Browse more pieces like this in <a href="$cat_href">$cat_name</a>.</p>
  </section>
  </div>
  <section class="related">
    <h2>$related_title</h2>
    <div class="cards">
$related
    </div>
    <a class="all" href="$cat_href">$related_all &rarr;</a>
  </section>
</div>
$footer
$beacon
</body>
</html>
''')


def piece_notes(p, cat):
    # Sentences derived only from the product's own data, attached to the
    # matching category guidance section.
    notes = {}
    specs = p.get('specs', '')
    if cat and cat['slug'] == 'zisha-teapots':
        m = re.search(r'Capacity\s+(\d+)\s*cc', specs)
        if m:
            cc = int(m.group(1))
            use = ('solo gongfu-style brewing' if cc < 150 else
                   'two to four small cups' if cc <= 300 else 'sharing or longer brews')
            notes['Choosing a size'] = 'This pot holds about %d cc, a size that suits %s.' % (cc, use)
    elif cat and cat['slug'] == 'jade-bracelets':
        m = re.search(r'Beads?\s*~?\s*([\d.]+)', specs)
        if m:
            mm = float(m.group(1))
            feel = 'delicate' if mm <= 10 else 'bolder, statement'
            notes['Choosing size and fit'] = 'The beads on this bracelet measure about %s mm, in the %s range.' % (m.group(1), feel)
    elif cat and cat['slug'] == 'jade-pendants' and p['type'] == 'Jade Pendant':
        m = re.search(r'([\d.]+)\s*g\b', specs)
        if m:
            g = float(m.group(1))
            notes['How to choose a pendant'] = (
                'This pendant weighs %s g, a substantial piece to wear.' % m.group(1) if g > 40 else
                'This pendant weighs %s g, light enough to sit comfortably on a fine chain.' % m.group(1))
    return notes


def page(p, items):
    e = esc
    cat = cat_of(p)
    imgs = [p['image']] + p['gallery']
    gallery = '\n'.join(
        '    <img src="../%s" alt="%s" loading="lazy">' % (e(i), e(p['name'])) for i in imgs)
    if p.get('video'):
        gallery += '\n    <video src="../%s" controls preload="none" playsinline></video>' % e(p['video'])
    specs = '<div class="spec">%s</div>' % e(p['specs']) if p.get('specs') else ''
    wa_msg = 'Hello Wen Gu Hall, I am interested in %s (%s).' % (p['name'], p['sku'])
    if cat:
        cat_name, cat_href, cat_abs, term = cat['h1'], '../c/%s.html' % cat['slug'], cat_url(cat), cat['term']
        sections = [s for s in cat['guide'] if s[0] in cat['product_sections']]
        peers = [x for x in items if cat_of(x) is cat]
    else:
        cat_name, cat_href, cat_abs, term = 'All pieces', './', SITE + '/p/', p['type']
        sections = MISC.get(p['type'], [])
        peers = items
    i = peers.index(p)
    related = [peers[(i + k) % len(peers)] for k in range(1, min(5, len(peers)))]
    rows = [('Category', term), ('Material / origin', p['origin']), ('SKU', p['sku'])]
    if p.get('specs'):
        rows.append(('Measurements', p['specs']))
    media = '%d photograph%s' % (len(imgs), '' if len(imgs) == 1 else 's')
    if p.get('video'):
        media += ' and a video'
    rows += [('Price', 'US$%s' % format(p['price'], ',')), ('Availability', 'One of a kind - only one available'),
             ('On this page', media)]
    glance = '\n'.join('      <dt>%s</dt><dd>%s</dd>' % (e(k), e(v)) for k, v in rows)
    title = '%s | %s | Wen Gu Hall' % (p['name'], term)
    if len(title) > 70:
        title = '%s | %s' % (p['name'], term)
    return PAGE.substitute(
        title=e(title),
        favicon=FAVICON,
        desc_meta=e(meta_desc(p)),
        url='%s/p/%s.html' % (SITE, p['sku']),
        ogimg='%s/%s' % (SITE, p['image']),
        ld=json_ld(p),
        ld_crumb=breadcrumb_ld([('Home', SITE + '/'), (cat_name, cat_abs),
                                (p['name'], '%s/p/%s.html' % (SITE, p['sku']))]),
        shared_css=SHARED_CSS,
        topnav=topnav('../'),
        gallery=gallery,
        cat_href=cat_href,
        cat_name=e(cat_name),
        name=e(p['name']),
        origin=e(p['origin']),
        sku=e(p['sku']),
        price=format(p['price'], ','),
        desc=e(p['desc']),
        specs=specs,
        glance=glance,
        guide=sections_html(sections, piece_notes(p, cat)),
        ordering='\n'.join('    <p>%s</p>' % e(x) for x in ORDERING).replace(
            'shipping and returns terms', '<a href="../policies.html">shipping and returns terms</a>'),
        related_title=e('More %s' % (cat['nav'].lower() if cat else 'pieces')),
        related='\n'.join(card(x, '../') for x in related),
        related_all=e('See all %d in %s' % (len(peers), cat_name) if cat else 'See all %d pieces' % len(items)),
        wa='https://wa.me/8613910049069?text=' + e(wa_msg.replace(' ', '%20')),
        mail='mailto:86886779@qq.com?subject=Enquiry:%%20%s%%20(%s)' % (
            p['name'].replace(' ', '%20'), p['sku']),
        footer=footer_html('../'),
        beacon=BEACON,
    )


CAT_PAGE = Template('''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>$title</title>
<link rel="icon" href="$favicon">
<meta name="description" content="$desc_meta">
<link rel="canonical" href="$url">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Wen Gu Hall">
<meta property="og:title" content="$title">
<meta property="og:description" content="$desc_meta">
<meta property="og:url" content="$url">
<meta property="og:image" content="$ogimg">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500&family=Cormorant+Garamond:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500&family=Cormorant+Garamond:wght@400;500;600;700&display=swap" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500&family=Cormorant+Garamond:wght@400;500;600;700&display=swap"></noscript>
$ld
$ld_crumb
<style>
  :root{--ink:#1A1714;--paper:#E8DCC4;--paper-light:#F1E8D6;--cinnabar:#9E2B25;--cinnabar-dark:#7A211C;--gold:#B08D57;--text-dark:#2A211A;}
  *{margin:0;padding:0;box-sizing:border-box;}
  body{background:var(--paper);color:var(--text-dark);font-family:'Noto Sans SC',sans-serif;font-size:15px;line-height:1.75;-webkit-font-smoothing:antialiased;}
  a{color:inherit;}
$shared_css
  main{max-width:1080px;margin:0 auto;padding:36px 24px 70px;}
  h1{font-family:'Cormorant Garamond',serif;font-size:40px;line-height:1.15;font-weight:600;margin-bottom:12px;}
  .lead{max-width:760px;font-size:15.5px;margin-bottom:8px;}
  .count{font-size:13px;opacity:.65;margin-bottom:28px;}
  .guide{max-width:760px;margin-top:48px;}
  .guide h2{font-family:'Cormorant Garamond',serif;font-size:25px;font-weight:600;margin:26px 0 8px;}
  .guide p{margin-bottom:12px;}
  .others{margin-top:40px;border-top:1px solid rgba(42,33,26,.14);padding-top:18px;font-size:14px;}
  .others a{color:var(--cinnabar);text-decoration:none;margin-right:18px;white-space:nowrap;}
  @media(max-width:820px){h1{font-size:31px;}}
</style>
</head>
<body>
<div class="bar">
  <a class="brand" href="../">问古堂 Wen Gu Hall</a>
  <nav aria-label="Categories">$topnav</nav>
</div>
<main>
  <nav class="crumb" aria-label="Breadcrumb"><a href="../">Home</a> / $h1</nav>
  <h1>$h1</h1>
  <p class="lead">$intro</p>
  <div class="count">$count</div>
  <div class="cards">
$cards
  </div>
  <section class="guide">
$guide
  </section>
  <nav class="others" aria-label="Other categories">More from Wen Gu Hall: $others</nav>
</main>
$footer
$beacon
</body>
</html>
''')


def cat_page(c, items):
    e = esc
    members = [p for p in items if cat_of(p) is c]
    url = cat_url(c)
    prices = [p['price'] for p in members]
    count = '%d piece%s, each one of a kind &middot; US$%s to US$%s &middot; free insured worldwide shipping' % (
        len(members), '' if len(members) == 1 else 's', format(min(prices), ','), format(max(prices), ','))
    ld = ld_script({
        '@context': 'https://schema.org/', '@type': 'CollectionPage',
        'name': c['h1'], 'url': url, 'description': c['meta'], 'inLanguage': 'en',
        'isPartOf': {'@type': 'WebSite', 'name': 'Wen Gu Hall', 'url': SITE + '/'},
        'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(members),
                       'itemListElement': [{'@type': 'ListItem', 'position': i + 1,
                                            'url': '%s/p/%s.html' % (SITE, p['sku']), 'name': p['name']}
                                           for i, p in enumerate(members)]}})
    others = ''.join('<a href="%s.html">%s</a>' % (o['slug'], e(o['nav'])) for o in CATEGORIES if o is not c)
    others += '<a href="../p/">All pieces</a>'
    return CAT_PAGE.substitute(
        title=e('%s | Wen Gu Hall' % c['title']),
        favicon=FAVICON,
        desc_meta=e(c['meta']),
        url=url,
        ogimg='%s/%s' % (SITE, members[0]['image']),
        ld=ld,
        ld_crumb=breadcrumb_ld([('Home', SITE + '/'), (c['h1'], url)]),
        shared_css=SHARED_CSS,
        topnav=topnav('../'),
        h1=e(c['h1']),
        intro=e(c['intro']),
        count=count,
        cards='\n'.join(card(p, '../') for p in members),
        guide=sections_html(c['guide'] + [BUYING]),
        others=others,
        footer=footer_html('../'),
        beacon=BEACON,
    )


HUB = Template('''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>All Pieces | Wen Gu Hall</title>
<link rel="icon" href="$favicon">
<meta name="description" content="Every piece currently offered by Wen Gu Hall - Hetian jade, Yixing zisha teaware, Chinese porcelain, ink painting and calligraphy, each with its own page.">
<link rel="canonical" href="https://wenguhall.com/p/">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500&family=Cormorant+Garamond:wght@400;600&display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500&family=Cormorant+Garamond:wght@400;600&display=swap" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500&family=Cormorant+Garamond:wght@400;600&display=swap"></noscript>
<style>
  *{margin:0;padding:0;box-sizing:border-box;}
  body{background:#E8DCC4;color:#2A211A;font-family:'Noto Sans SC',sans-serif;font-size:15px;line-height:1.8;}
  .bar{background:#1A1714;padding:16px 24px;}
  .bar a{color:#B08D57;text-decoration:none;font-family:'Cormorant Garamond',serif;font-size:21px;letter-spacing:3px;}
  main{max-width:840px;margin:0 auto;padding:40px 24px 70px;}
  h1{font-family:'Cormorant Garamond',serif;font-size:36px;font-weight:600;margin-bottom:8px;}
  .sub{opacity:.65;font-size:13.5px;margin-bottom:34px;}
  h2{font-family:'Cormorant Garamond',serif;font-size:23px;font-weight:600;margin:30px 0 10px;border-bottom:1px solid rgba(42,33,26,.16);padding-bottom:6px;}
  ul{list-style:none;}
  li{display:flex;justify-content:space-between;gap:16px;padding:7px 0;border-bottom:1px solid rgba(42,33,26,.07);font-size:14px;}
  li a{color:inherit;text-decoration:none;}
  li a:hover{color:#9E2B25;}
  li span{font-family:'Cormorant Garamond',serif;font-weight:600;white-space:nowrap;}
  .cats{font-size:14px;margin:-18px 0 10px;}
  .cats a{color:#9E2B25;text-decoration:none;margin-right:14px;white-space:nowrap;}
</style>
</head>
<body>
<div class="bar"><a href="../">问古堂 Wen Gu Hall</a></div>
<main>
  <h1>All pieces</h1>
  <div class="sub">$count pieces, each one of a kind. Free insured worldwide shipping.</div>
  <nav class="cats" aria-label="Categories">Shop by category: $cats</nav>
$blocks
</main>
$beacon
</body>
</html>
''')


def hub(items):
    groups = {}
    for p in items:
        groups.setdefault(p['type'], []).append(p)
    blocks = []
    for t in sorted(groups):
        rows = '\n'.join(
            '    <li><a href="%s.html">%s</a> <span>$%s</span></li>' % (
                p['sku'], html.escape(p['name']), format(p['price'], ','))
            for p in groups[t])
        blocks.append('  <h2>%s</h2>\n  <ul>\n%s\n  </ul>' % (html.escape(t), rows))
    cats = ''.join('<a href="../c/%s.html">%s</a>' % (c['slug'], esc(c['nav'])) for c in CATEGORIES)
    return HUB.substitute(blocks='\n'.join(blocks), count=len(items), cats=cats,
                          favicon=FAVICON, beacon=BEACON)


def sitemap(items):
    today = datetime.date.today().isoformat()
    urls = [(SITE + '/', '1.0'), (SITE + '/ja.html', '0.9'), (SITE + '/p/', '0.8'),
            (SITE + '/policies.html', '0.3'), (SITE + '/policies-ja.html', '0.3')]
    urls += [(cat_url(c), '0.8') for c in CATEGORIES]
    urls += [('%s/p/%s.html' % (SITE, p['sku']), '0.7') for p in items]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, pr in urls:
        out.append('  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>'
                   % (u, today, pr))
    out.append('</urlset>')
    return '\n'.join(out) + '\n'


def homepage_links(items, lang):
    """Category links injected into index.html / ja.html between markers."""
    counts = dict((c['slug'], sum(1 for p in items if cat_of(p) is c)) for c in CATEGORIES)
    if lang == 'ja':
        label = lambda c: JA_LABELS[c['slug']]
        allp = '全%d点の一覧' % len(items)
    else:
        label = lambda c: c['h1']
        allp = 'All %d pieces' % len(items)
    block = ''.join('<a href="c/%s.html">%s <span>%d</span></a>' % (c['slug'], esc(label(c)), counts[c['slug']])
                    for c in CATEGORIES) + '<a href="p/">%s</a>' % allp
    shop = ''.join('<li><a href="c/%s.html">%s</a></li>' % (c['slug'], esc(label(c))) for c in CATEGORIES)
    return {'catlinks': block, 'shoplinks': shop}


def inject(path, blocks):
    src = io.open(path, encoding='utf-8').read()
    for name, content in blocks.items():
        pat = re.compile(r'(<!--seo:%s-->).*?(<!--/seo:%s-->)' % (name, name), re.S)
        if not pat.search(src):
            raise SystemExit('marker <!--seo:%s--> missing in %s' % (name, path))
        src = pat.sub(lambda m: m.group(1) + content + m.group(2), src)
    io.open(path, 'w', encoding='utf-8').write(src)


def main():
    items = parse_products(os.path.join(ROOT, 'index.html'))
    for d in (OUT, CAT_OUT):
        if not os.path.isdir(d):
            os.makedirs(d)
    for p in items:
        io.open(os.path.join(OUT, p['sku'] + '.html'), 'w', encoding='utf-8').write(page(p, items))
    for c in CATEGORIES:
        io.open(os.path.join(CAT_OUT, c['slug'] + '.html'), 'w', encoding='utf-8').write(cat_page(c, items))
    io.open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(hub(items))
    io.open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(sitemap(items))
    inject(os.path.join(ROOT, 'index.html'), homepage_links(items, 'en'))
    inject(os.path.join(ROOT, 'ja.html'), homepage_links(items, 'ja'))
    print('generated %d product pages + %d category pages + hub + sitemap' % (len(items), len(CATEGORIES)))


if __name__ == '__main__':
    main()
