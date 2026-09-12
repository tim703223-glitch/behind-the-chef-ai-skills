---
name: local-business-seo-audit
description: "Audit a local business's website and social profiles for SEO and discoverability defects, then produce a paste-ready implementation document someone else can work through without needing CMS access. Reads live rendered pages (not raw HTML) to check titles, meta descriptions, heading structure, structured data, alt text and social preview images; cross-checks name/address/phone consistency across every profile; and separates outside-creator posts from native posts to show where reach actually comes from. Use when the user wants a website or social media review for a restaurant, shop, or other local business, asks why a business isn't showing up on Google, or wants an SEO deliverable to hand to an owner."
metadata:
  author: user-derived
  source: "Built 2026-09-06 from a live audit of a real restaurant (Square Online site + Instagram + TikTok) for a favor/portfolio project. The method exists because a raw-HTML sweep produced a confident, plausible, WRONG audit on the first attempt -- everything here is shaped around not making that mistake."
  version: "0.1.0-draft"
---

# Local Business SEO Audit

Produces two things from a live business website and its social profiles:

1. **A findings review** -- what's actually broken, with the real numbers, dated.
2. **A paste-ready implementation document** -- exact field values someone with CMS access can paste
   in, with no redesign and no guessing.

The deliverable is written for a business owner or whoever manages their site, not for the person
running the audit.

## When to Activate

- The user wants a website, SEO, or social media review for a local business
- The user asks why a business isn't ranking, or isn't showing up in "near me" searches
- The user needs something concrete to hand an owner (a report, a one-sheet, a field-by-field doc)
- The user is auditing their own local business's site

## Status: draft, single-site

Version 0.1.0. Every technique below was confirmed on exactly **one** site, on **one** platform
(Square Online), in **one** session. See `PENDING-NOTES.md` for what's confirmed versus untested.
Treat the Square-specific parts as untransferable until tested elsewhere.

## Rule 1: Read the rendered DOM, never the raw HTML

This is the whole foundation. Modern site builders (Square Online, Wix, Squarespace, Toast) serve an
empty JS app shell. A `fetch()` of a sub-page returns tens of kilobytes of markup with an **empty
`<title>`, absent meta tags, and zero body text** -- which reads exactly like "this site has no SEO
fields set" rather than "you used the wrong method."

On the site this skill was built against, a raw-HTML sweep of seven pages reported every title empty.
The rendered titles were all present (`Menu | [Restaurant A]`, `About Us | [Restaurant A]`, and so
on). The audit was confidently wrong until it was redone properly.

**So:** navigate to each page, wait for render, then read from the live DOM.

```js
// Run per page, after navigating to it
const m = n => { const e = document.querySelector(`meta[name="${n}"]`); return e ? e.getAttribute('content') : 'ABSENT'; };
await new Promise(r => setTimeout(r, 1500));
JSON.stringify({
  path: location.pathname,
  title: document.title,
  titleLen: document.title.length,
  desc: m('description'),
  descLen: (m('description') || '').length,
  h1: [...document.querySelectorAll('h1')].map(e => e.textContent.trim()),
  h2: [...document.querySelectorAll('h2')].map(e => e.textContent.trim()),
  schema: document.querySelectorAll('script[type="application/ld+json"]').length,
  ogImage: document.querySelector('meta[property="og:image"]')?.content || 'ABSENT',
  words: document.body.innerText.trim().split(/\s+/).length,
  imgs: document.images.length,
  imgsNoAlt: [...document.images].filter(i => !i.getAttribute('alt')).length,
  socials: [...new Set([...document.querySelectorAll('a[href]')].map(a => a.href)
    .filter(h => /tiktok|facebook|instagram|yelp|youtube|x\.com/i.test(h)))]
})
```

Batch the navigate/read pairs (`browser_batch` or equivalent) so a seven-page site is two calls, not
fourteen.

## Rule 2: Verify "empty" twice, with a screenshot

A page returning almost no text may be genuinely blank, or may just be mid-render. Both happened in
the same sweep on the build site: at a 1.5s wait, two pages looked empty; at 5s, one had 82 words of
real copy and the other was still blank. A screenshot confirmed the blank one.

Before writing "this page is empty" in something an owner will read, re-read with a longer wait
**and** take a screenshot. A blank page in a client's navigation is a strong claim; earn it.

## Rule 3: Validate field lengths with a script, every pass

Titles truncate in Google around 60 characters; meta descriptions around 160. Hand-checking fails,
and rewriting introduces new violations.

On the build site, the first validation pass caught 3 over-length descriptions. After fixing those, a
re-run caught a **fourth** that the fix itself had created (an em dash rewritten as the word
"including" pushed it to 169), plus em dashes still sitting in a published list.

Use `scripts/validate_seo_fields.py` after **every** edit pass, not once at the end.

```
python validate_seo_fields.py <implementation-doc.md>
```

## Rule 4: Diff the business's identity across every profile

