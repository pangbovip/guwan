# -*- coding: utf-8 -*-
"""Build Google Merchant Center feeds (feed.xml + feed.tsv) from index.html.

Free-listings target: United States only, prices and shipping in USD.
Website still ships worldwide via PayPal; non-USD free-listing countries
(KR, JP, EU, etc.) need separate local-currency feeds later.

Run from repo root:
  python3 tools/build-merchant-feed.py
"""
import os, csv, importlib.util
from xml.sax.saxutils import escape

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://wenguhall.com'

# Free standard shipping to the US. Matches policies.html:
# dispatch 3-5 business days; North America transit 7-15 business days.
# Shipping currency MUST match product price currency (USD).
SHIP_COUNTRIES = ['US']
SHIP_PRICE = '0.00 USD'
MIN_HANDLING, MAX_HANDLING = 3, 5
MIN_TRANSIT, MAX_TRANSIT = 7, 15

spec = importlib.util.spec_from_file_location(
    'b', os.path.join(REPO, 'tools/build-product-pages.py'))
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
items = b.parse_products(os.path.join(REPO, 'index.html'))


def gpc(p):
    t, n = p['type'], p['name'].lower()
    if t == 'Zisha Teaware':
        return '2169' if 'mug' in n else '652'
    if t == 'Porcelain':
        return '3498' if ('bowl' in n and 'tea bowl' not in n) else '6049'
    return {
        'Jade Bracelet': '191', 'Jade Pendant': '192', 'Jade Necklace': '196',
        'Jade Jewelry': '200', 'Raw Jade': '218', 'Calligraphy': '500044',
        'Ink Painting': '500044', 'Carved Gourd': '696',
    }[t]


APPAREL = {'191', '192', '196', '200'}
EXCLUDE_SKUS = {'J07'}  # huanghuali / CITES — do not list
COLOURS = [
    ('spinach-green', 'Green'), ('blue-green', 'Blue/Green'),
    ('deep green', 'Green'), ('dark-green', 'Green'),
    ('black-and-white', 'Black/White'), ('celadon', 'Celadon'),
    ('white', 'White'), ('green', 'Green'), ('black', 'Black'),
    ('grey', 'Grey'), ('turquoise', 'Turquoise'), ('amber', 'Honey'),
    ('beeswax', 'Yellow'), ('dark jade', 'Black'), ('jadeite', 'Green'),
    ('marbled', 'Multicolor'),
]
COLOR_OVERRIDES = {
    'J02': 'Honey', 'J06': 'Black', 'J08': 'White', 'J10': 'Yellow',
    'J16': 'Green', 'J28': 'Brown', 'J29': 'Multicolor',
}


def colour(p):
    sku = p.get('sku') or p.get('id') or ''
    if sku in COLOR_OVERRIDES:
        return COLOR_OVERRIDES[sku]
    n = p['name'].lower()
    for k, v in COLOURS:
        if k in n:
            return v
    return ''


def product_type(p):
    c = b.cat_of(p)
    return '%s > %s' % (c['h1'] if c else 'All pieces', p['type'])


def title(p):
    t = p['name']
    o = p['origin']
    if o and o.lower() not in t.lower():
        t2 = '%s - %s' % (t, o)
        if len(t2) <= 150:
            t = t2
    return t[:150]


def description(p):
    parts = [p['desc'].strip()]
    parts.append('Origin / material: %s.' % p['origin'])
    if p.get('specs'):
        parts.append('Measurements: %s.' % p['specs'])
    parts.append('SKU %s. One of a kind - only one available.' % p['sku'])
    return ' '.join(parts)[:5000]


def imgs(p):
    real = [i for i in p['gallery'] if '-real' in i]
    other = [i for i in p['gallery'] if '-real' not in i]
    return real + other + [p['image']] if real else [p['image']] + p['gallery']


