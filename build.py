"""Build README.md and the styled SVG images it shows.

GitHub strips <style> tags and style="" attributes from READMEs, so the CSS
lives inside SVG files instead: SVG + CSS for shapes and motion, and HTML + CSS
inside <foreignObject> wherever text has to wrap. GitHub renders those SVGs as
images, CSS animations included.

Edit the content below, then run:

    python build.py

Standard library only. Palette and fonts follow levsan13.github.io.
"""
import math
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
GH = "https://github.com/levsan13"

# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------

HERO = {
    "eyebrow": "2D materials and AI.",
    "name": "Sergio Levy",
    "handle": "@levsan13 · Brazil",
    "tagline": "Ph.D. candidate in condensed matter physics at UFC. I simulate wave "
               "packet dynamics in graphene and customize open-source language models.",
}

LINKS = [  # (file slug, label, url)
    ("website", "Website", "https://levsan13.github.io"),
    ("orcid", "ORCID", "https://orcid.org/0009-0004-2541-7934"),
    ("x", "X / @lvnsan13", "https://x.com/lvnsan13"),
    ("linktree", "Linktree", "https://linktr.ee/lvnsan13"),
]

ABOUT = [  # trusted HTML: <em> renders in amber
    "I'm a physicist from the Universidade Federal do Ceará (UFC): a bachelor's and a "
    "master's in Physics, and now a <em>Ph.D. candidate in Condensed Matter Physics</em>.",
    "My research is computational: C, C++ and Python simulations of <em>wave packet "
    "dynamics in graphene</em>, and retrieval-augmented language models for 2D materials.",
    "Since September 2025 I've been at FCPC, on the <em>Kunumi Lab UFC</em> project, "
    "customizing open-source large language models for process automation.",
    "I'm also finishing a technical degree in <em>Electrotechnics</em> at IFCE: "
    "microcontrollers, instrumentation, signal conditioning and industrial control.",
]

FACTS = [
    ("Doctorate", "Condensed Matter Physics, UFC"),
    ("Since 2025", "FCPC · Kunumi Lab UFC"),
    ("Technical", "Electrotechnics, IFCE (ongoing)"),
    ("Location", "Brazil"),
    ("Languages", "Portuguese · English"),
    ("ORCID", "0009-0004-2541-7934"),
]

RESEARCH = [
    {
        "slug": "llmatter2d", "repo": "LLMatter2D", "tag": "Paper · Zenodo · 2026",
        "desc": "A retrieval-augmented LLM for the analysis and discovery of two-dimensional "
                "materials: DFT, ARPES, tight-binding models and the 11 Archimedean lattices.",
        "lang": "Python", "extra": "DOI 10.5281/zenodo.23779294", "viz": "kagome",
        "doi": "10.5281/zenodo.23779294",
    },
    {
        "slug": "wave-packet", "repo": "Wave-Packet-propagation-curvature",
        "tag": "Graduation project",
        "desc": "Split-operator simulation of the time evolution of a Gaussian wave packet "
                "in monolayer graphene with a smooth, non-uniform out-of-plane deformation.",
        "lang": "C++", "extra": "Plots in Python", "viz": "packet",
    },
]

