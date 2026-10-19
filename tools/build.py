#!/usr/bin/env python3
"""Builds srthsps.github.io from the Wise Words project: the app page, the privacy
policy and terms (from store/*.txt, so the site always matches the game's own
texts), app-ads.txt and images. Run: python3 tools/build.py ../wise-words"""
import html, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "wise-words"))
PLAY = "https://play.google.com/store/apps/details?id=com.wisewords.game"
EMAIL = "srthsps22@gmail.com"

STYLE = """
:root {
  --sky-top: #5ec8ff; --sky-bottom: #c9f3dc;
  --bg: #f6fbff; --surface: #ffffff; --ink: #2b2246; --muted: #675f80; --line: #dfe6f2;
  --accent: #7b4fd6; --accent-ink: #ffffff; --green: #2fb879; --chip: #efe7ff;
  --display: "Fredoka", "Trebuchet MS", system-ui, sans-serif;
  --body: "Atkinson Hyperlegible", "Segoe UI", system-ui, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root { --sky-top: #1b1d4f; --sky-bottom: #4b2f7a; --bg: #15122a; --surface: #211c3a; --ink: #f1edff;
    --muted: #b3a9d1; --line: #342c55; --accent: #b496ff; --accent-ink: #1a1430; --green: #5fd6a5; --chip: #2e2650; color-scheme: dark; }
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--body); font-size: 17px; line-height: 1.6; }
a { color: var(--accent); }
a:focus-visible, .button:focus-visible { outline: 3px solid var(--accent); outline-offset: 3px; }
.wrap { max-width: 1040px; margin: 0 auto; padding-left: max(18px, env(safe-area-inset-left)); padding-right: max(18px, env(safe-area-inset-right)); }
.col { max-width: 70ch; }
h1, h2, h3 { font-family: var(--display); font-weight: 600; line-height: 1.15; text-wrap: balance; margin: 0; }
h1 { font-size: clamp(2.2rem, 6vw, 3.4rem); }
h2 { font-size: 1.55rem; margin: 48px 0 12px; }
h3 { font-size: 1.15rem; margin: 30px 0 8px; }
p { margin: 0 0 14px; }
header.top { padding-block: 16px; }
header.top .wrap { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.brand { display: flex; align-items: center; gap: 10px; font-family: var(--display); font-weight: 600; font-size: 1.15rem; color: var(--ink); text-decoration: none; }
.brand img { width: 36px; height: 36px; border-radius: 9px; }
nav { display: flex; gap: 18px; flex-wrap: wrap; font-size: .95rem; }
nav a { color: var(--muted); text-decoration: none; font-weight: 700; }
nav a:hover { color: var(--accent); }
.hero { background: linear-gradient(180deg, var(--sky-top), var(--sky-bottom)); color: #fff; padding-block: 48px 56px; }
.hero .wrap { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); gap: 36px; align-items: center; }
@media (max-width: 760px) { .hero .wrap { grid-template-columns: minmax(0, 1fr); } }
.hero h1 { color: #fff; text-shadow: 0 2px 0 rgba(43, 34, 70, .35); }
.hero .lede { font-size: 1.2rem; margin-top: 14px; text-shadow: 0 1px 0 rgba(43, 34, 70, .3); }
.hero .icon { width: 88px; height: 88px; border-radius: 22px; box-shadow: 0 6px 18px rgba(30, 20, 60, .25); margin-bottom: 18px; }
.hero figure { margin: 0; }
.hero figure img { width: 100%; max-width: 100%; border-radius: 18px; box-shadow: 0 10px 30px rgba(30, 20, 60, .3); display: block; }
.button { display: inline-flex; align-items: center; gap: 10px; background: var(--green); color: #fff; font-family: var(--display); font-weight: 600;
  font-size: 1.1rem; padding: 12px 22px; border-radius: 999px; text-decoration: none; box-shadow: 0 4px 0 rgba(0, 0, 0, .18); margin-top: 22px; }
.note { font-size: .92rem; color: var(--muted); }
.hero .note { color: #fff; opacity: .92; margin-top: 10px; }
.features { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; margin-top: 8px; }
.feature { background: var(--surface); border: 1px solid var(--line); border-radius: 16px; padding: 16px 18px; min-width: 0; }
.feature h3 { margin: 0 0 6px; }
.shots { display: flex; gap: 14px; overflow-x: auto; padding-bottom: 8px; scroll-snap-type: x mandatory; }
.shots img { width: 220px; flex: 0 0 auto; border-radius: 16px; border: 1px solid var(--line); scroll-snap-align: start; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 6px 0 0; padding: 0; list-style: none; }
.chips li { background: var(--chip); border-radius: 999px; padding: 4px 12px; font-weight: 700; font-size: .92rem; }
.card { display: grid; grid-template-columns: 96px minmax(0, 1fr); gap: 18px; align-items: center; background: var(--surface);
  border: 1px solid var(--line); border-radius: 20px; padding: 18px; text-decoration: none; color: inherit; }
.card img { width: 96px; height: 96px; border-radius: 22px; }
.card h3 { margin: 0 0 4px; }
.legal h1 { font-size: clamp(1.9rem, 5vw, 2.6rem); margin-top: 28px; }
.legal .meta { color: var(--muted); margin: 8px 0 26px; }
.legal ul { padding-left: 1.2em; margin: 0 0 14px; }
.legal li { margin-bottom: 6px; }
footer { border-top: 1px solid var(--line); margin-top: 56px; padding-block: 24px 40px; color: var(--muted); font-size: .92rem; }
footer .wrap { display: flex; gap: 18px; flex-wrap: wrap; justify-content: space-between; }
"""

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>' \
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600&family=Atkinson+Hyperlegible:wght@400;700&display=swap">'


