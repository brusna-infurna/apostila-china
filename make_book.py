#!/usr/bin/env python3
"""Gera, a partir de data/apostila.json (+ live.json), dois arquivos em exports/:
  - apostila-china-print.html  (para virar PDF via Chrome headless)
  - apostila-china.epub         (EPUB3, compatível com Kindle / Send to Kindle)
Fonte única de conteúdo = o mesmo JSON que alimenta o site."""
import json, html as _html, re, os, zipfile, pathlib

ROOT = pathlib.Path(__file__).parent
EXP = ROOT/'exports'; EXP.mkdir(exist_ok=True)
DATA = json.load(open(ROOT/'data/apostila.json', encoding='utf-8'))
LIVE = json.load(open(ROOT/'data/live.json', encoding='utf-8'))
META, SEC = DATA['meta'], DATA['sections']

CJK = re.compile('([㐀-鿿豈-﫿　-〿＀-￯]+)')
def esc(s): return _html.escape(s or '', quote=True)
def wrapcjk(s): return CJK.sub(r'<span class="zh">\1</span>', s)

def runs_html(runs, text):
    if not runs:
        return wrapcjk(esc(text))
    out = []
    for r in runs:
        t = wrapcjk(esc(r['t']))
        if r.get('b'): t = f'<strong>{t}</strong>'
        if r.get('i'): t = f'<em>{t}</em>'
        out.append(t)
    return ''.join(out)

def render_blocks(blocks):
    out, i = [], 0
    while i < len(blocks):
        b = blocks[i]
        if b['type'] == 'li':
            j = i; items = []
            while j < len(blocks) and blocks[j]['type'] == 'li':
                items.append(blocks[j]); j += 1
            out.append(render_list(items)); i = j; continue
        if b['type'] == 'h':
            lvl = min(max(b.get('level', 2), 2), 4)
            idattr = f' id="{esc(b["id"])}"' if b.get('id') else ''
            out.append(f'<h{lvl}{idattr}>{runs_html(b.get("runs"), b.get("text"))}</h{lvl}>')
        elif b['type'] == 'p':
            out.append(f'<p>{runs_html(b.get("runs"), b.get("text"))}</p>')
        elif b['type'] == 'table':
            out.append(render_table(b))
        i += 1
    return '\n'.join(out)

def render_list(items):
    out = ''; stack = []
    def opent(ind, ordered):
        nonlocal out
        out += '<ol>' if ordered else '<ul>'; stack.append((ind, ordered))
    def closet():
        nonlocal out
        ind, ordered = stack.pop(); out += '</ol>' if ordered else '</ul>'
    for b in items:
        ind = b.get('indent', 0); ordered = bool(b.get('ordered'))
        while stack and stack[-1][0] > ind: closet()
        if not stack or stack[-1][0] < ind: opent(ind, ordered)
        out += f'<li>{runs_html(b.get("runs"), b.get("text"))}</li>'
    while stack: closet()
    return out

def render_table(b):
    rows = b.get('rows') or []
    if not rows: return ''
    h = '<table><thead><tr>' + ''.join(f'<th>{wrapcjk(esc(c))}</th>' for c in rows[0]) + '</tr></thead><tbody>'
    for r in rows[1:]:
        h += '<tr>' + ''.join('<td>' + wrapcjk(esc(c)).replace('\n', '<br/>') + '</td>' for c in r) + '</tr>'
    return h + '</tbody></table>'

def section_inner(s):
    kicker = s.get('label') or ('Apêndice' if s['group'] == 'apendices' else '')
    head = f'<p class="kicker">{esc(kicker)}</p>' if kicker else ''
    return f'{head}<h1 class="chapter-title">{esc(s["title"])}</h1>\n{render_blocks(s["blocks"])}'