Pull name, address, phone, and hours from the website, Instagram, TikTok, Facebook, and Yelp, then
compare them literally.

On the build site this surfaced the highest-value finding of the entire audit in one comparison: the
Instagram bio's ZIP was wrong (a neighbouring city's code), while the website and TikTok were right.
Inconsistent address data across profiles directly affects local ranking, and it costs nothing to fix.

Also check whether the site's footer links **every** profile. The build site linked Facebook,
Instagram, and Yelp but omitted TikTok, which was its largest audience.

## Rule 5: Prove where reach comes from, don't assert it

For a local business on Instagram, outside-creator visits often massively outperform native posts.
Prove it per-post rather than claiming it.

Fetch each reel permalink and read `og:title`. It names the actual author, so a collab post is
distinguishable from a native one:

- collab: `[Creator] on Instagram: "You have to try @[restaurant_a]..."`
- native: `[Restaurant A] on Instagram: "POV: ..."`

Report the native **median**, not the native average -- one viral native post distorts a mean and
weakens an otherwise sound argument. On the build site: top three posts all collabs
(15,900 / 7,779 / 3,107) against a native median of 1,015 across 18 reels.

Two gotchas confirmed on the build site:

- **Omit `credentials:'include'`** from in-page fetches. It gets the call refused outright
  (`[BLOCKED: Cookie/query string data]`). Same-origin fetches already carry the session.
- **Never regex profile fields out of Instagram's page bundle.** A `"biography"` regex returns the
  **logged-in viewer's** bio, not the profile being viewed, with nothing to signal the mismatch. Read
  the rendered `header` element instead.

Platform stats may be partially available: on the build site TikTok's profile header (followers,
likes) read fine while its video grid errored out permanently. State which one you actually got.

## Rule 6: Run `humanizer` on any copy that will be published

If the deliverable contains body copy that goes live under the business's name, pass it through the
`humanizer` skill before shipping. On the build site it caught a self-answered rhetorical opener, an
`-ing` participle, a tailing-negation fragment, a false "from X to Y" range, and em dashes
throughout. AI tells on a family business's About page are worse than a missing About page.

## Rule 7: Never invent the business's story

An About page is made of facts you do not have: who founded it, what year, why this food. Write the
structure, mark every unknown as an explicit `[BRACKET]`, and put a warning on the section telling
the reader not to publish it as-is.

Then list the questions only the owner can answer, as an actual section of the deliverable. On the
build site that list ran to seven items (founding story, whether hours were current, delivery or
pickup, which plan the site is on, and so on).

## Rule 8: Date every number, and separate audit date from finding date

View counts and follower counts move daily. Put the read date in the deliverable's footer and state
explicitly that figures change. If any number came from an earlier session, label it with **that**
date rather than the document's date, and say figures may have moved. A stale number presented as
current is the fastest way to lose an owner's trust.

## What the deliverable contains

Order matters. Lead with the finding that costs them money, not the one that's most technical.

1. **Findings summary** -- the single most important pattern, with real numbers
2. **Immediate free fixes** -- wrong address data, missing profile links
3. **Page-by-page field values** -- per page: current title/description (verified), new title, new
   description, H1 to add
4. **Body copy for blank or thin pages** -- with `[BRACKET]` placeholders for unknown facts
5. **Structured data block** -- `Restaurant`/`LocalBusiness` JSON-LD built from real hours read off
   the site, with a note to confirm they're current
6. **Alt text and social preview** -- counts of what's missing
7. **Off-site items** -- profile fixes, Google Business Profile checklist
8. **Questions only the owner can answer**
9. **Priority table** -- task, effort estimate, why it ranks there
10. **Status line** -- explicitly stating nothing has been applied

## Do not touch the live site

Producing the document requires no CMS access, and that's deliberate. Credentials are not
authorization: editing a real business's live site needs the owner's explicit go-ahead, separately
from whoever handed over a login. Their orders may run through that site.

If access is granted, note that Square Online (and most builders) stage edits as an unpublished draft
until Publish is pressed. Stage everything, let the owner review, then publish.

## Known limitations

- **One site, one platform, one session.** Square Online only. The rendered-DOM rule should
  generalize; the field locations and URL patterns will not.
- **The Square dashboard click-paths are unverified.** Written from general knowledge of Square's
  admin without ever seeing one. Label them unverified in any client-facing document until checked.
- **The JSON-LD has never been validated or published.** Run it through
  `search.google.com/test/rich-results` before claiming it works.
- **The Google Business Profile section is unexercised** -- general practice, not tested. For a local
  business this is plausibly a bigger lever than the entire website.
- **No page-speed measurement.** Core Web Vitals affect ranking and are not covered. `web-perf` is
  installed and would slot in.
- **Adoption unproven.** No owner has yet received or acted on a document produced this way.

See `PENDING-NOTES.md` for the full confirmed/untested/rejected log.
