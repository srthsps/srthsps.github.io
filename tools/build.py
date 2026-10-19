#!/usr/bin/env python3
"""Builds srthsps.github.io from the Wise Words project.

The home page is the Wise Words page; /wise-words/ forwards to it. The privacy
policy and terms are generated from the game's own texts (store/*.txt), so the
site always says what the game says. Art comes from the game too: gameplay
frames (build/store_raw_*.png, from tests/StoreShots.tscn) and Lexi, flags and
critters (build/site/*.png, from tests/SiteArt.tscn).

    python3 tools/build.py ../wise-words
"""
import html
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "wise-words"))
PLAY = "https://play.google.com/store/apps/details?id=com.wisewords.game"
EMAIL = "srthsps22@gmail.com"
SITE = "https://srthsps.github.io/"

# The game's letter-tile colours (UITheme.LETTER_COLORS).
TILE = ["#ff6fa8", "#ff9f43", "#ffd23f", "#3ddc97", "#4cc9f0", "#9b5de5", "#ff5d73"]

STYLE = """
/* Layout: one sky at the top like the game's first world (Starry Night in dark
   mode), rolling hills into the page, then alternating screenshot/text rows. */
:root {
  --sky-top: #5ec8ff; --sky-bottom: #c8f4d6; --hill-back: #7fd99a; --hill-mid: #5fd38d;
  --bg: #fbfcf7; --surface: #ffffff; --ink: #281f45; --muted: #5d5678; --line: #e3e6ee;
  --hero-ink: #1f1840; --accent: #7b4fd6; --play: #22a96b; --chip: #f0eaff; --phone: #251d45;
  --star: transparent;
  --display: "Fredoka", "Trebuchet MS", system-ui, sans-serif;
  --body: "Atkinson Hyperlegible", "Segoe UI", system-ui, sans-serif;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root { --sky-top: #0f1340; --sky-bottom: #4a2f86; --hill-back: #2c2470; --hill-mid: #3b2f8c;
    --bg: #14112b; --surface: #1f1a3d; --ink: #f2eeff; --muted: #b6acd6; --line: #332b58;
    --hero-ink: #ffffff; --accent: #b89bff; --play: #2fc27f; --chip: #2c2554; --phone: #0b0920;
    --star: rgba(255, 255, 255, .9); color-scheme: dark; }
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } * { animation: none !important; } }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--body); font-size: 17px; line-height: 1.6; }
a { color: var(--accent); }
a:focus-visible, .play:focus-visible { outline: 3px solid var(--accent); outline-offset: 3px; border-radius: 8px; }
img { max-width: 100%; height: auto; }
.wrap { max-width: 1080px; margin: 0 auto; padding-left: max(18px, env(safe-area-inset-left)); padding-right: max(18px, env(safe-area-inset-right)); }
h1, h2, h3 { font-family: var(--display); font-weight: 600; line-height: 1.12; text-wrap: balance; margin: 0; }
h2 { font-size: clamp(1.7rem, 4vw, 2.3rem); }
h3 { font-size: 1.2rem; }
p { margin: 0 0 14px; }
.eyebrow { font-family: var(--display); font-weight: 600; letter-spacing: .08em; text-transform: uppercase; font-size: .82rem; color: var(--accent); margin-bottom: 8px; }

/* Sky */
.sky { position: relative; overflow: hidden; color: var(--hero-ink);
  background: linear-gradient(180deg, var(--sky-top) 0%, var(--sky-bottom) 92%); }
.sky::before { content: ""; position: absolute; inset: 0; pointer-events: none; opacity: .9;
  background-image: radial-gradient(1.6px 1.6px at 8% 18%, var(--star), transparent 60%), radial-gradient(1.2px 1.2px at 22% 42%, var(--star), transparent 60%),
    radial-gradient(1.8px 1.8px at 37% 12%, var(--star), transparent 60%), radial-gradient(1.2px 1.2px at 51% 30%, var(--star), transparent 60%),
    radial-gradient(1.6px 1.6px at 66% 9%, var(--star), transparent 60%), radial-gradient(1.2px 1.2px at 79% 36%, var(--star), transparent 60%),
    radial-gradient(1.8px 1.8px at 91% 16%, var(--star), transparent 60%), radial-gradient(1.2px 1.2px at 14% 64%, var(--star), transparent 60%),
    radial-gradient(1.4px 1.4px at 58% 58%, var(--star), transparent 60%), radial-gradient(1.2px 1.2px at 86% 60%, var(--star), transparent 60%); }
.cloud { position: absolute; width: 150px; height: 46px; border-radius: 40px; background: rgba(255, 255, 255, .55); filter: blur(.3px); pointer-events: none;
  animation: drift 60s linear infinite; }
.cloud::before, .cloud::after { content: ""; position: absolute; background: inherit; border-radius: 50%; }
.cloud::before { width: 70px; height: 70px; left: 22px; top: -34px; }
.cloud::after { width: 54px; height: 54px; right: 24px; top: -24px; }
@media (prefers-color-scheme: dark) { .cloud { background: rgba(185, 180, 255, .14); } }
@keyframes drift { from { transform: translateX(-4vw); } 50% { transform: translateX(4vw); } to { transform: translateX(-4vw); } }
.hills { display: block; width: 100%; height: clamp(60px, 9vw, 120px); margin-top: -1px; }

/* Header */
.top { position: relative; z-index: 2; padding-block: 14px; }
.top .wrap { display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap; }
.brand { display: flex; align-items: center; gap: 10px; text-decoration: none; color: var(--hero-ink); font-family: var(--display); font-weight: 600; font-size: 1.2rem; }
.brand img { width: 38px; height: 38px; border-radius: 10px; box-shadow: 0 2px 6px rgba(20, 10, 60, .2); }
.top nav { display: flex; gap: 18px; flex-wrap: wrap; font-weight: 700; font-size: .95rem; }
.top nav a { color: var(--hero-ink); text-decoration: none; opacity: .82; }
.top nav a:hover { opacity: 1; }

/* Hero */
.hero { position: relative; z-index: 1; display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(0, .85fr); gap: 32px; align-items: center; padding-block: 40px 10px; }
@media (max-width: 820px) { .hero { grid-template-columns: minmax(0, 1fr); text-align: center; } .hero .actions { justify-content: center; } .logo { justify-content: center; } .stage { margin-top: 56px; } }
.logo { display: flex; flex-direction: column; gap: .14em; font-size: clamp(2.7rem, 8.5vw, 5rem); margin: 0 0 18px; }
.logo .line { display: flex; gap: .1em; flex-wrap: nowrap; }
@media (max-width: 820px) { .logo .line { justify-content: center; } }
.tile { display: inline-grid; place-items: center; width: 1.08em; height: 1.08em; border-radius: .24em; background: var(--t); color: #fff;
  font-family: var(--display); font-weight: 600; font-size: 1em; line-height: 1; transform: rotate(var(--r, 0deg));
  box-shadow: inset 0 -.1em 0 rgba(0, 0, 0, .22), 0 .08em .16em rgba(20, 10, 60, .25);
  text-shadow: 0 .04em 0 rgba(40, 20, 70, .45), 0 0 .06em rgba(40, 20, 70, .6); }
.tagline { font-family: var(--display); font-weight: 500; font-size: clamp(1.2rem, 3vw, 1.75rem); line-height: 1.25; margin-bottom: 10px; }
.lede { font-size: 1.08rem; max-width: 34em; }
@media (max-width: 820px) { .lede { margin-inline: auto; } }
.actions { display: flex; flex-wrap: wrap; align-items: center; gap: 12px 18px; margin-top: 22px; }
.play { display: inline-flex; align-items: center; gap: 10px; background: var(--play); color: #fff; text-decoration: none; font-family: var(--display); font-weight: 600;
  font-size: 1.12rem; padding: 13px 24px; border-radius: 999px; box-shadow: inset 0 -4px 0 rgba(0, 0, 0, .2), 0 6px 16px rgba(10, 60, 30, .22); }
.play svg { width: 20px; height: 20px; }
.soon { font-size: .92rem; font-weight: 700; opacity: .85; }

/* Phone */
.stage { position: relative; justify-self: center; width: min(300px, 74vw); }
.phone { background: var(--phone); border-radius: 38px; padding: 10px; box-shadow: 0 24px 48px rgba(20, 10, 60, .28); transform: rotate(-3deg); }
.phone img { display: block; width: 100%; aspect-ratio: 9 / 16; object-fit: cover; border-radius: 30px; }
.stage .lexi { position: absolute; width: 44%; right: -16%; top: -11%; transform: rotate(6deg); filter: drop-shadow(0 6px 10px rgba(20, 10, 60, .25)); }

/* Sections */
section { padding-block: 64px; }
.steps { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; margin-top: 26px; }
@media (max-width: 760px) { .steps { grid-template-columns: minmax(0, 1fr); } }
.step { background: var(--surface); border: 1px solid var(--line); border-radius: 20px; padding: 20px; min-width: 0; }
.step .tile { font-size: 1.8rem; margin-bottom: 12px; }
.step h3 { margin-bottom: 6px; }
.step p { color: var(--muted); margin: 0; }
.row { display: grid; grid-template-columns: minmax(0, .8fr) minmax(0, 1.2fr); gap: 44px; align-items: center; }
.row + .row { margin-top: 72px; }
.row.flip .shot { order: 2; }
@media (max-width: 760px) { .row { grid-template-columns: minmax(0, 1fr); gap: 22px; } .row.flip .shot { order: 0; } }
.shot { justify-self: center; width: min(270px, 70vw); }
.shot .phone { transform: rotate(var(--r, 2deg)); }
.row p { color: var(--muted); max-width: 32em; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 14px 0 0; padding: 0; list-style: none; }
.chips li { background: var(--chip); border-radius: 999px; padding: 4px 13px; font-weight: 700; font-size: .92rem; }
.band { background: var(--surface); border-block: 1px solid var(--line); }
.critters { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px 26px; margin-top: 22px; }
.critters figure { margin: 0; text-align: center; font-weight: 700; color: var(--muted); font-size: .95rem; }
.critters img { width: 92px; height: 92px; display: block; margin: 0 auto 2px; }
.flags { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 14px; margin-top: 24px; }
.flag { display: flex; align-items: center; gap: 10px; background: var(--surface); border: 1px solid var(--line); border-radius: 16px; padding: 10px 12px; font-weight: 700; min-width: 0; }
.flag img { width: 44px; height: 30px; flex: 0 0 auto; }
.promises { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px 26px; margin: 22px 0 0; padding: 0; list-style: none; }
.promises li { padding-left: 30px; position: relative; }
.promises li::before { content: ""; position: absolute; left: 0; top: .3em; width: 18px; height: 18px; border-radius: 6px; background: var(--t, #3ddc97);
  box-shadow: inset 0 -3px 0 rgba(0, 0, 0, .2); }
.finale { text-align: center; }
.finale img { width: 150px; display: block; margin: 0 auto 6px; }
.finale .actions { justify-content: center; }

/* Legal pages */
.legal-sky .hills { height: clamp(40px, 6vw, 70px); }
.legal-head { position: relative; z-index: 1; padding-block: 18px 6px; }
.legal-head h1 { font-size: clamp(2rem, 5vw, 2.8rem); }
.legal-head p { margin: 6px 0 0; opacity: .85; font-weight: 700; }
.legal { max-width: 72ch; padding-block: 22px 10px; }
.legal h2 { font-size: 1.35rem; margin: 40px 0 10px; }
.legal ul { padding-left: 1.2em; margin: 0 0 14px; }
.legal li { margin-bottom: 6px; }

footer { border-top: 1px solid var(--line); padding-block: 26px 44px; color: var(--muted); font-size: .92rem; }
footer .wrap { display: flex; gap: 12px 24px; flex-wrap: wrap; justify-content: space-between; }
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600&family=Atkinson+Hyperlegible:wght@400;700&display=swap">')
PLAY_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#fff" d="M4 2.8v18.4c0 .7.8 1.1 1.4.7l15.2-9.2c.6-.4.6-1.2 0-1.5L5.4 2.1C4.8 1.7 4 2.1 4 2.8z"/></svg>')
HILLS = ('<svg class="hills" viewBox="0 0 1440 120" preserveAspectRatio="none" aria-hidden="true">'
         '<path fill="var(--hill-back)" d="M0 62 C 180 18 360 18 540 52 S 900 96 1080 54 S 1350 10 1440 34 V120 H0 Z"/>'
         '<path fill="var(--hill-mid)" d="M0 84 C 240 48 420 60 640 82 S 1060 110 1260 76 S 1400 58 1440 64 V120 H0 Z"/>'
         '<path fill="var(--bg)" d="M0 104 C 260 84 520 96 760 104 S 1180 116 1440 98 V120 H0 Z"/></svg>')


def tiles(word: str, start: int = 0, tilt: bool = True) -> str:
    out = []
    for i, ch in enumerate(word):
        r = ((i * 7) % 5 - 2) * 1.5 if tilt else 0
        out.append(f'<span class="tile" style="--t:{TILE[(start + i) % len(TILE)]};--r:{r:.1f}deg">{html.escape(ch)}</span>')
    return "".join(out)


def page(title: str, description: str, body: str, canonical: str, image: str = "images/wise-words-feature.jpg") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{SITE}{canonical}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:image" content="{SITE}{image}">
<meta property="og:url" content="{SITE}{canonical}">
<meta name="theme-color" content="#5ec8ff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0f1340" media="(prefers-color-scheme: dark)">
<link rel="icon" type="image/png" href="/images/wise-words-icon.png">
{FONTS}
<style>{STYLE}</style>
</head>
<body>
{body}
<footer><div class="wrap">
  <span>Wise Words is made by Sarath PS · © 2026</span>
  <span><a href="/privacy/">Privacy policy</a> · <a href="/terms/">Terms</a> · <a href="mailto:{EMAIL}">{EMAIL}</a></span>
</div></footer>
</body>
</html>
"""


