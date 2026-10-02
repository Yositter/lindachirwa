#!/usr/bin/env python3
"""Build the practice area pages from scripts/practice_content.py.

Usage (from the repository root):
    python3 scripts/build-practice-pages.py
    python3 scripts/sync-shared.py        # fills in nav, icons, legal links, consent
    python3 scripts/build-sitemap.py

Existing pages (civil-law.html, conveyancing.html and so on) are hand-written
and are not touched. This script writes only the pages defined in
practice_content.py, plus practice-areas.html.
"""
import pathlib
import re

from practice_content import PAGES, HUB, RELATED_LABELS

ROOT = pathlib.Path(__file__).resolve().parent.parent

WA_SVG = ('<svg aria-hidden="true" focusable="false" width="18" height="18" viewBox="0 0 20 20" fill="none"><path d="M10 1.5a8.5 8.5 0 00-7.4 12.7L1.5 18.5l4.4-1.1A8.5 8.5 0 1010 1.5z" stroke="currentColor" stroke-width="1.3"/>'
          '<path d="M7.5 6.5c.2-.5.5-.5.7-.5s.5 0 .7.4l.8 2c.1.2 0 .4-.1.6l-.5.5s-.1.2.2.6c.4.5.8.9 1.3 1.1.2.1.4.1.5-.1l.5-.6c.2-.2.3-.2.5-.1l1.5.8c.2.1.3.2.3.4s0 .7-.4 1c-.4.4-.9.5-1.5.5-1-.1-2.5-.8-3.7-2.3-1-1.2-1.4-2.5-1.4-3.2 0-.5.2-.8.5-1.1z" fill="currentColor"/></svg>')
WA_FLOAT = WA_SVG.replace('width="18" height="18"', 'width="28" height="28"')

FOOTER = ('</main>\n\n<footer class="footer">\n<!-- LEGAL:START -->\n<!-- LEGAL:END -->\n'
          '  <p>&copy; 2026 Linda Chirwa Attorneys. All rights reserved. | <a href="./">Back to Home</a></p>\n</footer>')

TAIL = ('<script src="site.js"></script>\n<!-- CONSENT:START -->\n<!-- CONSENT:END -->\n</body>\n</html>\n')


def fix(text):
    """Escape bare ampersands, turn **bold** into <strong>. Raw HTML links are kept."""
    text = re.sub(r'&(?!amp;|lt;|gt;|quot;|rsquo;|#)', '&amp;', text)
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)


def attr(text):
    return fix(text).replace('"', '&quot;')


def head(title, meta, extra_css=''):
    style = f'<style>\n{extra_css}</style>\n' if extra_css else ''
    return (f'<!DOCTYPE html>\n<html lang="en-ZA">\n<head>\n<meta charset="UTF-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f'<title>{fix(title)}</title>\n<meta name="description" content="{attr(meta)}">\n'
            f'<!-- ICONS:START -->\n<!-- ICONS:END -->\n'
            f'<link rel="stylesheet" href="site.css">\n<link rel="stylesheet" href="service-page.css">\n{style}</head>\n<body>\n\n'
            f'<!-- NAV:START -->\n<!-- NAV:END -->\n\n<main id="main" tabindex="-1">\n')


def page_header(h1, lead, crumb):
    return (f'\n<section class="page-header">\n  <h1>{fix(h1)}</h1>\n  <p>{fix(lead)}</p>\n'
            f'  <div class="breadcrumb">\n    <a href="./">Home</a>\n    <span>/</span>\n'
            f'    <a href="practice-areas.html">Practice Areas</a>\n    <span>/</span>\n'
            f'    <span class="current">{fix(crumb)}</span>\n  </div>\n</section>\n')


def delay(i):
    d = i % 6 + 1 if i else 0
    return f' data-delay="{d}"' if d else ''


def accordion(i, area):
    aid, title, intro, groups, closing = area
    out = [f'    <details class="accordion reveal"{delay(i)} id="{aid}">',
           f'      <summary>{fix(title)}</summary>', '      <div class="accordion-body">',
           f'        <p>{fix(intro)}</p>']
    for heading, items in groups:
        out.append(f'\n        <h3>{fix(heading)}</h3>\n        <ul>')
        out += [f'          <li>{fix(x)}</li>' for x in items]
        out.append('        </ul>')
    if closing:
        out.append(f'\n        <p>{fix(closing)}</p>')
    out += ['      </div>', '    </details>\n']
    return '\n'.join(out)


