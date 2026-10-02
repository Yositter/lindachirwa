#!/usr/bin/env python3
"""Regenerate the shared header blocks on every page from one source.

Usage (from the repository root):  python3 scripts/sync-shared.py

Each page marks the blocks it shares with comment markers:

    <!-- ICONS:START --> ... <!-- ICONS:END -->   SEO head tags: canonical, Open Graph, Twitter,
                                                structured data, font preloads, icons
    <!-- LEGAL:START --> ... <!-- LEGAL:END -->   footer links to the legal pages
    <!-- CONSENT:START --> ... <!-- CONSENT:END -->   cookie consent script
    <!-- NAV:START -->   ... <!-- NAV:END -->     desktop nav + mobile nav

Edit NAV_ITEMS / PRACTICE_AREAS / OFFICES below, run this script, and every
page is updated with the right "active" item. Use --check to fail (exit 1)
when any page is out of date, e.g. in CI.

The head block is built from each page's own <title>, meta description and
breadcrumb, so change those in the page and re-run this script.

The script also stamps every reference to a local CSS or JS file with
?v=<content hash>, so browsers fetch a fresh copy whenever the file changes
(the server caches these files for a year, see .htaccess).
"""
import hashlib
import html
import json
import pathlib
import re
import sys

from site_config import BASE

ROOT = pathlib.Path(__file__).resolve().parent.parent

CONSENT = '<script src="consent.js" defer></script>'

ICONS = '''<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#1A4A2E">'''

FONT_PRELOADS = '''<link rel="preload" href="fonts/raleway-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>'''

# Without JavaScript, show content that would otherwise wait for scroll animations.
NOSCRIPT = '<noscript><style>.reveal,.reveal-left,.reveal-right{opacity:1!important;transform:none!important}#loader{display:none!important}</style></noscript>'

SITE_NAME = 'Linda Chirwa Attorneys'
OG_IMAGE = BASE + '/og-image.jpg'
NOINDEX = {'404.html'}

ORGANIZATION = {
    '@context': 'https://schema.org',
    '@type': 'LegalService',
    '@id': BASE + '/#organization',
    'name': SITE_NAME,
    'alternateName': 'Linda Chirwa Attorneys, Conveyancers & Notaries',
    'url': BASE + '/',
    'logo': BASE + '/logo.png',
    'image': OG_IMAGE,
    'telephone': '+27 10 085 5185',
    'email': 'admin@lindachirwaattorneys.co.za',
    'address': {
        '@type': 'PostalAddress',
        'streetAddress': 'Block C, Stoneridge Office Park, Greenstone',
        'addressLocality': 'Modderfontein, Johannesburg',
        'addressRegion': 'Gauteng',
        'postalCode': '1609',
        'addressCountry': 'ZA',
    },
    'openingHoursSpecification': [{
        '@type': 'OpeningHoursSpecification',
        'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        'opens': '08:00',
        'closes': '17:00',
    }],
    'areaServed': [{'@type': 'AdministrativeArea', 'name': n}
                   for n in ('Gauteng', 'KwaZulu-Natal', 'North West', 'Western Cape')],
    'department': [
        {'@type': 'LegalService', 'name': 'Linda Chirwa Attorneys, West Rand',
         'email': 'admin@lindachirwaattorneys.co.za',
         'address': {'@type': 'PostalAddress', 'streetAddress': '25 Drakenstein Street, Culemborg Park',
                     'addressLocality': 'Randfontein', 'addressRegion': 'Gauteng', 'addressCountry': 'ZA'}},
        {'@type': 'LegalService', 'name': 'Linda Chirwa Attorneys, KwaZulu-Natal',
         'telephone': '+27 33 108 5203', 'address': {'@type': 'PostalAddress', 'addressRegion': 'KwaZulu-Natal', 'addressCountry': 'ZA'}},
        {'@type': 'LegalService', 'name': 'Linda Chirwa Attorneys, North West',
         'telephone': '+27 18 108 5352', 'address': {'@type': 'PostalAddress', 'addressRegion': 'North West', 'addressCountry': 'ZA'}},
        {'@type': 'LegalService', 'name': 'Linda Chirwa Attorneys, Western Cape',
         'telephone': '+27 21 054 4906', 'address': {'@type': 'PostalAddress', 'addressRegion': 'Western Cape', 'addressCountry': 'ZA'}},
    ],
}
ORG_PAGES = {'index.html', 'contact.html', 'about.html'}

