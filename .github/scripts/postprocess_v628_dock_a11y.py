#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "candidate/v628/assets/app.v628.js"

MARKER = "/* V6.28 · estado semántico del dock móvil */"
BLOCK = r'''
/* V6.28 · estado semántico del dock móvil */
;document.addEventListener('DOMContentLoaded',()=>{
  const dock=document.querySelector('.device-dock');
  if(!dock)return;
  const page=(document.body.dataset.page||'').trim();
  const current={home:'home',iri:'iri',contact:'contact'}[page]||'';
  dock.querySelectorAll('[data-dock]').forEach(link=>{
    if(current&&link.dataset.dock===current)link.setAttribute('aria-current','page');
    else link.removeAttribute('aria-current');
  });
});
'''

if not APP.is_file():
    raise SystemExit(f"No existe {APP}")

source = APP.read_text("utf-8")
if MARKER in source:
    raise SystemExit("El postprocesado del dock ya estaba presente antes de aplicarlo")
if "data-dock=\"home\"" not in source or "data-dock=\"iri\"" not in source or "data-dock=\"contact\"" not in source:
    raise SystemExit("No se encontró la estructura esperada del dock móvil")

APP.write_text(source.rstrip() + "\n" + BLOCK.lstrip(), encoding="utf-8")

result = APP.read_text("utf-8")
required = [MARKER, "aria-current','page", "{home:'home',iri:'iri',contact:'contact'}"]
missing = [token for token in required if token not in result]
if missing:
    raise SystemExit("Postprocesado incompleto: " + ", ".join(missing))

print("Dock móvil: estado aria-current reproducible añadido.")