def build_service_page(fname, p):
    h = head(p['title'], p['meta'])
    h += page_header(p['h1'], p['lead'], p['nav_title'])
    h += f'\n<div class="content-wrap">\n\n  <p class="intro-text reveal">\n    {fix(p["intro"])}\n  </p>\n\n</div>\n'
    h += '''
<section class="stat-band" id="stats">
  <div class="stat-band-inner">
    <div class="stat-item-band reveal" data-delay="1">
      <div class="stat-number-band"><span class="counter" data-target="4">0</span></div>
      <div class="stat-label-band">Provinces<br>Served</div>
    </div>
    <div class="stat-item-band reveal" data-delay="2">
      <div class="stat-number-band">24<span>hr</span></div>
      <div class="stat-label-band">Response<br>Commitment</div>
    </div>
    <div class="stat-item-band reveal" data-delay="3">
      <div class="stat-number-band">Written</div>
      <div class="stat-label-band">Cost Estimate<br>Before You Commit</div>
    </div>
    <div class="stat-item-band reveal" data-delay="4">
      <div class="stat-number-band">Direct</div>
      <div class="stat-label-band">Access to<br>Your Attorney</div>
    </div>
  </div>
</section>
'''
    h += '\n<div class="content-wrap" style="padding-top: 0;">\n\n  <h2 class="section-title reveal">What We Handle</h2>\n\n  <div class="accordion-group">\n\n'
    h += '\n'.join(accordion(i, a) for i, a in enumerate(p['areas']))
    h += '\n  </div>\n\n'
    # steps
    h += '  <div class="steps-section">\n    <h2 class="section-title reveal">How We Work</h2>\n    <ol class="steps-list">\n'
    for t, d in p['steps']:
        h += f'      <li class="reveal">\n        <div>\n          <strong>{fix(t)}</strong>\n          <span>{fix(d)}</span>\n        </div>\n      </li>\n'
    h += '    </ol>\n  </div>\n\n'
    # checklist
    h += ('  <div class="checklist-section">\n    <h2 class="section-title reveal">What to Bring to Your First Consultation</h2>\n'
          '    <p class="reveal" style="font-size: 15px; color: var(--warm-gray); line-height: 1.8; margin-bottom: 8px; max-width: 780px;">'
          'Having these ready lets us give you a faster, more useful assessment. We will confirm exactly what is needed once we understand your situation.</p>\n    <ul class="checklist">\n')
    for i, c in enumerate(p['checklist']):
        h += f'      <li class="reveal"{delay(i % 6)}>{fix(c)}</li>\n'
    h += '    </ul>\n  </div>\n\n'
    # faqs
    h += '  <div class="faq-section">\n    <h2 class="section-title reveal">Frequently Asked Questions</h2>\n\n    <div class="accordion-group">\n\n'
    for i, (q, a) in enumerate(p['faqs']):
        h += (f'      <details class="accordion reveal"{delay(i)}>\n        <summary>{fix(q)}</summary>\n'
              f'        <div class="accordion-body">\n          <p>{fix(a)}</p>\n        </div>\n      </details>\n\n')
    h += '    </div>\n  </div>\n\n'
    # related
    h += '  <div class="related-block">\n    <h2 class="section-title reveal">Related Services</h2>\n    <div class="related-links reveal">\n'
    for r in p['related']:
        h += f'      <a href="{r}">{fix(RELATED_LABELS[r])}</a>\n'
    h += '      <a href="practice-areas.html">All practice areas</a>\n    </div>\n  </div>\n\n'
    # cta
    h += (f'  <div class="cta-section reveal">\n    <h2>{fix(p["cta_head"])}</h2>\n    <p>{fix(p["cta_text"])}</p>\n'
          '    <p>Call <strong>+27 (10) 085 5185</strong> &nbsp;&middot;&nbsp; WhatsApp <strong>074 990 5872</strong> &nbsp;&middot;&nbsp; Email <strong>admin@lindachirwaattorneys.co.za</strong></p>\n'
          f'    <div class="cta-buttons">\n      <a href="https://wa.me/27749905872" class="cta-btn cta-btn-primary" target="_blank" rel="noopener">\n        {WA_SVG}\n        WhatsApp Us\n      </a>\n'
          '      <a href="contact.html" class="cta-btn cta-btn-outline">\n        Send Us a Message\n      </a>\n    </div>\n  </div>\n\n</div>\n\n')
    h += FOOTER + '\n\n<!-- Floating WhatsApp -->\n<a href="https://wa.me/27749905872" class="wa-float" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">\n  ' + WA_FLOAT + '\n</a>\n\n' + TAIL
    (ROOT / fname).write_text(h, encoding='utf-8')


