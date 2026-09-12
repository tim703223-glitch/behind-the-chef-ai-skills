# Behind the Chef AI — Skills

Real tools built (and broken, and fixed) while documenting a human learning to work with AI tools for [Behind the Chef AI](https://www.youtube.com/@behind-the-chef-ai). Each skill here comes from an actual production need, not a demo — the write-up for each one covers the real build process: what broke, how it got diagnosed, and what the fix actually was.

## Skills

| Skill | What it does | Write-up |
|---|---|---|
| [smart-multitrack-cut](skills/smart-multitrack-cut/) | Automatically decides which of several recorded video tracks (screen, webcam) should be on screen at each moment, based on real motion/speech signals — then renders the rough cut. | [Full build write-up](skills/smart-multitrack-cut/WRITEUP.md) |
| [local-business-seo-audit](skills/local-business-seo-audit/) | Audits a local business's website and social profiles for SEO and discoverability defects, then writes a paste-ready document of exact field values — no CMS access needed. Built around not trusting your own first answer, because every failure in its build looked like a finding. | [Full build write-up](skills/local-business-seo-audit/WRITEUP.md) |

## How this repo is organized

Each skill gets its own folder under `skills/`, containing:
- `SKILL.md` — the actual usable skill (what it does, prerequisites, how to run it)
- `WRITEUP.md` — the detailed build story: the need, the problems hit and fixed, the honest end result and limitations
- `scripts/` — the real code
- `social/CAPTION.md` — the short version, written for a social post

New skills follow the process in [`docs/SKILL-BUILD-SOP-TEMPLATE.md`](docs/SKILL-BUILD-SOP-TEMPLATE.md).

## License

MIT — use it, fork it, break it, tell us what you fixed.