def tsv_shipping():
    # country:region:service:price:min_handling:max_handling:min_transit:max_transit
    parts = []
    for cc in SHIP_COUNTRIES:
        parts.append('%s:::%s:%d:%d:%d:%d' % (
            cc, SHIP_PRICE, MIN_HANDLING, MAX_HANDLING, MIN_TRANSIT, MAX_TRANSIT))
    return ','.join(parts)


def xml_shipping_blocks():
    blocks = []
    for cc in SHIP_COUNTRIES:
        blocks.append(
            '  <g:shipping>\n'
            '    <g:country>%s</g:country>\n'
            '    <g:price>%s</g:price>\n'
            '    <g:min_handling_time>%d</g:min_handling_time>\n'
            '    <g:max_handling_time>%d</g:max_handling_time>\n'
            '    <g:min_transit_time>%d</g:min_transit_time>\n'
            '    <g:max_transit_time>%d</g:max_transit_time>\n'
            '  </g:shipping>' % (
                cc, SHIP_PRICE, MIN_HANDLING, MAX_HANDLING,
                MIN_TRANSIT, MAX_TRANSIT))
    return '\n'.join(blocks)


COLS = [
    'id', 'title', 'description', 'link', 'image_link', 'additional_image_link',
    'video_link', 'availability', 'price', 'condition', 'brand',
    'identifier_exists', 'google_product_category', 'product_type',
    'color', 'gender', 'age_group', 'shipping',
]
rows = []
for p in items:
    if p['sku'] in EXCLUDE_SKUS:
        continue
    g = gpc(p)
    rows.append({
        'id': p['sku'],
        'title': title(p),
        'description': description(p),
        'link': '%s/p/%s.html' % (SITE, p['sku']),
        'image_link': '%s/%s' % (SITE, imgs(p)[0]),
        'additional_image_link': ','.join(
            '%s/%s' % (SITE, i) for i in imgs(p)[1:11]),
        'video_link': ('%s/%s' % (SITE, p['video'])) if p.get('video') else '',
        'availability': 'in_stock',
        'price': '%.2f USD' % p['price'],
        'condition': 'new',
        'brand': 'Wen Gu Hall',
        'identifier_exists': 'no',
        'google_product_category': g,
        'product_type': product_type(p),
        'color': colour(p) if g in APPAREL else '',
        'gender': 'unisex' if g in APPAREL else '',
        'age_group': 'adult' if g in APPAREL else '',
        'shipping': tsv_shipping(),
    })

tsv_path = os.path.join(REPO, 'feed.tsv')
with open(tsv_path, 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(
        f, COLS, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
    w.writeheader()
    w.writerows(rows)

def x(v):
    return escape(v)

out = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">',
    '<channel>',
    '<title>Wen Gu Hall</title>',
    '<link>%s/</link>' % SITE,
    '<description>Wen Gu Hall product feed (USD; free listings target: United States)</description>',
]
for r in rows:
    out.append('<item>')
    out.append('  <g:id>%s</g:id>' % x(r['id']))
    out.append('  <title>%s</title>' % x(r['title']))
    out.append('  <description>%s</description>' % x(r['description']))
    out.append('  <link>%s</link>' % x(r['link']))
    out.append('  <g:image_link>%s</g:image_link>' % x(r['image_link']))
    for a in filter(None, r['additional_image_link'].split(',')):
        out.append('  <g:additional_image_link>%s</g:additional_image_link>' % x(a))
    for k in [
        'video_link', 'availability', 'price', 'condition', 'brand',
        'identifier_exists', 'google_product_category', 'product_type',
        'color', 'gender', 'age_group',
    ]:
        if r[k]:
            out.append('  <g:%s>%s</g:%s>' % (k, x(r[k]), k))
    out.append(xml_shipping_blocks())
    out.append('</item>')
out += ['</channel>', '</rss>']

xml_path = os.path.join(REPO, 'feed.xml')
open(xml_path, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('rows', len(rows))
print('ship_countries', ','.join(SHIP_COUNTRIES))
print('wrote', xml_path)
print('wrote', tsv_path)