# Local assets that get a ?v=<hash> cache-busting stamp.
VERSIONED = ['site.css', 'service-page.css', 'legal-page.css', 'forms.css',
             'site.js', 'consent.js', 'home.js', 'contact.js', 'whistleblower.js']


LEGAL_LINKS = [
    ('Cookie Policy', 'cookies.html'),
    ('Privacy Policy', 'privacy-policy.html'),
    ('Terms of Use', 'terms-of-use.html'),
    ('Whistleblower', 'whistleblower.html'),
]


def page_url(page):
    return BASE + '/' if page in ('index.html', './') else f'{BASE}/{page}'


def link(href):
    """Pages link to the home page as ./ so visitors land on the canonical address."""
    return './' if href == 'index.html' else href


def meta_from(text, page):
    """Read the page's own title, description and breadcrumb."""
    title = html.unescape(re.search(r'<title>(.*?)</title>', text, re.S).group(1).strip())
    m = re.search(r'<meta name="description" content="([^"]*)"', text)
    desc = html.unescape(m.group(1)) if m else ''
    crumbs = []
    b = re.search(r'<div class="breadcrumb">(.*?)</div>', text, re.S)
    if b:
        for href, name in re.findall(r'<a href="([^"]+)">(.*?)</a>', b.group(1)):
            crumbs.append((html.unescape(re.sub('<[^>]+>', '', name)).strip(), page_url(href)))
        cur = re.search(r'<span class="current">(.*?)</span>', b.group(1), re.S)
        if cur:
            crumbs.append((html.unescape(re.sub('<[^>]+>', '', cur.group(1))).strip(), page_url(page)))
    return title, desc, crumbs


def ld_json(data):
    return ('<script type="application/ld+json">'
            + json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
            + '</script>')


def build_icons(page, text):
    title, desc, crumbs = meta_from(text, page)
    a = lambda v: html.escape(v, quote=True)
    url = page_url(page)
    out = []
    if page in NOINDEX:
        out.append('<meta name="robots" content="noindex, follow">')
    else:
        out.append(f'<link rel="canonical" href="{url}">')
    out += [
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        '<meta property="og:locale" content="en_ZA">',
        f'<meta property="og:title" content="{a(title)}">',
        f'<meta property="og:description" content="{a(desc)}">',
    ]
    if page not in NOINDEX:
        out.append(f'<meta property="og:url" content="{url}">')
    out += [
        f'<meta property="og:image" content="{OG_IMAGE}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{SITE_NAME}, Attorneys, Conveyancers &amp; Notaries">',
        '<meta name="twitter:card" content="summary_large_image">',
        FONT_PRELOADS,
        ICONS,
        NOSCRIPT,
    ]
    if page in ORG_PAGES:
        out.append(ld_json(ORGANIZATION))
    if page == 'index.html':
        out.append(ld_json({'@context': 'https://schema.org', '@type': 'WebSite',
                            'name': SITE_NAME, 'url': BASE + '/', 'inLanguage': 'en-ZA',
                            'publisher': {'@id': BASE + '/#organization'}}))
    if len(crumbs) > 1 and page not in NOINDEX:
        out.append(ld_json({'@context': 'https://schema.org', '@type': 'BreadcrumbList',
                            'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u}
                                                for i, (n, u) in enumerate(crumbs)]}))
    return '\n'.join(out)


def version_assets(text):
    """Stamp local CSS/JS references with a short content hash."""
    for name in VERSIONED:
        f = ROOT / name
        if not f.exists():
            continue
        v = hashlib.sha1(f.read_bytes()).hexdigest()[:8]
        text = re.sub(rf'((?:href|src)="/?){re.escape(name)}(?:\?v=[0-9a-f]+)?"', rf'\g<1>{name}?v={v}"', text)
    return text


