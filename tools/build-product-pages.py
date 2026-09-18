# -*- coding: utf-8 -*-
"""Generate one static page per product from the product array in index.html.

Run from the repo root:  python tools/build-product-pages.py
Output: p/{SKU}.html for every product, p/index.html (crawlable hub of all
pieces) and a refreshed sitemap.xml.
"""
import io
import os
import re
import html
import datetime
from string import Template

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://wenguhall.com'
OUT = os.path.join(ROOT, 'p')
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


def meta_desc(p):
    return '%s US$%s, free insured worldwide shipping from Wen Gu Hall.' % (
        p['desc'].rstrip() + ('' if p['desc'].rstrip().endswith('.') else '.'),
        format(p['price'], ','))[:300]


def json_ld(p):
    imgs = [p['image']] + p['gallery']
    q = lambda s: s.replace('\\', '').replace('"', '\\"')
    return (
        '{"@context":"https://schema.org/","@type":"Product",'
        '"name":"%s","sku":"%s","category":"%s","image":[%s],"description":"%s",'
        '"brand":{"@type":"Brand","name":"Wen Gu Hall"},'
        '"offers":{"@type":"Offer","url":"%s/p/%s.html","priceCurrency":"USD","price":"%d",'
        '"availability":"https://schema.org/InStock",'
        '"itemCondition":"https://schema.org/NewCondition",'
        '"seller":{"@type":"Organization","name":"Wen Gu Hall"}}}'
    ) % (q(p['name']), p['sku'], q(p['type']),
         ','.join('"%s/%s"' % (SITE, i) for i in imgs),
         q(meta_desc(p)), SITE, p['sku'], p['price'])


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
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500&family=Cormorant+Garamond:wght@400;500;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">$ld</script>
<style>
  :root{--ink:#1A1714;--paper:#E8DCC4;--paper-light:#F1E8D6;--cinnabar:#9E2B25;--cinnabar-dark:#7A211C;--gold:#B08D57;--text-dark:#2A211A;}
  *{margin:0;padding:0;box-sizing:border-box;}
  body{background:var(--paper);color:var(--text-dark);font-family:'Noto Sans SC',sans-serif;font-size:15px;line-height:1.75;-webkit-font-smoothing:antialiased;}
  a{color:inherit;}
  .bar{background:var(--ink);color:var(--paper-light);padding:16px 24px;display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;}
  .bar a{text-decoration:none;letter-spacing:1px;font-size:13px;}
  .bar .brand{font-family:'Cormorant Garamond',serif;font-size:21px;letter-spacing:3px;color:var(--gold);}
  .wrap{max-width:1080px;margin:0 auto;padding:40px 24px 70px;display:grid;grid-template-columns:1fr 1fr;gap:48px;}
  .media img,.media video{width:100%;height:auto;display:block;margin-bottom:14px;border:1px solid rgba(42,33,26,.14);background:var(--paper-light);}
  .crumb{font-size:12px;letter-spacing:1.5px;text-transform:uppercase;opacity:.55;margin-bottom:14px;}
  .crumb a{text-decoration:none;}
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
  footer{background:var(--ink);color:var(--paper-light);padding:30px 24px;font-size:12.5px;text-align:center;line-height:2;}
  footer a{color:var(--gold);}
  @media(max-width:820px){.wrap{grid-template-columns:1fr;gap:30px;padding-top:26px;}h1{font-size:29px;}}
</style>
</head>
<body>
<div class="bar">
  <a class="brand" href="../">问古堂 Wen Gu Hall</a>
  <a href="../">&larr; All pieces</a>
</div>
<div class="wrap">
  <div class="media">
$gallery
  </div>
  <div class="info">
    <div class="crumb"><a href="../">Wen Gu Hall</a> / $type</div>
    <h1>$name</h1>
    <div class="origin">$origin &middot; SKU $sku</div>
    <div class="price">$$$price</div>
    <div class="ship">Free insured worldwide shipping &middot; one of a kind, only one available</div>
    <p class="desc">$desc</p>
    $specs
    <a class="btn btn-primary" href="../?p=$sku">Add to treasure box &rarr;</a>
    <a class="btn btn-alt" href="$wa" target="_blank" rel="noopener">Ask on WhatsApp</a>
    <a class="btn btn-alt" href="$mail">Ask by email</a>
    <p class="note">Every piece is hand-picked and traceable to its origin. Questions about size, weight or condition are welcome before you buy &mdash; we answer within a day.</p>
  </div>
</div>
<footer>
  <div><a href="../">Wen Gu Hall</a> &middot; <a href="../policies.html">Shipping &amp; Returns</a> &middot; <a href="../ja.html">日本語</a></div>
  <div>&copy; 2026 Wen Gu Hall &middot; 86886779@qq.com &middot; WhatsApp +86 139 1004 9069</div>
</footer>
$beacon
</body>
</html>
''')


def page(p):
    e = lambda s: html.escape(s, quote=True)
    imgs = [p['image']] + p['gallery']
    gallery = '\n'.join(
        '    <img src="../%s" alt="%s" loading="lazy">' % (e(i), e(p['name'])) for i in imgs)
    if p.get('video'):
        gallery += '\n    <video src="../%s" controls preload="none" playsinline></video>' % e(p['video'])
    specs = '<div class="spec">%s</div>' % e(p['specs']) if p.get('specs') else ''
    wa_msg = 'Hello Wen Gu Hall, I am interested in %s (%s).' % (p['name'], p['sku'])
    return PAGE.substitute(
        title=e('%s | Wen Gu Hall' % p['name']),
        favicon=FAVICON,
        desc_meta=e(meta_desc(p)),
        url='%s/p/%s.html' % (SITE, p['sku']),
        ogimg='%s/%s' % (SITE, p['image']),
        ld=json_ld(p),
        gallery=gallery,
        type=e(p['type']),
        name=e(p['name']),
        origin=e(p['origin']),
        sku=e(p['sku']),
        price=format(p['price'], ','),
        desc=e(p['desc']),
        specs=specs,
        wa='https://wa.me/8613910049069?text=' + e(wa_msg.replace(' ', '%20')),
        mail='mailto:86886779@qq.com?subject=Enquiry:%%20%s%%20(%s)' % (
            p['name'].replace(' ', '%20'), p['sku']),
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
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500&family=Cormorant+Garamond:wght@400;600&display=swap" rel="stylesheet">
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
</style>
</head>
<body>
<div class="bar"><a href="../">问古堂 Wen Gu Hall</a></div>
<main>
  <h1>All pieces</h1>
  <div class="sub">$count pieces, each one of a kind. Free insured worldwide shipping.</div>
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
    return HUB.substitute(blocks='\n'.join(blocks), count=len(items),
                          favicon=FAVICON, beacon=BEACON)


def sitemap(items):
    today = datetime.date.today().isoformat()
    urls = [(SITE + '/', '1.0'), (SITE + '/ja.html', '0.9'), (SITE + '/p/', '0.8'),
            (SITE + '/policies.html', '0.3'), (SITE + '/policies-ja.html', '0.3')]
    urls += [('%s/p/%s.html' % (SITE, p['sku']), '0.7') for p in items]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, pr in urls:
        out.append('  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>'
                   % (u, today, pr))
    out.append('</urlset>')
    return '\n'.join(out) + '\n'


def main():
    items = parse_products(os.path.join(ROOT, 'index.html'))
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    for p in items:
        io.open(os.path.join(OUT, p['sku'] + '.html'), 'w', encoding='utf-8').write(page(p))
    io.open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(hub(items))
    io.open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(sitemap(items))
    print('generated %d product pages + hub + sitemap' % len(items))


if __name__ == '__main__':
    main()
