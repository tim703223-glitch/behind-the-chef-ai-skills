# local-business-seo-audit -- Build Write-Up

Built 2026-09-06, in one session, while doing a real audit for a real restaurant.

---

## 1. The Need

A local restaurant near me had become an accidental side project. A few weeks back I'd looked
through their Instagram and written up some recommendations as a favor, plus a portfolio piece. That
document sat in a folder. Nothing had been shown to the owner.

Then I decided to actually go see them, and asked Claude for a one-page PDF I could hand over.

That's where this skill really started, though not for the reason I expected. The one-sheet came back
fast and looked great. Then I asked a question that changed the whole session:

> "did you do a review of the social media before writing this?"

It hadn't. Every number on that sheet had been lifted out of the write-up from six weeks earlier. The
footer said "Prepared September 2026" and the opening line said "I went through the last 60 posts" in
present tense. Read together, that tells a business owner the review is current when it was a month
and a half stale.

Nobody had lied. The numbers were real numbers. But I was forty minutes from walking into someone's
restaurant with a document that quietly misrepresented when it had been made.

So the need was: **do the review live, and build the thing that makes a live review repeatable** --
because I'm going to want to do this again for other businesses, and I never want to be in that
position twice.

## 2. The Build Journey

### Problem 1: the audit that was confidently wrong

First real attempt at the website half. Their site is Square Online, seven pages. The obvious move
was to fetch all seven in one loop and read the SEO fields out of the HTML. One tool call, whole site
audited.

The result came back clean and damning: every page title empty, every meta description absent, no
structured data anywhere.

I was one step from writing that down. What stopped it was that the homepage had returned
`Home | [Restaurant A]` while every sub-page returned nothing at all. That's a weird failure shape.
Sites don't usually set a title on exactly one page.

Checked one sub-page properly, by navigating to it and reading the live DOM instead of the raw
markup. Its actual title was `Menu | [Restaurant A]`. Present the whole time.

Square Online, like most modern site builders, serves an empty JavaScript shell. All 51,744 bytes of
`/about-us` contained no title, no meta tags, and zero body text, because none of it exists until the
browser builds the page. The fetch hadn't failed. It had succeeded at retrieving nothing, and
"nothing" looks exactly like "this business has no SEO set up."

**The fix:** navigate to each page, wait for render, read from the live DOM. Slower, more tool calls,
correct. Batched into navigate/read pairs so seven pages costs two calls instead of fourteen.

That's rule one of the skill, and honestly it's the reason the skill exists at all. An AI producing a
plausible wrong answer is more dangerous than one producing an obvious error, because there's nothing
to notice.

### Problem 2: the fix created a new false conclusion

Re-ran with rendered DOM. Now `/specials` and `/catering` both came back with one word of content,
which suggested two blank pages in their navigation.

That's a strong claim to make about someone's business. It's also trivially checkable by the owner,
so being wrong would be embarrassing in a specific way.

Re-read both with a five second wait instead of one and a half, and took a screenshot.

`/catering` had 82 words of real copy that simply hadn't rendered yet: *[their catering headline]* Good copy, actually.

`/specials` was genuinely, truly empty. The screenshot showed white space between the header and the
footer.

So the same check produced one false positive and one true positive in a single pass. And the true
positive turned out to be the most valuable finding of the whole audit: `/specials` is exactly where
their weekly limited-flavor drops should live. They post those to Instagram every single week. The
page built for them is blank.

**The fix:** never report a page as empty without a second read at a longer wait plus a screenshot.
Two independent signals.

### Problem 3: the wrong account's data, with nothing to signal it

While pulling the Instagram profile, I regexed the `biography` field out of the page bundle.

It returned: *"25+ years in professional kitchens. Real technique, real science."*

That is not a restaurant's bio. That's the bio of the AI chef character I build for this project. It
was my own logged-in account's data, embedded in the same page payload, and the regex grabbed the
first match.

Nothing about the output flagged it. It arrived as a clean, plausible answer to the question I'd
asked. If I hadn't recognized my own words, that bio could have gone into a document about somebody
else's business.

**The fix:** read profile fields from the rendered header element, not from regexes over a page
bundle. Logged as a rejected technique so I don't rebuild the shortcut later.

### Problem 4: fixing three defects created a fourth

The deliverable ended up being nine page titles and nine meta descriptions, plus body copy. Titles
truncate in Google around 60 characters, descriptions around 160.

They all looked fine. I had Claude validate them with a script instead of by eye. Three descriptions
were over the limit: 165, 172, 163.

Fixed those three. Re-ran the validator.

**A fourth violation appeared.** Rewriting an em dash into the word "including" had pushed the
catering description to 169. The same pass also left em dashes sitting in a published combo list.