def absolutize(text):
    """Root-relative links for pages served at any depth (the 404 page)."""
    text = re.sub(r'((?:href|src)=")\./(?=["#])', r'\g<1>/', text)
    return re.sub(r'((?:href|src)=")(?!https?:|/|#|mailto:|tel:|data:)', r'\g<1>/', text)


def build_legal(page):
    rows = []
    for text, href in LEGAL_LINKS:
        cls = ' class="active"' if href == page else ''
        rows.append(f'  <a href="{link(href)}"{cls}>{text}</a>')
    rows.append('  <a href="cookies.html#manage" data-cookie-settings>Cookie Settings</a>')
    return '<div class="footer-legal-links">\n' + '\n'.join(rows) + '\n</div>'


# (mobile label, href, submenu key or None, short desktop label or None)
NAV_ITEMS = [
    ('Home', 'index.html', None, None),
    ('About', 'about.html', None, None),
    ('Practice Areas', 'practice-areas.html', 'practice', None),
    ('Criminal Law', 'criminal-law.html', None, 'Criminal'),
    ('Civil Litigation', 'civil-law.html', None, 'Civil'),
    ('Estates', 'wills-estates.html', None, None),
    ('Conveyancing', 'conveyancing.html', None, None),
    ('Notarial Services', 'notarial-services.html', None, 'Notarial'),
    ('Resources', 'resources.html', None, None),
    ('Contact', 'contact.html', 'offices', None),
]

PRACTICE_AREAS = {
    'For Individuals': [
        ('Family Law', 'family-law.html'),
        ('Wills, Estates &amp; Trusts', 'wills-estates.html#will-drafting'),
        ('Estate Administration', 'wills-estates.html#administration'),
        ('Property Conveyancing', 'conveyancing.html#residential'),
        ('Notarial Services (ANCs, Bonds, Apostille)', 'notarial-services.html'),
        ('Motor Vehicle &amp; Workplace Injury', 'civil-law.html#delictual'),
        ('Criminal Defence', 'criminal-law.html'),
        ('CCMA &amp; Employment Disputes', 'labour-law.html'),
        ('Immigration &amp; Permits', 'immigration.html'),
    ],
    'For Businesses': [
        ('Company Formation &amp; Governance', 'company-formation.html'),
        ('Contracts &amp; Transactions', 'commercial-contracts.html'),
        ('Mergers &amp; Acquisitions', 'mergers-acquisitions.html'),
        ('Debt Collection &amp; Litigation', 'civil-law.html#debt'),
        ('Insolvency &amp; Business Rescue', 'civil-law.html#insolvency'),
        ('Intellectual Property', 'intellectual-property.html'),
        ('Commercial Property', 'conveyancing.html#commercial'),
        ('Employment &amp; HR Compliance', 'employment-hr.html'),
    ],
}

OFFICES = [
    ('Gauteng: Head Office', 'contact.html#office-gauteng'),
    ('Gauteng: West Rand', 'contact.html#office-west-rand'),
    ('KwaZulu-Natal', 'contact.html#office-kzn'),
    ('North West', 'contact.html#office-north-west'),
    ('Western Cape', 'contact.html#office-western-cape'),
    ('Department Emails', 'contact.html#office-departments'),
    ('Send an Enquiry', 'contact.html#contactForm'),
]


def links(items, indent, page=''):
    cur = lambda h: ' aria-current="page"' if h == page else ''
    return '\n'.join(f'{indent}<a href="{h}"{cur(h)}>{t}</a>' for t, h in items)