HUB_CSS = '''.practice-section { margin-bottom: 56px; }
.practice-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin-top: 8px; }
.practice-card {
  display: block; text-decoration: none;
  background: var(--white); border: 1px solid var(--border); border-radius: 10px;
  padding: 24px 22px; position: relative; overflow: hidden;
  transition: border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}
.practice-card::after {
  content: ''; position: absolute; left: 0; right: 0; bottom: 0; height: 3px;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  transform: scaleX(0); transform-origin: left; transition: transform 0.4s ease;
}
.practice-card:hover { border-color: var(--primary); box-shadow: var(--shadow-md); transform: translateY(-4px); }
.practice-card:hover::after { transform: scaleX(1); }
.practice-card h3 { font-family: var(--font-display); font-weight: 600; font-size: 16px; color: var(--charcoal); margin-bottom: 8px; }
.practice-card p { font-size: 13.5px; line-height: 1.65; color: var(--warm-gray); margin-bottom: 14px; }
.practice-card .more { font-family: var(--font-display); font-size: 11px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--primary); }
@media (max-width: 1024px) { .practice-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 640px) { .practice-grid { grid-template-columns: 1fr; } }
'''


def build_hub():
    title = 'Practice Areas | Linda Chirwa Attorneys'
    meta = 'All practice areas of Linda Chirwa Attorneys: family, estates, property, notarial, criminal, civil, labour, immigration, company, contracts, M&A, IP and HR.'
    h = head(title, meta, HUB_CSS)
    h += ('\n<section class="page-header">\n  <h1>Practice Areas</h1>\n  <p>Legal services for individuals, families and businesses across Gauteng, KwaZulu-Natal, North West and the Western Cape.</p>\n'
          '  <div class="breadcrumb">\n    <a href="./">Home</a>\n    <span>/</span>\n    <span class="current">Practice Areas</span>\n  </div>\n</section>\n')
    h += ('\n<div class="content-wrap">\n\n  <p class="intro-text reveal">\n    We are attorneys, conveyancers and notaries, and most clients come to us with a matter that touches more than one of these areas. '
          '<strong>Choose the area closest to your problem, or contact us and we will point you to the right attorney.</strong> '
          'Every first consultation is confidential and comes with an honest view of your options and the likely cost.\n  </p>\n\n')
    for heading, key in (('For Individuals', 'individuals'), ('For Businesses', 'businesses')):
        h += f'  <div class="practice-section">\n    <h2 class="section-title reveal">{heading}</h2>\n    <div class="practice-grid">\n'
        for i, (name, href, desc) in enumerate(HUB[key]):
            h += (f'      <a href="{href}" class="practice-card reveal"{delay(i % 3)}>\n        <h3>{fix(name)}</h3>\n        <p>{fix(desc)}</p>\n'
                  '        <span class="more">Read more &rarr;</span>\n      </a>\n')
        h += '    </div>\n  </div>\n\n'
    h += ('  <div class="cta-section reveal">\n    <h2>Not Sure Which Area Fits?</h2>\n    <p>Describe your situation in a message. We will tell you which attorney can help and what to expect.</p>\n'
          '    <p>Call <strong>+27 (10) 085 5185</strong> &nbsp;&middot;&nbsp; WhatsApp <strong>074 990 5872</strong> &nbsp;&middot;&nbsp; Email <strong>admin@lindachirwaattorneys.co.za</strong></p>\n'
          f'    <div class="cta-buttons">\n      <a href="https://wa.me/27749905872" class="cta-btn cta-btn-primary" target="_blank" rel="noopener">\n        {WA_SVG}\n        WhatsApp Us\n      </a>\n'
          '      <a href="contact.html" class="cta-btn cta-btn-outline">\n        Send Us a Message\n      </a>\n    </div>\n  </div>\n\n</div>\n\n')
    h += FOOTER + '\n\n<!-- Floating WhatsApp -->\n<a href="https://wa.me/27749905872" class="wa-float" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">\n  ' + WA_FLOAT + '\n</a>\n\n' + TAIL
    (ROOT / 'practice-areas.html').write_text(h, encoding='utf-8')


def main():
    for fname, p in PAGES.items():
        build_service_page(fname, p)
    build_hub()
    print(f'wrote {len(PAGES)} practice pages and practice-areas.html')


if __name__ == '__main__':
    main()