def live_inner():
    parts = ['<p class="kicker">Apêndice · Camada viva</p>',
             f'<h1 class="chapter-title">Atualidades</h1>',
             f'<p class="muted">{esc(LIVE["intro"])} (Atualizado em {esc(LIVE["updated"])}.)</p>']
    for cat in LIVE['categories']:
        parts.append(f'<h2>{esc(cat["title"])} <span class="zh">{esc(cat.get("zh",""))}</span></h2>')
        for it in cat['items']:
            src = it.get('source') or {}
            srcline = (f'<p class="src">Fonte: <a href="{esc(src.get("url",""))}">{esc(src.get("name",""))}</a></p>'
                       if src else '')
            parts.append(f'<h3>{esc(it["title"])}</h3><p>{wrapcjk(esc(it["text"]))}</p>{srcline}')
    return '\n'.join(parts)

# ---------------- PRINT HTML (for PDF) ----------------
PRINT_CSS = """
@page{size:A4;margin:20mm 18mm 18mm;}
*{box-sizing:border-box}
html{font-size:11.2pt}
body{font-family:'Iowan Old Style','Palatino Linotype',Palatino,'Book Antiqua',Georgia,serif;
 color:#20201d;line-height:1.5;margin:0;background:#fff;
 -webkit-print-color-adjust:exact;print-color-adjust:exact}
.zh{font-family:'PingFang SC','Hiragino Sans GB','Songti SC','Noto Sans CJK SC',serif}
h1.chapter-title{font-size:25pt;line-height:1.1;margin:0 0 .3em;font-weight:700;color:#1a1813}
.kicker{font-size:9pt;letter-spacing:.22em;text-transform:uppercase;color:#9c2b22;font-weight:700;margin:0 0 .4em;font-family:Helvetica,Arial,sans-serif}
h2{font-size:15pt;margin:1.4em 0 .4em;color:#9c2b22;font-weight:700;page-break-after:avoid}
h3{font-size:12.5pt;margin:1.1em 0 .3em;font-weight:700;page-break-after:avoid}
h4{font-size:10pt;margin:1em 0 .2em;text-transform:uppercase;letter-spacing:.08em;color:#555;font-family:Helvetica,Arial,sans-serif;page-break-after:avoid}
p{margin:0 0 .6em;text-align:justify}
strong{font-weight:700}
ul,ol{margin:.2em 0 .8em;padding-left:1.4em}
li{margin:0 0 .3em}
ul li::marker,ol li::marker{color:#9c2b22}
table{width:100%;border-collapse:collapse;margin:.8em 0;font-size:9.5pt;font-family:Helvetica,Arial,sans-serif;page-break-inside:avoid}
th{background:#9c2b22;color:#fff;text-align:left;padding:6px 8px;font-size:9pt}
td{padding:5px 8px;border-top:.5px solid #d8cfbb;vertical-align:top}
tbody tr:nth-child(even) td{background:#f6f2e9}
.src{font-size:9pt;color:#777;font-family:Helvetica,Arial,sans-serif}
.muted{color:#666;font-style:italic}
a{color:#9c2b22;text-decoration:none}
section.chapter{page-break-before:always}
section.cover{page-break-after:always;text-align:center;padding-top:55mm}
section.cover .cn{font-size:80pt;color:#9c2b22;font-family:'PingFang SC','Songti SC',serif;line-height:1;font-weight:700}
section.cover h1{font-size:34pt;letter-spacing:.34em;text-transform:uppercase;margin:.2em 0 0;padding-left:.34em}
section.cover .sub{font-style:italic;font-size:17pt;color:#555;margin:.2em 0}
section.cover .tag{font-family:Helvetica,Arial,sans-serif;font-size:10pt;color:#333;margin-top:.8em}
section.cover .ml{font-family:Helvetica,Arial,sans-serif;font-size:10pt;color:#666;margin-top:18mm;line-height:1.9}
section.toc{page-break-after:always}
section.toc h1{font-size:20pt;color:#1a1813;border-bottom:2px solid #9c2b22;padding-bottom:.2em}
.toc-item{display:flex;justify-content:space-between;padding:5px 0;border-bottom:.5px dotted #ccc;font-family:Helvetica,Arial,sans-serif;font-size:10.5pt}
.toc-item .lbl{color:#9c2b22;font-weight:700;margin-right:10px;min-width:78px;display:inline-block}
.toc-item a{color:#20201d}
"""

