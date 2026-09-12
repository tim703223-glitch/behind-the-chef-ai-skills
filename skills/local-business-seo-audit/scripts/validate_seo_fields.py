#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
validate_seo_fields.py -- length and AI-tell validation for a local-business SEO
implementation document.

Run this after EVERY edit pass, not once at the end. On the session this skill was
built in, the first pass caught 3 over-length meta descriptions; the pass after
fixing them caught a 4th that the fix itself had introduced.

Usage:
    python validate_seo_fields.py <implementation-doc.md> [--max-title 60] [--max-desc 160]

Expects the document to mark fields in this shape (the format SKILL.md produces):

    - **New title:** `Some Title Here`
    - **New description:**
      > Some description text on one line.

Published body copy is expected in fenced blocks that begin with "H1:".

Exit code 0 = clean, 1 = problems found. Output is ASCII-safe so it survives
Windows consoles using cp1252.
"""

import argparse
import io
import re
import sys

EM_DASH = u"—"
EN_DASH = u"–"
CURLY = [u"“", u"”", u"‘", u"’"]

# Google truncates around these; they are guidelines, not hard API limits.
DEFAULT_MAX_TITLE = 60
DEFAULT_MAX_DESC = 160
SHORT_DESC = 110  # below this, you are wasting available snippet space

TITLE_RE = re.compile(r"\*\*New title:\*\*\s*`([^`]+)`")
DESC_RE = re.compile(r"\*\*New description:\*\*\s*\n\s*>\s*(.+)")
COPY_BLOCK_RE = re.compile(r"```\s*\n(H1:.*?)```", re.S)


def ascii_safe(text):
    """Windows consoles default to cp1252 and raise on smart punctuation."""
    return text.encode("ascii", "replace").decode("ascii")


def check_lengths(label, values, limit, short=None):
    problems = []
    lines = ["=== %s (max %d) ===" % (label, limit)]
    for value in values:
        n = len(value)
        if n > limit:
            problems.append("%s too long (%d): %s" % (label, n, value))
            flag = "LONG"
        elif short is not None and n < short:
            flag = "short"
        else:
            flag = "ok"
        lines.append("  %-5s %3d  %s" % (flag, n, value[:64]))
    if not values:
        lines.append("  (none found -- check the document's field format)")
    return lines, problems


def check_ai_tells(values, where):
    """Dashes and curly quotes in text that will be published."""
    problems = []
    for value in values:
        if EM_DASH in value or EN_DASH in value:
            problems.append("dash in %s: %s" % (where, value[:70]))
        for q in CURLY:
            if q in value:
                problems.append("curly quote in %s: %s" % (where, value[:70]))
                break
    return problems


def check_copy_blocks(text):
    """Scan published body-copy blocks. [BRACKET] lines are author instructions
    that get deleted before publishing, so they are exempt."""
    lines = ["=== published copy blocks ==="]
    problems = []
    blocks = COPY_BLOCK_RE.findall(text)
    lines.append("  blocks found: %d" % len(blocks))
    for block in blocks:
        for raw in block.split("\n"):
            line = raw.strip()
            if not line or "[" in line:
                continue
            if EM_DASH in line or EN_DASH in line:
                problems.append("dash in copy: %s" % line[:70])
            for q in CURLY:
                if q in line:
                    problems.append("curly quote in copy: %s" % line[:70])
                    break
    if not blocks:
        lines.append("  (no H1: blocks found -- none to check)")
    return lines, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("doc")
    ap.add_argument("--max-title", type=int, default=DEFAULT_MAX_TITLE)
    ap.add_argument("--max-desc", type=int, default=DEFAULT_MAX_DESC)
    args = ap.parse_args()

    try:
        text = io.open(args.doc, encoding="utf-8").read()
    except IOError as exc:
        sys.stderr.write("cannot read %s: %s\n" % (args.doc, exc))
        return 2

    titles = TITLE_RE.findall(text)
    descs = DESC_RE.findall(text)

    out = []
    problems = []

    lines, probs = check_lengths("titles", titles, args.max_title)
    out += lines + [""]
    problems += probs

    lines, probs = check_lengths("descriptions", descs, args.max_desc, short=SHORT_DESC)
    out += lines + [""]
    problems += probs

    problems += check_ai_tells(titles, "title")
    problems += check_ai_tells(descs, "description")

    lines, probs = check_copy_blocks(text)
    out += lines + [""]
    problems += probs

    out.append("=== result ===")
    if problems:
        out.append("  %d problem(s):" % len(problems))
        for p in problems:
            out.append("   - " + p)
    else:
        out.append("  clean: %d titles, %d descriptions" % (len(titles), len(descs)))

    sys.stdout.write(ascii_safe("\n".join(out)) + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
