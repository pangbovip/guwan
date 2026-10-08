# -*- coding: utf-8 -*-
"""Category definitions and category-level copy used by build-product-pages.py.

Copy here is generic, category-level guidance only. Facts about a specific
piece (material, origin, size, weight) must come from the product data in
index.html - do not add per-piece claims here.
"""

# Each category maps one or more product `type` values to a landing page.
# Types not listed here (e.g. Raw Jade, Carved Gourd) only appear on /p/.
CATEGORIES = [
    dict(
        slug='zisha-teapots',
        types=['Zisha Teaware'],
        nav='Zisha Teapots',
        term='Yixing Zisha Teapots',
        title='Yixing Zisha Teapots - Handmade Clay Teapots',
        h1='Yixing Zisha Teapots',
        meta='Handmade Yixing zisha teapots and teaware from Jiangsu: duanni, dahongpao and shipiao pots, each one of a kind. Free insured worldwide shipping.',
        intro='Unglazed teapots and lidded mugs thrown and moulded from Yixing zisha clay in Jiangsu province. Every pot below is a single piece with its own page, photographs and, where we have measured it, its capacity.',
        guide=[
            ('Why zisha clay', [
                'Zisha - literally "purple sand" - is the iron-rich clay mined around Yixing in Jiangsu province, and teapots made from it have been the companions of Chinese tea drinkers for centuries. Because the clay is fired without a glaze it stays slightly porous: with regular use a pot slowly takes on a soft sheen, and many drinkers feel it rounds out the tea brewed in it.',
            ]),
            ('Clay and colour', [
                'Zisha is a family of clays rather than a single material. Purple-brown zini is the classic; hongni fires to a brighter red; duanni is a buff to yellowish clay that often shows fine speckles. Firing temperature and kiln atmosphere also shift the colour, so two pots made from the same clay can look quite different.',
            ]),
            ('Choosing a size', [
                'Capacity matters more than most first-time buyers expect. Pots under about 150 cc suit solo gongfu-style brewing with many short infusions; 150-300 cc serves two to four small cups; larger pots and lidded mugs suit sharing or longer, everyday brews.',
            ]),
            ('Shape and decoration', [
                'Classic forms such as the shipiao (stone ladle), the pear form and the bamboo-node cylinder pour differently and suit different teas, while carved, slip-painted or gilt pots are as much for display as for brewing. When you receive a pot, check that the lid sits snugly and the spout pours a clean, unbroken stream.',
            ]),
            ('Caring for a zisha teapot', [
                'Rinse a new pot with hot water before first use, never use detergent, and let it dry completely with the lid off. Many drinkers dedicate one pot to one family of tea - oolong, pu-erh or black tea - so that flavours do not mix in the porous clay.',
            ]),
        ],
        product_sections=('Choosing a size', 'Caring for a zisha teapot'),
    ),
    dict(
        slug='jade-pendants',
        types=['Jade Pendant', 'Jade Necklace', 'Jade Jewelry'],
        nav='Jade Pendants',
        term='Jade Pendants & Amulets',
        title='Jade Pendants, Guanyin Amulets & Jewelry',
        h1='Jade Pendants, Guanyin Amulets & Jewelry',
        meta='Hand-carved Hotan and Russian nephrite pendants - Guanyin, Buddha, safety buckle and cicada - plus amber, turquoise and jade jewelry. Free insured shipping.',
        intro='Carved and plain pendants in nephrite from Hotan and Russia, a jadeite Guanyin from Myanmar, Baltic amber and turquoise, together with a jade bead necklace and a jade gourd ring. Each piece is one of a kind and has its own page with photographs and, where measured, size and weight.',
        guide=[
            ('Pendants that carry a wish', [
                'Carved pendants are among the oldest forms of Chinese jade jewellery, and many carry a wish as well as a design. Guanyin, the bodhisattva of compassion, is traditionally worn for protection; the round ping\'an kou or "safety buckle" stands for peace and safe travels; the gourd (hulu) is associated with blessings and good fortune; the cicada with renewal. A plain tag lets the material speak for itself.',
            ]),
            ('Nephrite, jadeite, amber and turquoise', [
                'Most pendants here are nephrite, the tough, slightly waxy stone that Chinese carvers have worked for millennia; Hotan in Xinjiang is its most famous source, and fine white nephrite is prized for an even colour and an oily lustre. Jadeite is a different mineral, usually glassier and often brighter green. Baltic amber is fossilised tree resin, very light and warm in the hand, and turquoise is a soft, porous stone.',
            ]),
            ('How to choose a pendant', [
                'Look at colour and texture in natural daylight, then at the carving: crisp, confident lines and a well-finished back are signs of care. Think about size and weight too - a pendant over about 40 g is a substantial piece to wear every day, while lighter pieces sit comfortably on a fine chain.',
            ]),
            ('Caring for jade and amber', [
                'Hang pendants on a cord or chain that suits their weight, and take them off for sport and sleep. Store each piece in its own pouch so harder stones cannot scratch softer ones. Amber and turquoise are softer and more porous than jade, so keep them away from perfume, oils and heat; wipe all pieces with a soft, dry cloth.',
            ]),
        ],
        product_sections=('How to choose a pendant', 'Caring for jade and amber'),
    ),
    dict(
        slug='jade-bracelets',
        types=['Jade Bracelet'],
        nav='Bracelets',
        term='Jade & Bead Bracelets',
        title='Jade Bead Bracelets - Hotan Nephrite, Amber & Rosewood',
        h1='Jade & Natural Bead Bracelets',
        meta='Bead bracelets in Hotan and Russian nephrite - white, celadon, green, black and qinghua jade - plus Baltic amber and huanghuali rosewood. Free insured shipping.',
        intro='Bead bracelets in nephrite jade from Hotan and Russia, a chatoyant green stone from Myanmar, Baltic amber and Hainan huanghuali rosewood. Each bracelet is one of a kind; bead size and weight are listed wherever we have measured them.',
        guide=[
            ('Everyday natural materials', [
                'A bead bracelet is the easiest way to live with natural materials every day. Most bracelets here are nephrite jade in white, celadon, green, black and qinghua (black-and-white) colours, alongside amber and wood. The material and source of each bracelet are stated on its own page.',
            ]),
            ('Nephrite, amber and wood', [
                'Nephrite is tough and slightly waxy to the touch, which is why it has been carved and worn in China for thousands of years. Amber is fossilised tree resin: very light, warm in the hand and much softer than stone. Huanghuali is a dense, fragrant rosewood whose grain deepens with handling. Dense stone beads feel noticeably heavier on the wrist than amber or wood of the same size.',
            ]),
            ('Choosing size and fit', [
                'Measure your wrist snugly with a strip of paper and add about 1-2 cm for a comfortable fit. Beads of 8-10 mm read as delicate; 12-16 mm make a bolder statement and suit larger wrists. Ask us for the inner circumference of a bracelet before ordering if fit is critical.',
            ]),
            ('Caring for a bead bracelet', [
                'Take bracelets off for sport, gardening and heavy cleaning, and store them separately so hard stone beads cannot scratch softer amber or wood. Keep amber and wood away from heat, perfume and solvents, and wipe all beads with a soft, dry cloth. Re-stringing every few years keeps an everyday bracelet secure.',
            ]),
        ],
        product_sections=('Choosing size and fit', 'Caring for a bead bracelet'),
    ),
    dict(
        slug='porcelain-teacups',
        types=['Porcelain'],
        nav='Porcelain Teacups',
        term='Porcelain Teacups',
        title='Jingdezhen Porcelain Teacups & Tea Bowls',
        h1='Porcelain Teacups & Tea Bowls',
        meta='Hand-painted Jingdezhen porcelain teacups and tea bowls - blue-and-white, famille rose, teadust glaze - for gongfu tea. Free insured worldwide shipping.',
        intro='Teacups and tea bowls, most of them from Jingdezhen in Jiangxi province, in blue-and-white, underglaze red, famille rose enamels and monochrome glazes, plus one handmade studio tea bowl. Each piece is one of a kind with its own page and photographs.',
        guide=[
            ('Jingdezhen porcelain', [
                'Jingdezhen in Jiangxi province has been China\'s best-known porcelain town for around a thousand years. Porcelain is fired at a high temperature until the body becomes dense and glassy, which is why a fine cup feels light, rings when tapped and does not hold on to flavours - ideal for tasting delicate teas.',
            ]),
            ('Decoration styles', [
                'Blue-and-white is painted in cobalt under the glaze; underglaze red uses copper and is harder to fire evenly. Famille rose (fencai) enamels are painted over the fired glaze and fired again at a lower temperature, giving soft pinks and shading, and gilt rims or raised gold need a further firing. Monochromes such as teadust glaze rely on the glaze itself for colour.',
            ]),
            ('Choosing a teacup', [
                'For gongfu tea, small cups let you taste each infusion while it is hot; wider bowls suit whisked tea or simply look beautiful on the tea table. A thin wall shows off the colour of the tea and feels delicate on the lip, while a thicker wall holds heat longer. Turn a cup over: the foot and any mark or seal show how carefully it was finished.',
            ]),
            ('Caring for porcelain', [
                'Wash by hand in warm water with a soft cloth. Keep enamelled and gilt pieces out of the dishwasher and microwave, and avoid abrasive pads that can wear decoration. Warming a cup with hot water before pouring boiling tea helps avoid thermal shock.',
            ]),
        ],
        product_sections=('Choosing a teacup', 'Caring for porcelain'),
    ),
    dict(
        slug='calligraphy-ink-painting',
        types=['Calligraphy', 'Ink Painting'],
        nav='Calligraphy & Painting',
        term='Calligraphy & Ink Painting',
        title='Chinese Calligraphy Scrolls & Ink Paintings',
        h1='Chinese Calligraphy & Ink Painting',
        meta='Brush-written Chinese calligraphy - a running-script blessing scroll and a four-panel screen - and a hand-painted ink and colour painting. Free shipping.',
        intro='A small collection of brush-written calligraphy and hand-painted ink painting: a running-script scroll with an auspicious blessing, a mounted four-panel calligraphy screen and a New Year painting of scholar\'s objects in ink and colour.',
        guide=[
            ('Brush, ink and a single stroke', [
                'Chinese calligraphy and ink painting share the same tools - brush, ink, and paper or silk - and the same belief that a single, unrepeatable stroke reveals the hand behind it. That is why a brushed work cannot be corrected once the ink touches the paper, and why collectors value the rhythm and confidence of the line as much as the words or image themselves.',
            ]),
            ('Script styles and formats', [
                'Running script (xingshu) sits between careful regular script and free cursive, so the characters flow while staying readable. Hanging scrolls are mounted on silk or paper with a rod at the bottom; screens and panel sets divide a longer text or several images into parts that can stand or hang together.',
            ]),
            ('Choosing a work', [
                'Think about where the work will live: vertical hanging scrolls suit narrow walls and entrances, screens can divide a room, and a small painting brightens a study or tea corner. Ask us about the text, the meaning of the characters and the measurements of the mounted work before you buy.',
            ]),
            ('Caring for scrolls and paintings', [
                'Hang works away from direct sunlight, radiators and damp walls. Roll hanging scrolls loosely and never fold them; store them in a dry place with stable humidity, and handle paper with clean, dry hands. Rotating what you display also protects a work from long exposure to light.',
            ]),
        ],
        product_sections=('Choosing a work', 'Caring for scrolls and paintings'),
    ),
]