def build_print_html():
    cover = f"""<section class="cover">
      <div class="cn">{esc(META['zh'])}</div>
      <h1>China</h1>
      <div class="sub">{esc(META['subtitle'])}</div>
      <div class="tag">{esc(META['tagline'])}</div>
      <div class="ml">{esc(META['dates'])}<br/>{esc(META['route'])}<br/>{esc(META['version'])}<br/>{esc(META['prepared'])}</div>
    </section>"""
    toc_rows = []
    for s in SEC:
        toc_rows.append(f'<div class="toc-item"><span><span class="lbl">{esc(s.get("label") or "")}</span>'
                        f'<a href="#sec-{esc(s["id"])}">{esc(s["title"])}</a></span></div>')
    toc_rows.append('<div class="toc-item"><span><span class="lbl">Apêndice</span>'
                    '<a href="#sec-atualidades">Atualidades (camada viva)</a></span></div>')
    toc = f'<section class="toc"><h1>Sumário</h1>{"".join(toc_rows)}</section>'
    body = [cover, toc]
    for s in SEC:
        body.append(f'<section class="chapter" id="sec-{esc(s["id"])}">{section_inner(s)}</section>')
    body.append(f'<section class="chapter" id="sec-atualidades">{live_inner()}</section>')
    htmldoc = (f'<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"/>'
               f'<title>China — Apostila de Estudo</title><style>{PRINT_CSS}</style></head>'
               f'<body>{"".join(body)}</body></html>')
    out = EXP/'apostila-china-print.html'
    out.write_text(htmldoc, encoding='utf-8')
    print('print html ->', out)
    return out

# ---------------- EPUB ----------------
EPUB_CSS = """
body{font-family:Georgia,'Iowan Old Style',Palatino,serif;line-height:1.6;margin:0 5%}
.zh{font-family:'PingFang SC','Songti SC','Noto Sans CJK SC',sans-serif}
h1.chapter-title{font-size:1.7em;line-height:1.15;margin:.2em 0 .5em}
.kicker{font-size:.72em;letter-spacing:.18em;text-transform:uppercase;color:#9c2b22;font-weight:bold;margin:1em 0 .3em}
h2{color:#9c2b22;font-size:1.25em;margin:1.4em 0 .4em}
h3{font-size:1.08em;margin:1.1em 0 .3em}
h4{font-size:.85em;text-transform:uppercase;letter-spacing:.06em;color:#555;margin:1em 0 .2em}
p{margin:0 0 .7em;text-align:justify}
ul,ol{margin:.2em 0 .9em}
li{margin:0 0 .4em}
table{border-collapse:collapse;width:100%;font-size:.82em;margin:1em 0}
th{background:#9c2b22;color:#fff;text-align:left;padding:5px 7px}
td{padding:4px 7px;border-top:1px solid #ccc;vertical-align:top}
.src{font-size:.8em;color:#777}.muted{color:#666;font-style:italic}
a{color:#9c2b22}
.cover-t{text-align:center;margin-top:18%}
.cover-t .cn{font-size:4.2em;color:#9c2b22;font-family:'PingFang SC','Songti SC',serif}
.cover-t h1{font-size:2.4em;letter-spacing:.3em;text-transform:uppercase;margin:.2em 0;padding-left:.3em}
.cover-t .sub{font-style:italic;color:#555;font-size:1.2em}
.cover-t .ml{font-size:.85em;color:#666;margin-top:2em;line-height:1.9}
"""

def xhtml(title, body):
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<!DOCTYPE html>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="pt-BR" lang="pt-BR">\n'
            f'<head><meta charset="utf-8"/><title>{esc(title)}</title>'
            '<link rel="stylesheet" type="text/css" href="style.css"/></head>\n'
            f'<body>{body}</body></html>')