def header() -> str:
    return """<header class="top"><div class="wrap">
  <a class="brand" href="/"><img src="/images/wise-words-icon.png" alt="" width="38" height="38">Wise Words</a>
  <nav aria-label="Site"><a href="/#how">How it plays</a><a href="/#languages">Languages</a><a href="/privacy/">Privacy</a><a href="/terms/">Terms</a></nav>
</div></header>"""


def clouds() -> str:
    return ('<div class="cloud" style="left:6%;top:120px"></div><div class="cloud" style="left:58%;top:70px;transform:scale(.8)"></div>'
            '<div class="cloud" style="left:80%;top:300px;transform:scale(.7)"></div>')


def phone(img: str, alt: str, tilt: float = 2.0) -> str:
    return (f'<div class="shot" style="--r:{tilt}deg"><div class="phone">'
            f'<img src="/images/{img}" alt="{html.escape(alt)}" width="540" height="960" loading="lazy"></div></div>')


def home() -> str:
    flags = [("en", "English"), ("de", "Deutsch"), ("fr", "Français"), ("es", "Español"), ("pt", "Português"), ("it", "Italiano"), ("nl", "Nederlands")]
    critters = ["Butterfly", "Crab", "Ladybug", "Snail", "Firefly"]
    body = f"""<div class="sky">
{clouds()}
{header()}
<div class="wrap hero">
  <div>
    <h1 class="logo" aria-label="Wise Words"><span class="line">{tiles("WISE")}</span><span class="line">{tiles("WORDS", 4)}</span></h1>
    <p class="tagline">A crossword that grows into the sky.</p>
    <p class="lede">Swipe letters to solve each ledge, watch the vine climb higher, and learn a new word with every swipe. For kids and grown-ups, in seven languages.</p>
    <div class="actions">
      <a class="play" href="{PLAY}">{PLAY_ICON}Get it on Google Play</a>
      <span class="soon">In testing now · coming soon to everyone</span>
    </div>
  </div>
  <div class="stage">
    <div class="phone"><img src="/images/play-climb.jpg" alt="A ledge of the Word Vine in Sunset Canyon, mid-swipe" width="540" height="960"></div>
    <img class="lexi" src="/images/lexi.png" alt="Lexi the owl" width="240" height="240">
  </div>
</div>
{HILLS}
</div>

<section id="how"><div class="wrap">
  <p class="eyebrow">How it plays</p>
  <h2>Swipe, climb, learn</h2>
  <div class="steps">
    <div class="step">{tiles("1", 0, False)}<h3>Swipe the letters</h3><p>Join letters on the wheel to spell the words hidden in the ledge. Find extra words for bonus coins.</p></div>
    <div class="step">{tiles("2", 3, False)}<h3>Grow the vine</h3><p>Solved words turn to stone and a new ledge sprouts above. No level screens, no timers, no losing.</p></div>
    <div class="step">{tiles("3", 5, False)}<h3>Learn the words</h3><p>Tap any word for its meaning. Every word you find goes into your own Word Book.</p></div>
  </div>
</div></section>

<section class="band"><div class="wrap">
  <div class="row">
    {phone("play-tiles.jpg", "Fog, a mystery tile, a snail and a bomb on a ledge", -2)}
    <div>
      <p class="eyebrow">A new surprise in every world</p>
      <h2>Eight kinds of special tiles</h2>
      <p>Ice freezes a word until its neighbour is solved. Bombs uncover letters. Mystery tiles change with every try. Fog, golden buds, lightning and moss join as you climb through five worlds, from Sunny Meadow to Starry Night.</p>
      <ul class="chips"><li>Ice</li><li>Bombs</li><li>Mystery tiles</li><li>Fog</li><li>Golden buds</li><li>Lightning</li><li>Moss</li><li>Critters</li></ul>
    </div>
  </div>
  <div class="row flip">
    {phone("play-daily.jpg", "The Daily Bloom calendar with a six-day streak", 2)}
    <div>
      <p class="eyebrow">Every day</p>
      <h2>A new puzzle each morning</h2>
      <p>The Daily Bloom is one extra puzzle a day, the same for everyone. Fill your calendar, keep your streak and win a new flower frame every month. Lexi has a little gift for you every day too.</p>
    </div>
  </div>
  <div class="row">
    {phone("play-word.jpg", "A treasure word's card: its meaning, similar words and story", -2)}
    <div>
      <p class="eyebrow">Learn as you play</p>
      <h2>Every word has a story</h2>
      <p>See what any solved word means, and hunt down 92 rare treasure words, each with a riddle, similar words and where the word comes from.</p>
    </div>
  </div>
</div></section>

<section><div class="wrap" style="text-align:center">
  <p class="eyebrow">From ledge 71</p>
  <h2>Catch all five critters</h2>
  <p style="color:var(--muted);max-width:34em;margin:10px auto 0">They hop around the vine with every try. Solve the word one sits on to catch it for your collection.</p>
  <div class="critters">{"".join(f'<figure><img src="/images/critter-{i}.png" alt="" width="92" height="92" loading="lazy">{n}</figure>' for i, n in enumerate(critters))}</div>
</div></section>

<section id="languages" class="band"><div class="wrap">
  <div class="row flip">
    {phone("play-languages.jpg", "Choosing the crossword language, with each language's ledge", 2)}
    <div>
      <p class="eyebrow">Seven languages</p>
      <h2>Crosswords in your language</h2>
      <p>Play in any of seven languages, each with its own climb, world ranking and word meanings. Switch any time with the flag on the home screen.</p>
      <div class="flags">{"".join(f'<div class="flag"><img src="/images/flag-{c}.png" alt="" width="44" height="30">{n}</div>' for c, n in flags)}</div>
    </div>
  </div>
</div></section>

<section><div class="wrap">
  <p class="eyebrow">Fair and friendly</p>
  <h2>Made to be calm</h2>
  <ul class="promises">
    <li style="--t:{TILE[3]}">No timers, no fail state, no pressure</li>
    <li style="--t:{TILE[0]}">No in-app purchases</li>
    <li style="--t:{TILE[2]}">No pop-up ads: optional reward videos only</li>
    <li style="--t:{TILE[4]}">Plays offline</li>
    <li style="--t:{TILE[5]}">A fair world ranking: everyone plays the same puzzles</li>
    <li style="--t:{TILE[1]}">Great for kids and grown-ups</li>
  </ul>
</div></section>

<section class="band finale"><div class="wrap">
  <img src="/images/lexi-calm.png" alt="" width="150" height="150" loading="lazy">
  <h2>Ready to start climbing?</h2>
  <div class="actions"><a class="play" href="{PLAY}">{PLAY_ICON}Get it on Google Play</a></div>
  <p class="note" style="color:var(--muted);margin-top:14px">Questions or a word meaning that looks wrong? Email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
</div></section>"""
    return page("Wise Words – a crossword that grows into the sky",
                "Wise Words: an endless crossword word puzzle for Android. Swipe letters, grow the vine and learn new words, in 7 languages.", body, "")