def page(title, description, body, depth, canonical):
    up = "/"  # the site lives at the domain root
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="https://srthsps.github.io/{canonical}">
<link rel="icon" type="image/png" href="{up}images/wise-words-icon.png">
{FONTS}
<style>{STYLE}</style>
</head>
<body>
<header class="top"><div class="wrap">
  <a class="brand" href="{up}"><img src="{up}images/wise-words-icon.png" alt="">Sarath PS</a>
  <nav aria-label="Site"><a href="{up}wise-words/">Wise Words</a><a href="{up}wise-words/privacy/">Privacy</a><a href="{up}wise-words/terms/">Terms</a><a href="mailto:{EMAIL}">Contact</a></nav>
</div></header>
{body}
<footer><div class="wrap">
  <span>© 2026 Sarath PS</span>
  <span><a href="{up}wise-words/privacy/">Privacy policy</a> · <a href="{up}wise-words/terms/">Terms</a> · <a href="mailto:{EMAIL}">{EMAIL}</a></span>
</div></footer>
</body>
</html>
"""


def link(text):
    t = html.escape(text)
    t = re.sub(r"(https?://[^\s)<]+[^\s).,<])", r'<a href="\1">\1</a>', t)
    t = re.sub(r"(?<![\w/>])((?:creativecommons\.org|wiktionary\.org|kaikki\.org)(?:/[^\s),<]*[^\s).,<])?)", r'<a href="https://\1">\1</a>', t)
    t = t.replace(EMAIL, f'<a href="mailto:{EMAIL}">{EMAIL}</a>')
    return t


def legal(path, depth, canonical, title):
    lines = open(path, encoding="utf-8").read().splitlines()
    heading = lines[0]
    out, para, bullets = [], [], []
    meta = ""

    def flush():
        if para:
            out.append("<p>" + link(" ".join(para)) + "</p>")
            para.clear()
        if bullets:
            out.append("<ul>" + "".join(f"<li>{link(b)}</li>" for b in bullets) + "</ul>")
            bullets.clear()

    for line in lines[1:]:
        s = line.strip()
        if s.startswith("Effective date:"):
            meta = s
            continue
        if not s:
            flush()
            continue
        if re.match(r"^\d+\.\s+[A-Z][A-Z ,'&-]+$", s):
            flush()
            num, name = s.split(" ", 1)
            out.append(f"<h2>{num} {html.escape(name.capitalize())}</h2>")
            continue
        if s.startswith("- "):
            if para:
                flush()
            bullets.append(s[2:])
            continue
        if bullets:
            flush()
        para.append(s)
    flush()
    body = f"""<main class="wrap legal"><div class="col">
<h1>{html.escape(title)}</h1>
<p class="meta">Wise Words · {html.escape(meta)}</p>
{chr(10).join(out)}
</div></main>"""
    return page(f"{title} – Wise Words", f"{title} for the Wise Words word puzzle game.", body, depth, canonical)


def main():
    img = os.path.join(ROOT, "images")
    os.makedirs(img, exist_ok=True)
    shutil.copy(os.path.join(GAME, "store", "icon-512.png"), os.path.join(img, "wise-words-icon.png"))
    subprocess.run(["magick", os.path.join(GAME, "store", "en-US", "feature-graphic.png"), "-quality", "86",
                    os.path.join(img, "wise-words-feature.jpg")], check=True)
    shots = [("01-climb", "Climb a crossword into the sky"), ("02-special-tiles", "Fog, bombs, critters and more"),
             ("03-daily-bloom", "A new puzzle every day"), ("06-seven-languages", "Crosswords in 7 languages"),
             ("04-word-stories", "Every word has a story")]
    for name, _ in shots:
        subprocess.run(["magick", os.path.join(GAME, "store", "en-US", "screenshots", name + ".png"), "-resize", "440x",
                        "-quality", "82", os.path.join(img, f"wise-words-{name}.jpg")], check=True)

    # Developer home
    home = f"""<main>