The fix had introduced the defect. If validation had run once at the end instead of after every edit,
that 169-character description ships.

**The fix:** re-validate after every edit pass, not once. This is now the only script that ships with
the skill, and I made Claude prove it works by feeding it a deliberately broken document -- all five
injected defects caught, and it correctly stayed quiet on the placeholder lines that get deleted
before publishing. A validator that returns green on a clean file hasn't demonstrated anything.

### Problem 5: the copy sounded like a robot wrote it

The document included real body copy for their two blank pages, meant to go live under a family
business's name.

Ran it through the `humanizer` skill. It caught a self-answered rhetorical opener ("started with a
simple question: why should a [dish]..."), a participle clause bolted on for fake depth, a
tailing-negation fragment ("No heat lamps, no holding trays."), a false "from X to Y" range, and em
dashes throughout.

Every one of those is a tell. AI-sounding copy on a family restaurant's About page is worse than
having no About page.

### The thing I refused to write

The About page needs a founding story. Who started it, what year, why this food.

I don't know any of that, and neither does Claude. The structurally easy move is to write something
warm and plausible about family recipes and generations, and it would have read beautifully.

Instead the section ships with `[BRACKETS]` marking every unknown fact and a warning not to publish
it as-is, plus a list of seven questions only the owner can answer. That constraint is now rule seven
of the skill.

Inventing a family's history to fill a content gap isn't a small liberty. It's the kind of thing that
would be quoted back at you.

---

## 3. Final Write-Up

**Purpose.** Point it at a local business's website and social accounts. It finds what's actually
broken for search and discovery, then writes a document listing the exact text to paste into each
field, so whoever runs the site can fix it without needing to understand SEO or hand over a password.

**Why it needed a human and an AI together.** Claude did the work no person wants to do: reading nine
pages field by field, checking 40 images for alt text, pulling view counts and authorship off 18
Instagram reels, counting characters. That's the boring, high-volume, error-prone half, and it was
fast and accurate at it.

But the two moments that decided whether this session produced something honest were both human.
Asking "did you actually look at the social media before writing this?" is what caught six-week-old
numbers being presented as current. And noticing that one page had a title while six didn't is what
caught the false audit before it got written down.

The pattern I'd draw from it: the AI was reliable at gathering and terrible at knowing when its
gathering had silently failed. Every failure in this session looked like a finding.

**End result.** Concretely, things that are true now and weren't this morning:

- Their top three Instagram reels are, provably, all outside-creator visits: 15,900 / 7,779 / 3,107
  views against a native median of 1,015 across 18 reels. That's roughly 15x, and it's sourced from
  per-post authorship rather than asserted.
- Their Instagram bio has the wrong ZIP code. It lists a neighbouring city's code while their website
  and TikTok both have it right. One comparison found it. It's free to fix and it affects local
  ranking.
- They have more followers on TikTok than Instagram, and their own website footer doesn't link
  TikTok at all.
- Two pages in their navigation are completely blank, one of which is where their best recurring
  content should live.
- There's a document with nine page titles, nine meta descriptions, body copy for the blank pages,
  and a complete structured-data block built from their real posted hours -- all length-validated,
  all paste-ready.

None of it has been applied. I have no access to their site, and I'm not going to touch a live
business's website on a borrowed login. Credentials aren't authorization. Their orders run through
that thing.

**Known limitations.** Being straight about these, because the skill is version 0.1.0 and shouldn't
pretend otherwise:

- **One site, one platform, one session.** Square Online only. The read-the-rendered-DOM rule should
  hold for any JavaScript builder, but the field locations and URL patterns are Square-specific and
  won't transfer. Restaurants commonly run Toast or BentoBox. Untested there.
- **The Square dashboard click-paths are unverified.** The table saying where each field lives was
  written from general knowledge of Square's admin. I have never had access to one. Any path in it
  could be wrong, and it stays labelled unverified in client documents until somebody checks.
- **The structured-data block has never been validated or published.** It was never submitted to
  Google's Rich Results Test. It might have an error in it.
- **The Google Business Profile section is entirely unexercised.** Written from general local-SEO
  practice. For a local restaurant that's plausibly a bigger lever than the whole website, which
  makes it the least tested part of the most important thing.
- **No page speed measurement.** Core Web Vitals affect ranking and aren't covered at all.
- **Nobody has used the document yet.** The owner hasn't seen it. A well-built deliverable that
  nobody opens is a real failure mode, and I've hit it before on this project.

Full confirmed / untested / rejected log is in `PENDING-NOTES.md`. At build time: nine confirmed, seven untested, two rejected. Untested notes from a second site
have been added since.