def link(text: str) -> str:
    t = html.escape(text)
    t = re.sub(r"(https?://[^\s)<]+[^\s).,<])", r'<a href="\1">\1</a>', t)
    t = re.sub(r"(?<![\w/>.])((?:creativecommons\.org|wiktionary\.org|kaikki\.org)(?:/[^\s),<]*[^\s).,<])?)", r'<a href="https://\1">\1</a>', t)
    return t.replace(EMAIL, f'<a href="mailto:{EMAIL}">{EMAIL}</a>')


def legal(path: str, canonical: str, title: str) -> str:
    lines = open(path, encoding="utf-8").read().splitlines()
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
        elif not s:
            flush()
        elif re.match(r"^\d+\.\s+[A-Z][A-Z ,'&-]+$", s):
            flush()
            num, name = s.split(" ", 1)
            out.append(f"<h2>{num} {html.escape(name.capitalize())}</h2>")
        elif s.startswith("- "):
            if para:
                flush()
            bullets.append(s[2:])
        else:
            if bullets:
                flush()
            para.append(s)
    flush()
    body = f"""<div class="sky legal-sky">
{header()}
<div class="wrap legal-head"><h1>{html.escape(title)}</h1><p>Wise Words · {html.escape(meta)}</p></div>
{HILLS}
</div>
<main class="wrap legal">
{chr(10).join(out)}
</main>"""
    return page(f"{title} – Wise Words", f"{title} for Wise Words, the crossword word puzzle game.", body, canonical)