PROJECT_GROUPS = [
    ("AI and LLMs", [
        {"repo": "wabot_python", "tag": "WhatsApp × LLMs", "lang": "Python", "extra": "FastAPI",
         "desc": "FastAPI service linking the WhatsApp Cloud API to OpenAI, Anthropic and "
                 "Gemini: runtime provider switching, fallback, memory, voice notes, images and PDFs."},
        {"repo": "case-vicio-ia-classificacao", "tag": "Question classification",
         "lang": "Python", "extra": "No dependencies",
         "desc": "Decides, for each question, whether to publish it under a taxonomy topic, "
                 "send it to a teacher for review, or mark it off-taxonomy, with no LLM in the decision."},
    ]),
    ("Live streaming and community", [
        {"repo": "StreamDeck-Obs", "tag": "OBS · iPad", "lang": "Python", "extra": "ES5 page",
         "desc": "A Stream Deck for OBS that runs in an old iPad's browser. A dependency-free "
                 "Python server plus a single ES5 page."},
        {"repo": "holyrics-obs-label", "tag": "OBS · Holyrics", "lang": "Python",
         "extra": "Browser source",
         "desc": "Publishes only the lyric on air in Holyrics, styled on a transparent "
                 "background, ready to drop into OBS as a browser source."},
        {"repo": "python-ShareScreen", "tag": "Screen sharing", "lang": "Python",
         "extra": "One script",
         "desc": "Shares the whole screen or a single Windows window, with audio, to any "
                 "browser on the local network."},
        {"repo": "Sorteio-RifaDigital", "tag": "Raffle draw", "lang": "HTML", "extra": "No data stored",
         "desc": "Drawing page for a charity raffle: load the rifa.digital report and it picks "
                 "a winner at random, with fireworks and confetti."},
        {"repo": "IBVB-Campanha", "tag": "Pix donations", "lang": "HTML", "extra": "MySQL",
         "desc": "Mobile-first donation campaign on the Mercado Pago API. The total updates "
                 "as payments are confirmed."},
        {"repo": None, "tag": "Everything else", "desc": "", "lang": None},  # "all repositories" card
    ]),
]

STACK = [  # (name, dot color)
    ("Python", "#3572A5"), ("C", "#A8B9CC"), ("C++", "#F34B7D"), ("Jupyter", "#DA5B0B"),
    ("TensorFlow", "#FF6F00"), ("FastAPI", "#009688"), ("LLM APIs", "#8A7BF0"),
    ("HTML", "#E34C26"), ("JavaScript", "#F1E05A"), ("MySQL", "#4479A1"),
    ("OBS Studio", "#9AA0C6"),
]

FOOTER = "Built with SVG, CSS and a bit of numerical physics."

LANG_COLORS = {"Python": "#3572A5", "C++": "#F34B7D", "HTML": "#E34C26", "Jupyter Notebook": "#DA5B0B"}

# --------------------------------------------------------------------------
# Shared CSS
# --------------------------------------------------------------------------

W = 900   # every full-width image; half-width cards are W / 2
M = 5     # transparent margin around each panel, so rows line up