def build_nav(page):
    # Service pages that sit only under the Practice Areas menu highlight that menu.
    top_level = {h for _, h, _, _ in NAV_ITEMS}
    practice_only = {h.split('#')[0] for items in PRACTICE_AREAS.values() for _, h in items} - top_level
    desktop, mobile = [], []
    for label, href, sub, short in NAV_ITEMS:
        active = href == page or (sub == 'practice' and page in practice_only)
        dlabel = short or label
        cls = 'nav-link active' if active else 'nav-link'
        # aria-current marks the exact page only; a parent menu is highlighted visually.
        cur = ' aria-current="page"' if href == page else ''
        if sub is None:
            desktop.append(f'    <div class="nav-item"><a class="{cls}" href="{link(href)}"{cur}>{dlabel}</a></div>')
            m_cls = ' class="active"' if active else ''
            mobile.append(f'  <a href="{link(href)}"{m_cls}{cur}>{label}</a>')
            continue
        if sub == 'practice':
            groups = '\n'.join(
                f'        <div class="submenu-group">\n          <p class="submenu-title">{g}</p>\n{links(items, "          ", page)}\n        </div>'
                for g, items in PRACTICE_AREAS.items())
            panel = f'      <div class="submenu wide">\n{groups}\n      </div>'
            msub = '\n'.join(
                f'      <p class="submenu-title">{g}</p>\n{links(items, "      ", page)}' for g, items in PRACTICE_AREAS.items())
            msub = f'      <a href="{href}"{cur}>All Practice Areas</a>\n{msub}'
        else:
            panel = f'      <div class="submenu align-right">\n{links(OFFICES, "        ")}\n      </div>'
            msub = f'      <a href="{href}"{cur}>Contact Overview</a>\n{links(OFFICES, "      ")}'
        desktop.append(
            f'    <div class="nav-item has-sub">\n'
            f'      <a class="{cls}" href="{href}" aria-haspopup="true"{cur}>{dlabel}<span class="caret" aria-hidden="true"></span></a>\n'
            f'{panel}\n    </div>')
        open_attr = ' open' if active else ''
        mobile.append(f'  <details{open_attr}>\n    <summary>{label}</summary>\n    <div class="mobile-sub">\n{msub}\n    </div>\n  </details>')

    return f'''<a class="skip-link" href="#main">Skip to main content</a>
<header class="navbar" role="banner">
  <div class="navbar-left">
    <a href="./" class="navbar-brand">
      <img src="logo.png" alt="Linda Chirwa Attorneys, home page" width="360" height="161" class="navbar-logo">
    </a>
  </div>
  <nav class="navbar-right" role="navigation" aria-label="Main navigation">
{chr(10).join(desktop)}
  </nav>
  <button class="mobile-toggle" id="mobileToggle" aria-label="Open menu" aria-controls="mobileNav" aria-expanded="false">
    <span></span><span></span><span></span>
  </button>
</header>

<!-- Mobile Nav -->
<div class="mobile-nav" id="mobileNav" aria-hidden="true">
{chr(10).join(mobile)}
</div>'''


def replace_block(text, name, body):
    pat = re.compile(rf'<!-- {name}:START -->.*?<!-- {name}:END -->', re.S)
    if not pat.search(text):
        return text, False
    block = f'<!-- {name}:START -->\n{body}\n<!-- {name}:END -->'
    return pat.sub(lambda m: block, text), True


def main():
    check = '--check' in sys.argv
    stale = []
    for path in sorted(ROOT.glob('*.html')):
        text = path.read_text(encoding='utf-8')
        new, ok_nav = replace_block(text, 'NAV', build_nav(path.name))
        new, ok_icons = replace_block(new, 'ICONS', build_icons(path.name, new))
        new, ok_legal = replace_block(new, 'LEGAL', build_legal(path.name))
        new, ok_consent = replace_block(new, 'CONSENT', CONSENT)
        if not (ok_nav and ok_icons and ok_legal and ok_consent):
            print(f'skip  {path.name} (markers missing)')
            continue
        new = version_assets(new)
        if path.name in NOINDEX:
            new = absolutize(new)
        if new != text:
            stale.append(path.name)
            if not check:
                path.write_text(new, encoding='utf-8')
                print(f'wrote {path.name}')
        else:
            print(f'ok    {path.name}')
    if check and stale:
        print('out of date:', ', '.join(stale))
        sys.exit(1)


if __name__ == '__main__':
    main()
