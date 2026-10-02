#!/usr/bin/env python3
"""Generate sitemap.xml and robots.txt from the pages in the repository root.

Usage (from the repository root):  python3 scripts/build-sitemap.py

Edit BASE in scripts/site_config.py if the live domain changes. Every *.html file in the root is listed, newest edit date from
git as <lastmod>. Add a filename to EXCLUDE to keep a page out of the sitemap.
Run it again after adding or editing pages.
"""
import pathlib
import subprocess
import datetime
from xml.sax.saxutils import escape

from site_config import BASE
EXCLUDE = {'404.html'}     # pages kept out of the sitemap
DISALLOW = ['/contact-handler.php', '/whistleblower-handler.php']

# Listing order. Pages not named here are appended alphabetically.
ORDER = [
    'index.html', 'about.html', 'criminal-law.html', 'civil-law.html',
    'wills-estates.html', 'conveyancing.html', 'notarial-services.html',
    'practice-areas.html', 'family-law.html', 'labour-law.html', 'immigration.html',
    'company-formation.html', 'commercial-contracts.html', 'mergers-acquisitions.html',
    'intellectual-property.html', 'employment-hr.html',
    'resources.html', 'contact.html', 'whistleblower.html',
    'privacy-policy.html', 'terms-of-use.html', 'cookies.html',
]

ROOT = pathlib.Path(__file__).resolve().parent.parent


def lastmod(path):
    try:
        out = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', path.name],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        if out:
            return out
    except Exception:
        pass
    return datetime.date.fromtimestamp(path.stat().st_mtime).isoformat()


def url_for(name):
    return BASE + '/' if name == 'index.html' else f'{BASE}/{name}'


def main():
    pages = {p.name: p for p in ROOT.glob('*.html') if p.name not in EXCLUDE}
    names = [n for n in ORDER if n in pages] + sorted(n for n in pages if n not in ORDER)

    rows = []
    for n in names:
        rows.append(f'  <url>\n    <loc>{escape(url_for(n))}</loc>\n    <lastmod>{lastmod(pages[n])}</lastmod>\n  </url>')
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + '\n'.join(rows) + '\n</urlset>\n')
    (ROOT / 'sitemap.xml').write_text(xml, encoding='utf-8')

    robots = 'User-agent: *\nAllow: /\n' + ''.join(f'Disallow: {d}\n' for d in DISALLOW) + f'\nSitemap: {BASE}/sitemap.xml\n'
    (ROOT / 'robots.txt').write_text(robots, encoding='utf-8')
    print(f'sitemap.xml: {len(names)} URLs; robots.txt written')


if __name__ == '__main__':
    main()
