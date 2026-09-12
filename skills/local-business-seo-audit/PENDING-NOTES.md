# local-business-seo-audit -- Pending Notes

Candidate techniques and claims for this skill, tracked as `[ ] untested` / `[x] confirmed` /
`[-] rejected`. Nothing moves into `SKILL.md` as a stated fact until it's `[x]`.

**Origin:** built 2026-09-06 during a live audit of a real restaurant's Square Online site
([restaurant-a].com) plus their Instagram and TikTok, for the [Restaurant A] favor/portfolio project.
Everything marked confirmed below was observed in that single session against a real production site.

**Single-site caveat:** every `[x]` here was confirmed on exactly ONE site, on one platform
(Square Online), in one session. "Confirmed" means "I saw this actually happen," not "this
generalizes." Second-site validation is the top open item.

---

## Confirmed

### [x] JS-rendered site builders return empty `<title>` and meta tags to `fetch()` -- you must read the rendered DOM
**Found:** sweeping all seven pages of a Square Online site in one `fetch()` loop.
**Symptom:** raw HTML came back 51,744 bytes with `<title>` empty, `meta[name=description]` absent,
and `document.body.innerText` length 0 for every sub-page. The markup was an empty JS app shell.
**Why it matters:** I briefly concluded "titles are empty sitewide," which was **wrong** -- the
rendered `/menu` title was actually `Menu | [Restaurant A]`. A raw-HTML sweep produces a
confident, plausible, false audit.
**The rule:** navigate to each page and read `document.title` / `document.querySelector('meta[...]')`
from the live DOM. Never audit SEO fields from `fetch()` on a builder site.

### [x] A page that reads "empty" may just be slow to render -- verify twice, and screenshot
**Found:** first pass gave `/specials` 1 word and `/catering` 1 word, suggesting both were blank.
**After a 5-second wait:** `/catering` had 82 words of real copy (their catering headline). `/specials` was still empty, and a screenshot confirmed genuine white
space between header and footer.
**Why it matters:** this cut both ways in the same sweep -- one false positive, one true positive.
Declaring a client's page "blank" when it isn't would be an embarrassing, checkable error.
**The rule:** before reporting a page as empty, re-read it with a longer wait AND take a screenshot.
Two independent signals.

### [x] Instagram's embedded page JSON contains the VIEWER's profile fields, not only the viewed profile
**Found:** regexing `"biography":"..."` out of the fetched HTML while on `/[restaurant_a]/`.
**Symptom:** it returned *Chef Andre's* bio ("25+ years in professional kitchens...") -- the
logged-in viewer's own data, embedded in the same page bundle. Nothing in the output signalled the
mismatch; it read as a perfectly plausible answer to the question asked.
**The rule:** read profile fields from the rendered `header` element's `innerText`, not from
regexes over the page bundle. Cross-check anything surprising against a screenshot.

### [x] `credentials:'include'` on an in-page fetch is refused by the browser tool
**Symptom:** the whole call returned `[BLOCKED: Cookie/query string data]` and no result.
**Fix:** omit the option. Same-origin fetches already carry session cookies by default.

### [x] Reel `og:title` identifies the real author, which is how you separate creator collabs from native posts
**Found:** needed to prove "outside creators outperform native content" rather than assert it.
**Method:** fetch each reel permalink and read `meta[property="og:title"]`. A collab post returns
the creator's name and handle (`[Creator] on Instagram: "You have to try @[restaurant_a]..."`),
a native post returns the business (`[Restaurant A] on Instagram: ...`).
**Result:** cleanly separated the top 3 (all collabs: 15,900 / 7,779 / 3,107) from the native median
(1,015) across 18 reels. This turns a vague claim into a sourced one.

### [x] Cross-checking the same business address across every profile finds real NAP errors
**Found:** Instagram bio listed a neighbouring city's ZIP code; the website and TikTok both had the correct one.
The Instagram bio was simply wrong.
**Why it matters:** this was the single most actionable finding of the whole audit and took one
comparison to spot. Always diff address, phone, and hours across website / IG / TikTok / Facebook / Yelp.

### [x] Programmatic length validation catches defects the eye does not -- including ones you introduce while fixing
**Found:** wrote 9 page titles and 9 meta descriptions that "looked fine."
**First validation pass:** 3 descriptions over the ~160-char truncation point (165, 172, 163).
**After editing those:** a re-run caught a **new** 169-char one I had just created by rewriting an
em dash into the word "including," plus em dashes still sitting in a published combo list.
**The rule:** validate with a script, and re-validate after every edit pass. Never hand-check.

### [x] TikTok profile stats are readable when the video grid is not
**Symptom:** the profile header returned followers / following / total likes reliably, but the video
grid rendered `Something went wrong` and yielded zero video links across retries.
**The rule:** treat profile-level numbers as usable and per-video numbers as best-effort. Say
explicitly in the deliverable which one you got, rather than implying you measured both.

### [x] Customer-facing copy needs a `humanizer` pass before it ships under someone else's brand
**Found:** ran the drafted About/Specials/homepage copy through the `humanizer` skill.
**Caught:** a self-answered rhetorical opener ("started with a simple question: why should..."),
an `-ing` participle ("take the idea further, folding..."), a tailing-negation fragment
("No heat lamps, no holding trays."), a false "from X to Y" range, and em dashes throughout.
**Why it matters:** AI tells in a family restaurant's About page are worse than no About page.

---

## Untested

### [ ] Does any of this work on builders other than Square Online?
Only Square Online has been touched. Restaurant sites commonly run on Toast, BentoBox, Wix,
Squarespace, or WordPress. The rendered-DOM rule should hold for any JS-rendered builder, but the
field locations, the custom-code availability, and the URL patterns (`/s/order`, `/s/gift-cards`)
are Square-specific and will not transfer.
**Test plan:** run the same sweep against one Toast or BentoBox restaurant site and diff what breaks.