def build_epub():
    uid = 'urn:uuid:china-apostila-bruna-infurna-v1'
    files = {}  # path -> (bytes or str)
    files['mimetype'] = 'application/epub+zip'
    files['META-INF/container.xml'] = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
        '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>'
        '</rootfiles></container>')
    files['OEBPS/style.css'] = EPUB_CSS

    # cover
    cover_body = (f'<div class="cover-t"><div class="cn">{esc(META["zh"])}</div>'
                  f'<h1>China</h1><div class="sub">{esc(META["subtitle"])}</div>'
                  f'<div class="ml">{esc(META["tagline"])}<br/><br/>{esc(META["dates"])}<br/>'
                  f'{esc(META["route"])}<br/>{esc(META["version"])}<br/>{esc(META["prepared"])}</div></div>')
    files['OEBPS/cover.xhtml'] = xhtml('China — Apostila de Estudo', cover_body)

    spine = ['cover']
    manifest = ['<item id="css" href="style.css" media-type="text/css"/>',
                '<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>']
    navpoints = []; navlist = []
    order = 1

    def add_doc(fid, fname, title, body):
        nonlocal order
        files[f'OEBPS/{fname}'] = xhtml(title, body)
        manifest.append(f'<item id="{fid}" href="{fname}" media-type="application/xhtml+xml"/>')
        spine.append(fid)
        navpoints.append(f'<navPoint id="np{order}" playOrder="{order}"><navLabel><text>{esc(title)}</text></navLabel><content src="{fname}"/></navPoint>')
        navlist.append(f'<li><a href="{fname}">{esc(title)}</a></li>')
        order += 1

    for n, s in enumerate(SEC):
        title = (f'{s["label"]} — {s["title"]}' if s.get('label') else s['title'])
        add_doc(f'sec{n}', f'sec-{n}.xhtml', title, f'<p class="kicker">{esc(s.get("label") or "")}</p>'
                f'<h1 class="chapter-title">{esc(s["title"])}</h1>\n{render_blocks(s["blocks"])}')
    add_doc('atuais', 'atualidades.xhtml', 'Apêndice — Atualidades', live_inner())

    # nav.xhtml (EPUB3)
    nav_body = ('<nav epub:type="toc" id="toc" xmlns:epub="http://www.idpf.org/2007/ops">'
                f'<h1>Sumário</h1><ol>{"".join("<li>"+x[4:] if False else x for x in navlist)}</ol></nav>')
    nav_body = ('<nav epub:type="toc" id="toc" xmlns:epub="http://www.idpf.org/2007/ops">'
                f'<h2>Sumário</h2><ol>{"".join(navlist)}</ol></nav>')
    files['OEBPS/nav.xhtml'] = xhtml('Sumário', nav_body)
    manifest.append('<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')

    # toc.ncx (EPUB2 fallback)
    files['OEBPS/toc.ncx'] = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">'
        f'<head><meta name="dtb:uid" content="{uid}"/></head>'
        '<docTitle><text>China — Apostila de Estudo</text></docTitle>'
        f'<navMap>{"".join(navpoints)}</navMap></ncx>')
    manifest.append('<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>')

    spine_xml = ''.join('<itemref idref="%s"/>' % i for i in spine)
    opf = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">'
           '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
           f'<dc:identifier id="bookid">{uid}</dc:identifier>'
           '<dc:title>China — Apostila de Estudo</dc:title>'
           '<dc:creator>Bruna Infurna</dc:creator>'
           '<dc:language>pt-BR</dc:language>'
           f'<dc:date>{esc(LIVE["updated"])}</dc:date>'
           '<dc:description>Apostila de estudo sobre a China — cultura, história, economia, tech, geopolítica e sociedade.</dc:description>'
           '<meta property="dcterms:modified">2026-06-02T00:00:00Z</meta>'
           '</metadata>'
           f'<manifest>{"".join(manifest)}</manifest>'
           f'<spine toc="ncx">{spine_xml}</spine>'
           '</package>')
    files['OEBPS/content.opf'] = opf

    out = EXP/'apostila-china.epub'
    with zipfile.ZipFile(out, 'w') as z:
        # mimetype first, stored (uncompressed)
        z.writestr('mimetype', files.pop('mimetype'), compress_type=zipfile.ZIP_STORED)
        for path, content in files.items():
            data = content.encode('utf-8') if isinstance(content, str) else content
            z.writestr(path, data, compress_type=zipfile.ZIP_DEFLATED)
    print('epub ->', out, f'({out.stat().st_size/1024:.0f} KB)')
    return out

if __name__ == '__main__':
    build_print_html()
    build_epub()