def redirect(to: str) -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Wise Words</title>
<link rel="canonical" href="{SITE}{to.lstrip('/')}"><meta http-equiv="refresh" content="0; url={to}">
<meta name="robots" content="noindex"></head>
<body><p><a href="{to}">Wise Words</a></p></body></html>
"""


def write(rel: str, text: str) -> None:
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main() -> None:
    img = os.path.join(ROOT, "images")
    shutil.rmtree(img, ignore_errors=True)
    os.makedirs(img)
    shutil.copy(os.path.join(GAME, "store", "icon-512.png"), os.path.join(img, "wise-words-icon.png"))
    # The store's feature graphic is only used for link previews (og:image).
    subprocess.run(["magick", os.path.join(GAME, "store", "en-US", "feature-graphic.png"), "-quality", "86",
                    os.path.join(img, "wise-words-feature.jpg")], check=True)
    for src, dst in [("1_climb", "play-climb"), ("9_tiles", "play-tiles"), ("10_daily", "play-daily"),
                     ("3_treasure", "play-word"), ("11_languages", "play-languages")]:
        subprocess.run(["magick", os.path.join(GAME, "build", f"store_raw_{src}.png"), "-resize", "540x",
                        "-quality", "84", os.path.join(img, dst + ".jpg")], check=True)
    art = os.path.join(GAME, "build", "site")
    for name in ["lexi", "lexi-calm"]:
        subprocess.run(["magick", os.path.join(art, name + ".png"), "-resize", "300x", os.path.join(img, name + ".png")], check=True)
    for f in os.listdir(art):
        if f.startswith(("flag-", "critter-")):
            shutil.copy(os.path.join(art, f), os.path.join(img, f))

    write("index.html", home())
    write("privacy/index.html", legal(os.path.join(GAME, "store", "privacy-policy.txt"), "privacy/", "Privacy Policy"))
    write("terms/index.html", legal(os.path.join(GAME, "store", "terms-and-conditions.txt"), "terms/", "Terms and Conditions"))
    # Addresses already given out (Play Console, AdMob) keep working.
    write("wise-words/index.html", redirect("/"))
    # The policy addresses given to Google Play and AdMob show the page itself
    # (reviewers expect the policy at the address, not a forward).
    write("wise-words/privacy/index.html", legal(os.path.join(GAME, "store", "privacy-policy.txt"), "privacy/", "Privacy Policy"))
    write("wise-words/terms/index.html", legal(os.path.join(GAME, "store", "terms-and-conditions.txt"), "terms/", "Terms and Conditions"))
    write("app-ads.txt", "google.com, pub-7021910910381177, DIRECT, f08c47fec0942fa0\n")
    write(".nojekyll", "")
    write("404.html", page("Page not found – Wise Words", "Page not found.",
                           f'<div class="sky legal-sky">{header()}<div class="wrap legal-head"><h1>Page not found</h1>'
                           f'<p>Try <a href="/" style="color:inherit">the Wise Words home page</a>.</p></div>{HILLS}</div>', "404.html"))
    print("built", ROOT)


main()