# Japanese labels for links from ja.html (the landing pages themselves are English).
JA_LABELS = {
    'zisha-teapots': '紫砂急須',
    'jade-pendants': '翡翠ペンダント',
    'jade-bracelets': '翡翠ブレスレット',
    'porcelain-teacups': '磁器の茶杯・茶碗',
    'calligraphy-ink-painting': '書道・水墨画',
}

# Generic guidance for product types that have no landing page of their own.
MISC = {
    'Raw Jade': [
        ('About raw jade', [
            'A raw pebble lets you see nephrite before any carving: its skin, colour and texture. Look at it in natural daylight, turn it to see the skin and any inclusions, and keep it on a soft surface - nephrite is tough, but polished faces can still be scratched by harder stones and metal.',
        ]),
    ],
    'Carved Gourd': [
        ('Caring for a carved gourd', [
            'Carved gourds are made from natural dried gourd shell, a light material that is sensitive to moisture and strong sunlight. Display it away from damp, direct sun and heat, dust it with a soft brush, and handle it with dry hands so the carved surface stays crisp.',
        ]),
    ],
}

BUYING = ('Buying from Wen Gu Hall', [
    'Every piece on this page is one of a kind and has its own page with photographs. Quote the SKU on WhatsApp or by email if you would like extra photographs, measurements or condition details before deciding. You can pay with PayPal in the treasure box or by a secure payment link, and standard shipping is free, tracked and insured.',
])

ORDERING = [
    'Add this piece to the treasure box on our homepage and pay securely with PayPal, or message us on WhatsApp or by email quoting the SKU - we confirm availability within 24 hours and send a secure payment link.',
    'Pieces ship from Shenzhen within 3-5 business days, tracked and insured, and standard shipping is free; import duties and taxes, where applicable, are the buyer\'s responsibility. Returns can be requested within 14 days of delivery - see our shipping and returns terms for details.',
]