<section class="hero"><div class="wrap">
  <div>
    <h1>Games and apps by Sarath PS</h1>
    <p class="lede">Friendly, ad-light games for kids and grown-ups.</p>
  </div>
  <figure><img src="images/wise-words-feature.jpg" alt="Wise Words: climb a crossword into the sky" width="1024" height="500"></figure>
</div></section>
<div class="wrap">
  <h2>Apps</h2>
  <a class="card" href="wise-words/">
    <img src="images/wise-words-icon.png" alt="" width="96" height="96">
    <div><h3>Wise Words</h3><p class="note" style="margin:0">An endless crossword that grows into the sky, in 7 languages. Android.</p></div>
  </a>
  <h2>Contact</h2>
  <p class="col">Questions, feedback or a word meaning that looks wrong? Email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
</div>
</main>"""
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(
        page("Sarath PS – games and apps", "Games and apps by Sarath PS, including Wise Words.", home, 0, ""))

    # App page
    shot_tags = "".join(f'<img src="../images/wise-words-{n}.jpg" alt="{html.escape(a)}" width="440" height="782" loading="lazy">' for n, a in shots)
    app = f"""<main>
<section class="hero"><div class="wrap">
  <div>
    <img class="icon" src="../images/wise-words-icon.png" alt="" width="88" height="88">
    <h1>Wise Words</h1>
    <p class="lede">Swipe letters, grow the vine, climb into the sky. One endless crossword that grows upward, ledge by ledge, and teaches you a new word with every swipe.</p>
    <a class="button" href="{PLAY}">Get it on Google Play</a>
    <p class="note">Now in testing on Google Play, coming soon for everyone. Android.</p>
  </div>
  <figure><img src="../images/wise-words-feature.jpg" alt="Wise Words feature graphic: Lexi the owl on a crossword tower" width="1024" height="500"></figure>
</div></section>
<div class="wrap">
  <h2>Screenshots</h2>
  <div class="shots">{shot_tags}</div>
  <h2>What's inside</h2>
  <div class="features">
    <div class="feature"><h3>A crossword that grows</h3><p>Every puzzle is a new ledge on the Word Vine. No level-complete screens, just the next ledge, a little higher.</p></div>
    <div class="feature"><h3>Seven languages</h3><p>Crosswords, menus and word meanings in each language, with its own climb and world ranking.</p>
      <ul class="chips"><li>English</li><li>Deutsch</li><li>Français</li><li>Español</li><li>Português</li><li>Italiano</li><li>Nederlands</li></ul></div>
    <div class="feature"><h3>Eight special tiles</h3><p>Ice, bombs, mystery tiles, fog, golden buds, lightning, moss, and critters to catch for your collection.</p></div>
    <div class="feature"><h3>A new puzzle every day</h3><p>The Daily Bloom: fill your calendar, keep your streak, win a flower frame each month.</p></div>
    <div class="feature"><h3>Every word has a story</h3><p>Meanings for every word you solve, your own Word Book, and 92 rare treasure words to find.</p></div>
    <div class="feature"><h3>Fair and friendly</h3><p>No timers, no fail state, no purchases and no pop-up ads. Optional reward videos only.</p></div>
  </div>
  <h2>Privacy and terms</h2>
  <p class="col">Read the <a href="privacy/">privacy policy</a> and the <a href="terms/">terms</a>. To delete your data, open your profile in the game and tap "Delete my data", or email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
</div>
</main>"""
    os.makedirs(os.path.join(ROOT, "wise-words"), exist_ok=True)
    open(os.path.join(ROOT, "wise-words", "index.html"), "w", encoding="utf-8").write(
        page("Wise Words – a crossword that grows into the sky", "Wise Words: an endless crossword word puzzle for Android, in 7 languages.", app, 1, "wise-words/"))

    for sub, src, title in [("privacy", "privacy-policy.txt", "Privacy Policy"), ("terms", "terms-and-conditions.txt", "Terms and Conditions")]:
        d = os.path.join(ROOT, "wise-words", sub)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(
            legal(os.path.join(GAME, "store", src), 2, f"wise-words/{sub}/", title))

    open(os.path.join(ROOT, "app-ads.txt"), "w").write("google.com, pub-7021910910381177, DIRECT, f08c47fec0942fa0\n")
    open(os.path.join(ROOT, ".nojekyll"), "w").write("")
    open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8").write(page("Page not found – Sarath PS", "Page not found.",
        '<main class="wrap col"><h1 style="margin-top:40px">Page not found</h1><p>Go to <a href="/">the home page</a>.</p></main>', 0, ""))
    print("built", ROOT)


main()
