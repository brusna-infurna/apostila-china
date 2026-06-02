#!/usr/bin/env python3
"""Builds a self-contained index.html by injecting the JSON data into template.html.
Run again any time you update data/apostila.json or data/live.json."""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).parent
tpl = (ROOT/'template.html').read_text(encoding='utf-8')
apostila = (ROOT/'data/apostila.json').read_text(encoding='utf-8')
live = (ROOT/'data/live.json').read_text(encoding='utf-8')

# guard: ensure no </script> sequence breaks the inline JSON
def safe(s): return s.replace('</', '<\\/')
html = tpl.replace('__APOSTILA__', safe(apostila)).replace('__LIVE__', safe(live))
out = ROOT/'index.html'
out.write_text(html, encoding='utf-8')
print(f'Built {out}  ({len(html)/1024:.0f} KB)')