BASE_CSS = """
svg{--void:#0B0E24;--surface:#141935;--line:#2A3160;--amber:#F2B441;--violet:#8A7BF0;
  --text:#E6E7F2;--muted:#9AA0C6;--soft:#D3D6E8;
  --display:"Newsreader",Georgia,"Times New Roman",serif;
  --body:"IBM Plex Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
:where(.fo),:where(.fo) *{box-sizing:border-box;margin:0;padding:0}
.fo{width:100%;height:100%;font-family:var(--body);color:var(--text);-webkit-font-smoothing:antialiased}
em{font-style:normal;color:var(--amber)}
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
@keyframes scan{0%{transform:translateX(-120%)}55%,100%{transform:translateX(330%)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""

# Images without their own dark panel sit on GitHub's page colour.
ON_PAGE_CSS = """
@media (prefers-color-scheme:light){svg{--muted:#5B6190;--violet:#5D4ED6;--line:#C9CCE3;--amber:#B7791F}}
"""

CARD_CSS = """
.card{position:relative;height:100%;overflow:hidden;display:flex;flex-direction:column;
  border:1px solid var(--line);border-radius:16px;padding:22px 26px 20px 30px;
  background:radial-gradient(120% 140% at 100% 0%,rgba(138,123,240,.14),transparent 55%),
             linear-gradient(180deg,#171C3D,var(--surface))}
.card::before{content:"";position:absolute;left:0;top:0;width:34%;height:1px;
  background:linear-gradient(90deg,transparent,var(--amber),transparent);
  animation:scan 8s ease-in-out infinite}
.card::after{content:"";position:absolute;left:0;top:24px;width:3px;height:36px;
  border-radius:0 3px 3px 0;background:linear-gradient(var(--amber),var(--violet))}
.tag{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--violet)}
.title{font-family:var(--display);font-size:24px;line-height:1.25;margin-top:8px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.title b{font:500 15px var(--mono);color:var(--amber);margin-left:8px}
.desc{font-size:13.5px;line-height:1.6;color:var(--soft);margin-top:9px;
  display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:4;overflow:hidden}
.meta{margin-top:auto;padding-top:12px;display:flex;align-items:center;gap:16px;
  font-family:var(--mono);font-size:11.5px;letter-spacing:.03em;color:var(--muted)}
.meta i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;vertical-align:-1px}
"""


def svg(w, h, title, css, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">\n'
        f"<title>{escape(title)}</title>\n<style>{BASE_CSS}{css}</style>\n{body}\n</svg>\n"
    )


def html(x, y, w, h, inner):
    return (f'<foreignObject x="{x}" y="{y}" width="{w}" height="{h}">'
            f'<div xmlns="http://www.w3.org/1999/xhtml" class="fo">{inner}</div></foreignObject>')


def path_d(points):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)


def text_only(s):
    return re.sub(r"<[^>]+>", "", s)


def write(name, content):
    (ASSETS / name).write_text(content, encoding="utf-8")


# --------------------------------------------------------------------------
# Physics for the drawings
# --------------------------------------------------------------------------

def packet_frames(sigma, amp, k, frames, step=4.0):
    """Re and Im of a Gaussian packet, centred at 0, for one turn of the phase."""
    us = [-4 * sigma + i * step for i in range(int(8 * sigma / step) + 1)]
    env = [math.exp(-0.5 * (u / sigma) ** 2) for u in us]
    re_f, im_f = [], []
    for j in range(frames + 1):
        phi = 2 * math.pi * j / frames
        re_f.append(path_d([(u, -amp * e * math.cos(k * u - phi)) for u, e in zip(us, env)]))
        im_f.append(path_d([(u, -amp * e * math.sin(k * u - phi)) for u, e in zip(us, env)]))
    top = [(u, -amp * e) for u, e in zip(us, env)]
    bottom = [(u, amp * e) for u, e in zip(us, env)][::-1]
    envelope = path_d(top + bottom) + " Z"
    return envelope, re_f, im_f


def packet_svg(sigma, amp, k, frames=12, dur="1.2s", glow=True):
    envelope, re_f, im_f = packet_frames(sigma, amp, k, frames)
    cls = "re glow" if glow else "re"
    return (
        f'<path class="env" d="{envelope}"/>'
        f'<path class="im" d="{im_f[0]}"><animate attributeName="d" dur="{dur}" '
        f'repeatCount="indefinite" values="{";".join(im_f)}"/></path>'
        f'<path class="{cls}" d="{re_f[0]}"><animate attributeName="d" dur="{dur}" '
        f'repeatCount="indefinite" values="{";".join(re_f)}"/></path>'
    )


PACKET_CSS = """
.env{fill:url(#envfill)}
.re{fill:none;stroke:var(--amber);stroke-width:2;stroke-linejoin:round}
.im{fill:none;stroke:var(--violet);stroke-width:1.6;stroke-linejoin:round;opacity:.9}
.glow{filter:drop-shadow(0 0 5px rgba(242,180,65,.55))}
.grid{fill:none;stroke:var(--line);stroke-width:1}
"""

ENV_GRADIENT = (
    '<linearGradient id="envfill" x1="0" x2="1" y1="0" y2="0">'
    '<stop offset="0" stop-color="#8A7BF0" stop-opacity="0"/>'
    '<stop offset=".5" stop-color="#8A7BF0" stop-opacity=".22"/>'
    '<stop offset="1" stop-color="#8A7BF0" stop-opacity="0"/></linearGradient>'
)


def kagome_bands(n=60):
    """Nearest-neighbour kagome bands along Γ-M-K-Γ, in units of t (flat band at +2)."""
    d = [(0.5, 0.0), (0.25, math.sqrt(3) / 4), (-0.25, math.sqrt(3) / 4)]
    G, Mp, K = (0, 0), (0, 2 * math.pi / math.sqrt(3)), (2 * math.pi / 3, 2 * math.pi / math.sqrt(3))
    legs = [(G, Mp), (Mp, K), (K, G)]
    ks, s, nodes = [], 0.0, [0.0]
    for a, b in legs:
        length = math.dist(a, b)
        for i in range(n + (1 if (a, b) == legs[-1] else 0)):
            f = i / n
            ks.append((s + f * length, (a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1]))))
        s += length
        nodes.append(s)
    lower, upper = [], []
    for x, (kx, ky) in ks:
        c2 = sum(math.cos(kx * dx + ky * dy) ** 2 for dx, dy in d)
        r = math.sqrt(max(4 * c2 - 3, 0))
        lower.append((x, -1 - r))
        upper.append((x, -1 + r))
    return lower, upper, nodes, s


# --------------------------------------------------------------------------
# Images
# --------------------------------------------------------------------------

def header():
    H = 370
    def axis_y(x):
        t = x / W
        return H * 0.84 - math.sin(t * math.pi) * H * 0.06 - t * H * 0.04

    grid = []
    for i in range(-9, 3):
        grid.append(path_d([(x, axis_y(x) + i * H * 0.085) for x in range(0, W + 1, 12)]))
    for x in range(-40, W + 60, 64):
        grid.append(path_d([(x, axis_y(x) - H * 0.9), (x + 10, axis_y(x) + H * 0.3)]))
    motion = path_d([(x, axis_y(x)) for x in range(-260, W + 261, 20)])

    s = 13  # honeycomb bond length
    h = math.sqrt(3) * s
    hexagon = (f"M0,{h/2:.2f} L{s/2},0 L{1.5*s},0 L{2*s},{h/2:.2f} L{1.5*s},{h:.2f} "
               f"L{s/2},{h:.2f} Z M{2*s},{h/2:.2f} L{3*s},{h/2:.2f}")

    css = PACKET_CSS + """
.panel{fill:var(--void);stroke:var(--line)}
.hex{fill:none;stroke:var(--line);stroke-width:1}
.legend{font:11px var(--mono);fill:var(--muted);letter-spacing:.04em}
.hero{padding:0}
.eyebrow{font:italic 300 19px/1.4 var(--display);color:var(--amber);animation:rise .9s ease-out both}
h1{font:300 68px/1 var(--display);letter-spacing:-.02em;margin-top:14px;animation:rise .9s ease-out .12s both}
.handle{font:13px var(--mono);letter-spacing:.06em;color:var(--muted);margin-top:14px;animation:rise .9s ease-out .24s both}
.tagline{max-width:52ch;font-size:17px;line-height:1.55;margin-top:20px;
  text-shadow:0 0 14px var(--void),0 0 4px var(--void);animation:rise .9s ease-out .36s both}
"""
    hero = (
        '<div class="hero">'
        f'<p class="eyebrow">{escape(HERO["eyebrow"])}</p>'
        f'<h1>{escape(HERO["name"])}</h1>'
        f'<p class="handle">{escape(HERO["handle"])}</p>'
        f'<p class="tagline">{escape(HERO["tagline"])}</p></div>'
    )
    lx = W - 150
    body = f"""<defs>
<clipPath id="clip"><rect x="{M}" y="{M}" width="{W-2*M}" height="{H-2*M}" rx="18"/></clipPath>
<pattern id="honeycomb" width="{3*s}" height="{h:.2f}" patternUnits="userSpaceOnUse"><path class="hex" d="{hexagon}"/></pattern>
<radialGradient id="corner" cx="1" cy="0" r=".75"><stop offset="0" stop-color="#fff" stop-opacity=".5"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".15"/><stop offset=".6" stop-color="#fff" stop-opacity=".7"/><stop offset="1" stop-color="#fff" stop-opacity=".9"/></linearGradient>
<mask id="cornermask"><rect width="{W}" height="{H}" fill="url(#corner)"/></mask>
<mask id="gridmask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
{ENV_GRADIENT}
</defs>
<rect class="panel" x="{M+.5}" y="{M+.5}" width="{W-2*M-1}" height="{H-2*M-1}" rx="18"/>
<g clip-path="url(#clip)">
<rect width="{W}" height="{H}" fill="url(#honeycomb)" mask="url(#cornermask)"/>
<g mask="url(#gridmask)">{"".join(f'<path class="grid" d="{d}"/>' for d in grid)}</g>
<g><animateMotion dur="14s" repeatCount="indefinite" rotate="auto" path="{motion}"/>
<g><animateTransform attributeName="transform" type="scale" values="0.85 1.15;1.7 0.6" dur="14s" repeatCount="indefinite"/>
{packet_svg(sigma=44, amp=34, k=0.17)}
</g></g>
</g>
<g class="legend">
<line x1="{lx}" y1="42" x2="{lx+22}" y2="42" stroke="var(--amber)" stroke-width="2"/><text x="{lx+32}" y="46">Re ψ(x,t)</text>
<line x1="{lx}" y1="62" x2="{lx+22}" y2="62" stroke="var(--violet)" stroke-width="2"/><text x="{lx+32}" y="66">Im ψ(x,t)</text>
<rect x="{lx}" y="76" width="22" height="10" rx="2" fill="#8A7BF0" fill-opacity=".25"/><text x="{lx+32}" y="86">|ψ(x,t)|</text>
</g>
{html(44, 44, 640, 260, hero)}"""
    alt = f'{HERO["name"]}: {HERO["eyebrow"]} {HERO["tagline"]}'
    write("header.svg", svg(W, H, alt, css, body))
    return alt


def pill(slug, label):
    """Small rounded link button. textLength keeps the width exact whatever the mono font."""
    tw = round(7.4 * len(label))
    w, h = tw + 58, 36
    css = """
.pill{fill:var(--surface);stroke:var(--line)}
.lbl{font:12.5px var(--mono);fill:var(--muted);letter-spacing:.04em}
.arr{font:13px var(--mono);fill:var(--amber)}
"""
    body = (
        f'<rect class="pill" x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{(h-1)/2}"/>'
        f'<circle cx="17" cy="18" r="3.5" fill="var(--amber)"/>'
        f'<text class="lbl" x="29" y="22.5" textLength="{tw}" lengthAdjust="spacing">{escape(label)}</text>'
        f'<text class="arr" x="{w-15}" y="22.5" text-anchor="end">↗</text>'
    )
    write(f"link-{slug}.svg", svg(w, h, label, css, body))
    return w, h


def section(slug, number, label):
    H = 64
    css = ON_PAGE_CSS + """
.sec{height:100%;display:flex;align-items:flex-end;gap:14px;padding:0 6px 14px;
  font:12px var(--mono);letter-spacing:.18em;text-transform:uppercase}
.n{color:var(--amber)}
.t{color:var(--violet)}
.rule{flex:1;height:1px;margin-bottom:5px;background:linear-gradient(90deg,var(--line),transparent);
  transform-origin:left;animation:grow 1.4s ease-out both}
@keyframes grow{from{transform:scaleX(0)}to{transform:none}}
"""
    inner = (f'<div class="sec"><span class="n">{number:02d}</span>'
             f'<span class="t">{escape(label)}</span><i class="rule"></i></div>')
    write(f"section-{slug}.svg", svg(W, H, label, css, html(M, 0, W - 2 * M, H, inner)))


def about():
    H = 420
    css = CARD_CSS + """
.cols{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(0,1fr);gap:44px;height:100%}
.prose p{font-size:15px;line-height:1.65;color:var(--soft);margin-bottom:14px;animation:rise .8s ease-out both}
.prose p:nth-child(2){animation-delay:.1s}.prose p:nth-child(3){animation-delay:.2s}.prose p:nth-child(4){animation-delay:.3s}
.facts{list-style:none;align-self:center;border-top:1px solid var(--line)}
.facts li{display:flex;justify-content:space-between;gap:18px;padding:12px 0;
  border-bottom:1px solid var(--line);font:12.5px var(--mono)}
.k{color:var(--muted);letter-spacing:.04em}
.v{color:var(--text);text-align:right}
.facts li:last-child .v{color:var(--amber)}
"""
    prose = "".join(f"<p>{p}</p>" for p in ABOUT)
    facts = "".join(f'<li><span class="k">{escape(k)}</span><span class="v">{escape(v)}</span></li>'
                    for k, v in FACTS)
    inner = f'<div class="card" style="padding:28px 30px 16px 34px"><div class="cols"><div class="prose">{prose}</div><ul class="facts">{facts}</ul></div></div>'
    alt = " ".join(text_only(p) for p in ABOUT) + " " + "; ".join(f"{k}: {v}" for k, v in FACTS) + "."
    write("about.svg", svg(W, H, alt, css, html(M, M, W - 2 * M, H - 2 * M, inner)))
    return alt


def card_inner(item, delay):
    if item["repo"] is None:
        return (f'<div class="card all" style="--d:{delay}s">'
                f'<p class="tag">{escape(item["tag"])}</p>'
                '<p class="title">All repositories<b>→</b></p>'
                '<p class="desc">Forks, experiments and everything that did not fit on this page.</p>'
                '<p class="meta">github.com/levsan13?tab=repositories</p></div>')
    meta = ""
    if item.get("lang"):
        color = LANG_COLORS.get(item["lang"], "#9AA0C6")
        meta += f'<span><i style="background:{color}"></i>{escape(item["lang"])}</span>'
    if item.get("extra"):
        meta += f'<span>{escape(item["extra"])}</span>'
    return (f'<div class="card" style="--d:{delay}s">'
            f'<p class="tag">{escape(item["tag"])}</p>'
            f'<p class="title">{escape(item["repo"])}<b>↗</b></p>'
            f'<p class="desc">{escape(item["desc"])}</p>'
            f'<p class="meta">{meta}</p></div>')


DELAY_CSS = """
.card::before{animation-delay:var(--d)}
.card{animation:rise .8s ease-out both;animation-delay:calc(var(--d) / 8)}
.all{border-style:dashed;background:var(--void)}
.all::after{display:none}
"""


def project_card(item, index):
    w, h = W // 2, 214
    slug = (item["repo"] or "all-repositories").lower()
    inner = card_inner(item, round(index * 1.3 % 8, 1))
    alt = f'{item["repo"]}: {item["desc"]}' if item["repo"] else "All repositories"
    write(f"card-{slug}.svg", svg(w, h, alt, CARD_CSS + DELAY_CSS, html(M, M, w - 2 * M, h - 2 * M, inner)))
    return slug, alt


def research_card(item, index):
    H = 214
    vx, vy, vw, vh = W - M - 290, M + 24, 262, H - 2 * M - 48  # drawing box
    css = CARD_CSS + DELAY_CSS + PACKET_CSS + """
.card{padding-right:320px}
.frame{fill:rgba(11,14,36,.55);stroke:var(--line)}
.axis{font:10px var(--mono);fill:var(--muted);letter-spacing:.04em}
.guide{stroke:var(--line);stroke-width:1}
.band{fill:none;stroke-width:2;stroke-linecap:round;stroke-dasharray:1;animation:draw 2.4s ease-out .4s both}
.flat{stroke:var(--amber);filter:drop-shadow(0 0 4px rgba(242,180,65,.5))}
.disp{stroke:var(--violet)}
"""
    viz = f'<rect class="frame" x="{vx}" y="{vy}" width="{vw}" height="{vh}" rx="10"/>'
    if item["viz"] == "kagome":
        lower, upper, nodes, total = kagome_bands()
        px0, px1, py0, py1 = vx + 34, vx + vw - 14, vy + 22, vy + vh - 26
        emin, emax = -4.4, 2.7
        def xy(points):
            return [(px0 + x / total * (px1 - px0), py0 + (emax - e) / (emax - emin) * (py1 - py0))
                    for x, e in points]
        for x, name in zip(nodes, "ΓMKΓ"):
            gx = px0 + x / total * (px1 - px0)
            viz += f'<line class="guide" x1="{gx:.1f}" y1="{py0}" x2="{gx:.1f}" y2="{py1}"/>'
            viz += f'<text class="axis" x="{gx:.1f}" y="{py1 + 15}" text-anchor="middle">{name}</text>'
        for e in (2, 0, -2, -4):
            ey = py0 + (emax - e) / (emax - emin) * (py1 - py0)
            viz += f'<text class="axis" x="{px0 - 8}" y="{ey + 3.5:.1f}" text-anchor="end">{e}</text>'
        viz += f'<text class="axis" x="{px1}" y="{vy + 14}" text-anchor="end">kagome · E/t</text>'
        viz += f'<path class="band disp" pathLength="1" d="{path_d(xy(lower))}"/>'
        viz += f'<path class="band disp" pathLength="1" d="{path_d(xy(upper))}"/>'
        viz += (f'<path class="band flat" pathLength="1" '
                f'd="{path_d(xy([(0, 2), (total, 2)]))}"/>')
    else:
        cx, cy = vx + vw / 2, vy + vh / 2 + 8
        clip = f'<clipPath id="vclip"><rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" rx="10"/></clipPath>'
        lines = []
        for i in range(-4, 5):
            lines.append(path_d([(x, cy + i * 16 - math.sin((x - vx) / vw * math.pi) * 14)
                                 for x in range(int(vx), int(vx + vw) + 1, 6)]))
        for x in range(int(vx) + 8, int(vx + vw), 22):
            lines.append(path_d([(x, vy), (x + 6, vy + vh)]))
        bend = math.sin(0.5 * math.pi) * 14
        grid = "".join(f'<path class="grid" d="{d}"/>' for d in lines)
        viz = (f'<defs>{clip}{ENV_GRADIENT}</defs>' + viz +
               f'<g clip-path="url(#vclip)" opacity=".7">{grid}</g>'
               f'<g transform="translate({cx:.1f},{cy - bend:.1f})">{packet_svg(sigma=26, amp=34, k=0.33, frames=12, dur="1.1s")}</g>'
               f'<text class="axis" x="{vx + vw - 12}" y="{vy + 16}" text-anchor="end">graphene · split-operator</text>')
    inner = card_inner(item, round(index * 2.7, 1))
    alt = f'{item["repo"]}: {item["desc"]}'
    body = html(M, M, W - 2 * M, H - 2 * M, inner) + viz
    write(f'card-{item["slug"]}.svg', svg(W, H, alt, css, body))
    return alt


def stack():
    H = 134
    css = """
.panel{height:100%;display:flex;flex-wrap:wrap;align-content:center;gap:10px;padding:20px 24px;
  border:1px solid var(--line);border-radius:16px;background:linear-gradient(180deg,#171C3D,var(--surface))}
.chip{display:inline-flex;align-items:center;gap:8px;padding:7px 14px;border:1px solid var(--line);
  border-radius:999px;background:rgba(11,14,36,.55);font:12.5px var(--mono);letter-spacing:.03em;
  color:var(--soft);animation:rise .6s ease-out both}
.chip i{width:8px;height:8px;border-radius:50%}
"""
    chips = "".join(f'<span class="chip" style="animation-delay:{i * 0.05:.2f}s">'
                    f'<i style="background:{c}"></i>{escape(n)}</span>' for i, (n, c) in enumerate(STACK))
    alt = "Tools I use: " + ", ".join(n for n, _ in STACK) + "."
    write("stack.svg", svg(W, H, alt, css, html(M, M, W - 2 * M, H - 2 * M, f'<div class="panel">{chips}</div>')))
    return alt


def footer():
    H = 84
    wave = path_d([(x, 26 - 7 * math.exp(-((x - W / 2) / 120) ** 2) * math.cos((x - W / 2) * 0.09))
                   for x in range(M + 40, W - M - 39, 3)])
    css = ON_PAGE_CSS + """
.w{fill:none;stroke:var(--violet);stroke-width:1.4;stroke-dasharray:5 7;opacity:.8;animation:flow 3s linear infinite}
@keyframes flow{to{stroke-dashoffset:-48}}
.f{font:11.5px var(--mono);fill:var(--muted);letter-spacing:.06em}
"""
    body = (f'<path class="w" d="{wave}"/>'
            f'<text class="f" x="{W/2}" y="66" text-anchor="middle">{escape(FOOTER)}</text>')
    write("footer.svg", svg(W, H, FOOTER, css, body))


# --------------------------------------------------------------------------
# README
# --------------------------------------------------------------------------

def readme():
    ASSETS.mkdir(exist_ok=True)
    for old in ASSETS.glob("*.svg"):
        old.unlink()

    out = ["<!-- Generated by build.py: edit the content there, then run `python build.py`. -->", ""]
    out += ['<p align="center">', f'  <img src="assets/header.svg" width="100%" alt="{escape(header())}">', "</p>", ""]

    out.append('<p align="center">')
    for slug, label, url in LINKS:
        w, h = pill(slug, label)
        out.append(f'  <a href="{url}"><img src="assets/link-{slug}.svg" height="{h}" alt="{escape(label)}"></a>')
    out += ["</p>", ""]

    n = 1
    section("about", n, "About")
    out += [f'<img src="assets/section-about.svg" width="100%" alt="About">',
            f'<img src="assets/about.svg" width="100%" alt="{escape(about())}">', ""]

    n += 1
    section("research", n, "Research")
    out.append('<img src="assets/section-research.svg" width="100%" alt="Research">')
    for i, item in enumerate(RESEARCH):
        alt = research_card(item, i)
        out.append(f'<a href="{GH}/{item["repo"]}"><img src="assets/card-{item["slug"]}.svg" '
                   f'width="100%" alt="{escape(alt)}"></a>')
        if item.get("doi"):
            w, h = pill("doi", f'Read the paper · DOI {item["doi"]}')
            out += ['<p align="right">',
                    f'  <a href="https://doi.org/{item["doi"]}"><img src="assets/link-doi.svg" '
                    f'height="{h}" alt="{escape(item["repo"])} paper, DOI {item["doi"]}"></a>', "</p>", ""]
    out.append("")

    for group, items in PROJECT_GROUPS:
        n += 1
        slug = re.sub(r"[^a-z0-9]+", "-", group.lower()).strip("-")
        section(slug, n, group)
        out.append(f'<img src="assets/section-{slug}.svg" width="100%" alt="{escape(group)}">')
        # One paragraph per group: the half-width cards wrap two to a line.
        cells = []
        for i, item in enumerate(items):
            cslug, alt = project_card(item, i + n)
            href = f"{GH}/{item['repo']}" if item["repo"] else f"{GH}?tab=repositories"
            cells.append(f'<a href="{href}"><img src="assets/card-{cslug}.svg" width="50%" alt="{escape(alt)}"></a>')
        out += ['<p align="center">' + "".join(cells) + "</p>", ""]

    n += 1
    section("tools", n, "Tools I use")
    out += ['<img src="assets/section-tools.svg" width="100%" alt="Tools I use">',
            f'<img src="assets/stack.svg" width="100%" alt="{escape(stack())}">', ""]

    footer()
    out += [f'<img src="assets/footer.svg" width="100%" alt="{escape(FOOTER)}">', ""]
    (ROOT / "README.md").write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    readme()
    print(f"README.md + {len(list(ASSETS.glob('*.svg')))} SVGs written")
