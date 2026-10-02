#!/usr/bin/env python3
"""Regenerate the shared header blocks on every page from one source.

Usage (from the repository root):  python3 scripts/sync-shared.py

Each page marks the blocks it shares with comment markers:

    <!-- ICONS:START --> ... <!-- ICONS:END -->   favicon + manifest tags
    <!-- LEGAL:START --> ... <!-- LEGAL:END -->   footer links to the legal pages
    <!-- NAV:START -->   ... <!-- NAV:END -->     desktop nav + mobile nav

Edit NAV_ITEMS / PRACTICE_AREAS / OFFICES below, run this script, and every
page is updated with the right "active" item. Use --check to fail (exit 1)
when any page is out of date, e.g. in CI.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

ICONS = '''<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#1A4A2E">'''

LEGAL_LINKS = [
    ('Cookie Policy', 'cookies.html'),
    ('Privacy Policy', 'privacy-policy.html'),
    ('Terms of Use', 'terms-of-use.html'),
    ('Whistleblower', 'whistleblower.html'),
]


def build_legal(page):
    rows = []
    for text, href in LEGAL_LINKS:
        cls = ' class="active"' if href == page else ''
        rows.append(f'  <a href="{href}"{cls}>{text}</a>')
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
        ('Wills, Estates &amp; Trusts', 'wills-estates.html'),
        ('Property Conveyancing', 'conveyancing.html'),
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


def links(items, indent):
    return '\n'.join(f'{indent}<a href="{h}">{t}</a>' for t, h in items)


def build_nav(page):
    desktop, mobile = [], []
    for label, href, sub, short in NAV_ITEMS:
        active = href == page
        dlabel = short or label
        cls = 'nav-link active' if active else 'nav-link'
        cur = ' aria-current="page"' if active else ''
        if sub is None:
            desktop.append(f'    <div class="nav-item"><a class="{cls}" href="{href}"{cur}>{dlabel}</a></div>')
            m_cls = ' class="active"' if active else ''
            mobile.append(f'  <a href="{href}"{m_cls}>{label}</a>')
            continue
        if sub == 'practice':
            groups = '\n'.join(
                f'        <div class="submenu-group">\n          <h4>{g}</h4>\n{links(items, "          ")}\n        </div>'
                for g, items in PRACTICE_AREAS.items())
            panel = f'      <div class="submenu wide">\n{groups}\n      </div>'
            msub = '\n'.join(
                f'      <h4>{g}</h4>\n{links(items, "      ")}' for g, items in PRACTICE_AREAS.items())
            msub = f'      <a href="{href}">All Practice Areas</a>\n{msub}'
        else:
            panel = f'      <div class="submenu align-right">\n{links(OFFICES, "        ")}\n      </div>'
            msub = f'      <a href="{href}">Contact Overview</a>\n{links(OFFICES, "      ")}'
        desktop.append(
            f'    <div class="nav-item has-sub">\n'
            f'      <a class="{cls}" href="{href}" aria-haspopup="true"{cur}>{dlabel}<span class="caret" aria-hidden="true"></span></a>\n'
            f'{panel}\n    </div>')
        open_attr = ' open' if active else ''
        mobile.append(f'  <details{open_attr}>\n    <summary>{label}</summary>\n    <div class="mobile-sub">\n{msub}\n    </div>\n  </details>')

    return f'''<header class="navbar" role="banner">
  <div class="navbar-left">
    <a href="index.html" aria-label="Linda Chirwa Attorneys Home">
      <img src="logo.png" alt="Linda Chirwa Attorneys" class="navbar-logo">
    </a>
  </div>
  <nav class="navbar-right" role="navigation" aria-label="Main navigation">
{chr(10).join(desktop)}
  </nav>
  <button class="mobile-toggle" id="mobileToggle" aria-label="Toggle navigation" aria-expanded="false">
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
        new, ok_icons = replace_block(new, 'ICONS', ICONS)
        new, ok_legal = replace_block(new, 'LEGAL', build_legal(path.name))
        if not (ok_nav and ok_icons and ok_legal):
            print(f'skip  {path.name} (markers missing)')
            continue
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