### [ ] Are the Square dashboard click-paths in the deliverable actually correct?
The "where these fields live in Square Online" table was written from general knowledge of Square's
admin, **not verified in a real Square dashboard** -- I have never had access to one. Any path in it
could be stale or wrong.
**Test plan:** verify against a live Square Online admin before this table ships in a published skill.
Until then it must be labelled as unverified in any client-facing document.

### [ ] Does the generated Restaurant JSON-LD validate and earn a rich result?
The schema block was written but never submitted to `search.google.com/test/rich-results`, never
published, and never observed producing a rich result.
**Test plan:** paste into the validator and record the output. Rich-result eligibility takes weeks
to observe, so validation is the realistic near-term check.

### [ ] Can Square accept the schema block on a normal plan?
Custom code is believed to be gated to higher Square Online tiers, and a body-placed Embed Code
block is believed to work as a fallback since Google reads JSON-LD in the body. Neither has been
confirmed on a real account.

### [ ] Google Business Profile checklist -- entirely unexercised
Written from general local-SEO practice, not run against a real GBP. For a local restaurant this is
plausibly a bigger lever than the whole website, so it deserves real testing before the skill claims
anything about it.

### [ ] Should this skill invoke `web-perf` for Core Web Vitals?
Page speed is a real ranking factor and was never measured on the audited site. `web-perf` is already
installed and would slot in naturally.
**Test plan:** run `web-perf` against the same site and see whether it surfaces anything that changes
the priority order.

### [ ] Does the paste-ready document format actually get used?
The whole deliverable is optimized for someone else pasting values into a CMS. No owner has yet
received it, let alone acted on it. Adoption is unproven, and a beautiful artifact nobody opens is a real failure mode here.

### [ ] "Empty" page can be an image menu, not a blank page ([Restaurant B], 2026-09-12)
`/menu` read 36 words (nav + footer only) at both 4s and 8s waits. Screenshot showed a full menu.
It was one 1275x2100 JPG with no alt. Candidate rule: before calling a page blank, list images with
`naturalWidth > 300` along with their alt. Word count alone can't tell blank from image-only. The
finding ("no readable menu") is arguably worse for SEO than a blank page. Second site, still Square.

### [ ] Diff the site's own claims against its own pages and news (closed location)
Homepage meta description still said "two locations"; the About page on the same site said the second
location had closed. Found only because a news search was run alongside the sweep. Candidate: always
search `"<business>" closed OR opens OR new location` and compare against title/description/schema.

### [ ] Verify a handle before calling a footer link a typo
The X link looked like a typo (a handle apparently missing its final letter) and was briefly reported
to the user as one. It was the real handle. Candidate rule: search the handle before flagging.

### [ ] Rule 5 method worked on a second account, but the "collabs win" pattern did not replicate
[Restaurant B], 2026-09-12: the reels tab grid has no `<a>` around the view counts at first read;
after scrolling, the hrefs appear, and walking up from each leaf count node to its `href` ancestor pairs
counts with permalinks. `og:title` authorship worked again. Result: 18 reels, 17 native (median 525),
1 collab (a local public figure, 2,223), with the best native reel at 2,193. One collab is not a
pattern. Keep the method, don't presume the first site's conclusion. Also: the last numeric leaf in a tile
is views, but a tile with no comments has only two numbers, so likes/comments parsing by position is
unreliable.

### [ ] Public Google Maps listing: what's readable without the owner's login (2026-09-12)
Partial first exercise of the untested GBP section. Readable: name, address, phone, rating/count,
service options, website, and full weekly hours (click "See more hours", then read `table` innerText or
aria-labels like "Tuesday, 12 to 8 PM, Copy open hours"). The place URL's `!3d<lat>!4d<lng>` is the
pin: real `geo` values for the schema without asking the owner. Reviews tab → Sort → Newest, then count
`[data-review-id]` top-level nodes and "Response from the owner" strings (9 of 70 here, 0 of newest 10,
confirmed by screenshot on the unanswered 1-star). Gotchas: any JS result that includes hrefs from the
Maps panel is refused with `[BLOCKED: Cookie/query string data]`, so return text only. The Order online
button couldn't be found by text match, so its destination stayed unverified. Searching the closed
second address returned only the open listing, which doesn't prove the closed profile is marked closed.

### [ ] WebFetch of an Instagram profile silently drops fields
WebFetch summarised `@[restaurant_b]` as having "no physical address" in the bio. The rendered
`header` (once the browser could open instagram.com) showed the full street address. The wrong claim
went into a client doc and had to be corrected. Candidate: WebFetch is not a substitute for the
rendered header on Instagram, same class of failure as Rule 1.

### [ ] Footer Yelp slug may not be the listing with the reviews
Footer linked `-[city]-2`; search indexes `-[city]-3` (~500 reviews). Yelp 403s WebFetch and curl, and the
Chrome extension blocked yelp.com, instagram.com and google.com/maps this session, so it stayed
unverified. Rule 5 (reel og:title analysis) could not run for the same reason.

---

## Rejected

### [-] Sweeping every page with one in-page `fetch()` + `DOMParser` loop
Fast and tempting -- one tool call for the whole site. It returns empty titles and zero body text on
any JS-rendered builder, which looks like a finding rather than a failure. Superseded by
per-page navigation. Keep this entry so the shortcut doesn't get re-invented.

### [-] Regexing `"biography"` (or similar fields) out of Instagram's page bundle
Returns the logged-in viewer's own profile data. Silently wrong. Use the rendered header instead.
