# Linda Chirwa Attorneys website

A static website: plain HTML, CSS and JavaScript, plus two PHP form handlers. There is no framework and no build step to run on the server. A few small Python scripts keep the shared parts of the pages (navigation, footer links, icons) consistent, and you run them on your own computer before uploading.

## Contents

1. [What is in the repository](#what-is-in-the-repository)
2. [How the pages are put together](#how-the-pages-are-put-together)
3. [Everyday tasks](#everyday-tasks)
4. [Settings you may need to change](#settings-you-may-need-to-change)
5. [Deploying](#deploying)
6. [After each deploy](#after-each-deploy)
7. [Before the site goes live for the first time](#before-the-site-goes-live-for-the-first-time)
8. [Troubleshooting](#troubleshooting)

## What is in the repository

| Path | What it is |
|---|---|
| `*.html` | The 22 pages. Each page is a complete HTML file. |
| `site.css` | Shared styles: colours, fonts, navigation, header, footer, cookie banner. |
| `service-page.css` | Components used by the service pages (accordions, steps, checklists, call-to-action). |
| `legal-page.css` | Components used by the cookie, privacy and terms pages. |
| `forms.css` | Form styles, shared by the contact and whistleblower pages. |
| `site.js` | Mobile menu, scroll animations, counters, and opening an accordion from a `#link`. |
| `consent.js` | Cookie consent banner and the blocking of maps and videos until visitors allow them. |
| `contact-handler.php` | Receives the contact form and emails it. |
| `whistleblower-handler.php` | Receives whistleblower reports and emails them to a separate mailbox. |
| `images/avatars/` | Initials avatars for the home page testimonials (SVG). |
| `logo.png`, `favicon*.png`, `favicon.ico`, `apple-touch-icon.png`, `android-chrome-*.png`, `site.webmanifest` | Logo and icons. |
| `sitemap.xml`, `robots.txt` | Search engine files. Generated, see below. |
| `scripts/` | The maintenance scripts. Not part of the live site. |

Pages by group:

- **Main:** `index.html`, `about.html`, `contact.html`, `resources.html`, `practice-areas.html`
- **Hand-written service pages:** `criminal-law.html`, `civil-law.html`, `wills-estates.html`, `conveyancing.html`, `notarial-services.html`
- **Generated service pages:** `family-law.html`, `labour-law.html`, `immigration.html`, `company-formation.html`, `commercial-contracts.html`, `mergers-acquisitions.html`, `intellectual-property.html`, `employment-hr.html`
- **Legal:** `cookies.html`, `privacy-policy.html`, `terms-of-use.html`, `whistleblower.html`

## How the pages are put together

Three ideas explain almost everything.

**1. Shared styles live in the CSS files.** Change a colour or the header style once in `site.css` and every page follows. Each page also has a small `<style>` block at the top for styles that only that page needs.

**2. Shared page parts are written by a script.** The navigation, the favicon tags, the footer legal links and the cookie banner script appear on every page, so they are generated from one place. In each HTML file you will see marker comments like this:

```html
<!-- NAV:START -->
... generated, do not edit by hand ...
<!-- NAV:END -->
```

There are four pairs: `NAV`, `ICONS`, `LEGAL` and `CONSENT`. Anything between a pair is overwritten when you run `scripts/sync-shared.py`. Edit the script, not the pages. Keep the marker comments in place on every page, including new ones.

**3. Eight service pages are generated from one content file.** The wording for the family, labour, immigration, company, contracts, M&A, IP and employment pages, and the card text on `practice-areas.html`, lives in `scripts/practice_content.py`. The other pages were written by hand and are edited directly.

## Everyday tasks

You need Python 3.9 or newer on your computer. No packages to install. Run every command from the repository root (the folder that contains `index.html`).

### Edit text on a hand-written page

Open the HTML file, change the text, save. If you changed a page title or description, nothing else is needed.

### Edit a generated service page

1. Open `scripts/practice_content.py` and change the wording. Use `**bold**` for bold text. Plain `&` is fine.
2. Run:

```
python3 scripts/build-practice-pages.py
python3 scripts/sync-shared.py
```

Do not edit the generated HTML files directly. The next run of the build script would overwrite your change.

### Change the navigation menu

1. Open `scripts/sync-shared.py`.
2. Edit `NAV_ITEMS` (top bar), `PRACTICE_AREAS` (the Practice Areas dropdown) or `OFFICES` (the Contact dropdown).
3. Run `python3 scripts/sync-shared.py`.

Every page is updated, and the current page is highlighted automatically. The script prints `wrote` for each page it changed and `ok` for the ones already correct.

### Add a new page

1. Copy an existing page of the same kind (for example `civil-law.html` for a service page) and rename the copy.
2. Change the title, description, heading and content. Keep the four marker pairs and the `<link>` tags to the CSS files.
3. Add the page to the navigation if it should appear there (see above).
4. Add it to the `ORDER` list in `scripts/build-sitemap.py` so it lists in a sensible position.
5. Run:

```
python3 scripts/sync-shared.py
python3 scripts/build-sitemap.py
```

6. Open the page in a browser and click through its links.

### Link to a section of a page

Every accordion on a service page has an `id`, for example `civil-law.html#debt`. Visitors who follow such a link land on that section with the accordion already open. Give a new accordion an `id` and link to `page.html#id`.

### Change a phone number, email address or address

These appear as plain text in many files. Search the whole folder for the old value, change every match, and check the result:

```
grep -rn "074 990 5872" --include=*.html --include=*.php .
```

Key places: the contact page (sidebar and quick bar), the home page (hero, call-to-action, footer), the footer of the legal pages, and both PHP handlers.

### Change the logo or icons

Replace `logo.png` with a new file of the same name. The icon files (`favicon-16x16.png`, `favicon-32x32.png`, `favicon.ico`, `apple-touch-icon.png`, `android-chrome-192x192.png`, `android-chrome-512x512.png`) were cut from the logo as a stopgap. Replace them with clean artwork of the scales alone when you have it, keeping the same file names and sizes.

### Update the sitemap

Run this after adding, removing or editing pages:

```
python3 scripts/build-sitemap.py
```

It rewrites `sitemap.xml` and `robots.txt`. Each page's `lastmod` date comes from git, so commit your changes first if you want accurate dates.

### Check that nothing is out of date

```
python3 scripts/sync-shared.py --check
```

It prints `out of date:` with a list of pages and exits with an error if any page does not match the scripts. It changes nothing.

### Preview the site on your computer

Opening files directly works for most checks, but cookies, forms and the consent banner need a local web server:

```
python3 -m http.server 8000
```

Then browse to `http://localhost:8000`. The contact forms will not send mail locally, because they need a PHP-enabled server.

## Settings you may need to change

| Setting | Where | What it does |
|---|---|---|
| `BASE` | `scripts/site_config.py` | The live address, currently `https://lindachirwaattorneys.co.za`. Used for canonical tags and the sitemap. Change it if the site is served on `www`, then run `sync-shared.py` and `build-sitemap.py`. |
| `GA_ID` | `consent.js` (top of the file) | Your Google Analytics 4 measurement ID, for example `G-ABC123XYZ9`. While it is empty, no analytics code loads and the analytics option is hidden in the cookie preferences. |
| `$recipientEmail`, `$ccEmail` | `contact-handler.php` | Where enquiries go. Currently `admin@` with a copy to `info@`. |
| `$recipientEmail` | `whistleblower-handler.php` | Where whistleblower reports go. Must be a mailbox that only the designated recipient reads. |
| `EXCLUDE` | `scripts/build-sitemap.py` | Page names to keep out of the sitemap. |

## Deploying

The site needs ordinary web hosting with PHP, because of the two form handlers. Any shared host with cPanel or SFTP works.

### What to upload

Upload everything in the repository **except**:

- the `scripts/` folder
- the `.git/` folder
- `.gitignore`
- `README.md`

That leaves the HTML pages, the four CSS files, the two JavaScript files, the two PHP files, the `images/` folder, the logo and icons, `site.webmanifest`, `sitemap.xml` and `robots.txt`. Put them all in the site's web root (often `public_html`), with `index.html` at the top level. The icon links use absolute paths such as `/favicon-32x32.png`, so the files must sit at the root of the domain, not in a sub-folder.

### Steps

1. Run `python3 scripts/sync-shared.py --check` and `python3 scripts/build-sitemap.py` on your computer.
2. Upload the files with SFTP or your host's file manager, replacing the old copies.
3. Make sure the site is served over HTTPS. The cookie banner and the canonical tags assume it.
4. Follow the checklist below.

If the host redirects `www` to the bare domain, or the reverse, make sure it matches `BASE`.

### Email delivery

Both handlers use PHP's `mail()` function, which is the simplest option but depends on the host. Many hosts accept the message and then drop it silently if the sender address or the receiving mailbox does not exist. For that reason:

- Create the mailboxes the site uses: `admin@`, `info@`, `whistleblower@`, and the department addresses listed on the contact page (`litigation@`, `accounts@`, `conveyancing@`).
- The handlers send from `website@lindachirwaattorneys.co.za`. Create that mailbox, or ask the host which sender addresses are allowed.
- The contact handler copies `info@` with a `Cc:` header. Some hosts block this. If `admin@` receives the message but `info@` does not, remove the `Cc:` line in `contact-handler.php` and forward `admin@` to `info@` in the mailbox settings instead.
- If forms become unreliable, move to an SMTP service. That is a change to the two PHP files only.

## After each deploy

Spend five minutes on this. It catches most problems.

- [ ] The home page loads over HTTPS and shows the logo and the green navigation.
- [ ] The Practice Areas menu opens, and a link such as Family Law loads.
- [ ] Submit one enquiry through the contact form. Confirm it reaches `admin@` and `info@`.
- [ ] Submit one test report through the whistleblower form. Confirm it reaches only the whistleblower mailbox. Delete the test report afterwards.
- [ ] The cookie banner appears on a first visit. After choosing Reject, the map on the contact page and the videos on the resources page show a placeholder and do not load.
- [ ] `https://your-domain/sitemap.xml` and `https://your-domain/robots.txt` open in a browser.
- [ ] A phone-width view of the home page and one service page looks right.

## Before the site goes live for the first time

These items were flagged while the site was built and still need a decision or an action from the firm.

**Legal review.** The Cookie Policy, Privacy Policy, Terms of Use and Whistleblower page are drafts. A qualified attorney should review them. In particular:

- Name a real Information Officer and register them with the Information Regulator. The privacy policy currently names the firm.
- Confirm the retention periods in the privacy policy against the firm's actual practice.
- The practice area pages and the notarial page state points of law and deadlines. Have the relevant attorney confirm them.
- Replace the placeholder "Last updated" dates when the policies are approved.

**Cookie Policy accuracy.** The policy lists Google Analytics cookies as "only if switched on". If you do not use analytics, delete that table and section. If you do, set `GA_ID` in `consent.js`. The policy must always match what the site actually does.

**Mailboxes.** Create `whistleblower@lindachirwaattorneys.co.za` before the whistleblower page goes live, and make sure only the designated recipient can read it. Without it, reports are lost without any error.

**Fonts.** Typefaces load from Google Fonts before a visitor chooses anything in the cookie banner. They set no cookies, but they send the visitor's IP address to Google, and the Cookie Policy says so. Downloading the font files and serving them from the site removes this.

**Icons.** Replace the stopgap icons with clean artwork (see above).

**Placeholder claims.** The stat bands on service pages repeat claims such as a 24-hour response, written cost estimates and direct attorney access. Confirm the firm can keep every one of them.

**Testimonials.** The home page shows client testimonials with initials avatars (`images/avatars/`), not photos. Before launch, confirm that each testimonial is genuine, that the client agreed to it being published, and that publishing it is permitted under the Legal Practice Council's rules on attorney advertising. Remove any that cannot be verified.

## Troubleshooting

**The navigation looks wrong, or a page is missing from it.** Run `python3 scripts/sync-shared.py`. If a page is skipped with the message `markers missing`, add the four marker pairs (`NAV`, `ICONS`, `LEGAL`, `CONSENT`) to it, copying them from another page.

**My edit disappeared.** You edited a generated part. For navigation, footer links, icons or the consent script, edit `scripts/sync-shared.py`. For the eight generated service pages, edit `scripts/practice_content.py`. Then re-run the scripts.

**A link goes nowhere.** Check the file name for typos, and for `#` links check that the target accordion has that `id`.

**The cookie banner never shows.** It remembers earlier choices in a cookie called `cookie_consent`. Clear that cookie, or use a private window. Cookies do not work when a page is opened as a local file, so use `python3 -m http.server` for testing.

**The forms say they could not send.** Open the browser's developer tools, look at the request to the handler, and read the response. A `500` response means PHP's `mail()` failed on the server. Check that the sender mailbox exists and ask the host whether outbound mail is enabled. A `404` means the PHP file was not uploaded to the web root.

**Search engines show old or missing pages.** Re-run `scripts/build-sitemap.py`, upload `sitemap.xml`, and resubmit it in Google Search Console.

## Scripts reference

| Script | Run it when | What it does |
|---|---|---|
| `scripts/sync-shared.py` | You change the navigation, footer links, icons, base address or consent script, or add a page | Rewrites the four marked blocks in every HTML page. `--check` only reports. |
| `scripts/build-practice-pages.py` | You edit `scripts/practice_content.py` | Regenerates the eight service pages and `practice-areas.html`. Run `sync-shared.py` afterwards. |
| `scripts/build-sitemap.py` | You add, remove or edit pages | Regenerates `sitemap.xml` and `robots.txt`. |
| `scripts/site_config.py` | The live address changes | Holds `BASE`, used by the scripts above. |
