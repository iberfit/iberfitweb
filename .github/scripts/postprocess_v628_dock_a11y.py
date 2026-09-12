#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import quote
import re

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "candidate/v628/assets/app.v628.js"
CONTACT_ES = ROOT / "candidate/v628/contacto/index.html"
CONTACT_EN = ROOT / "candidate/v628/en/contact/index.html"

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

PHONE = "56944040032"
GENERAL_MESSAGES = {
    CONTACT_ES: (
        "Hola IBERFIT, quiero recibir orientación sobre entrenamiento y saber qué opción puede encajar mejor conmigo.",
        ("Escribir a IBERFIT", "Prefiero escribir directamente"),
    ),
    CONTACT_EN: (
        "Hello IBERFIT, I would like guidance about training and which option might fit me best.",
        ("Message IBERFIT", "I would rather write directly"),
    ),
}

GUIDE_PREFIXES = (
    (
        "Hola IBERFIT, quiero recibir orientación inicial sobre el Diagnóstico IRI.",
        "Hola IBERFIT, completé el orientador y quiero saber qué opción de entrenamiento puede encajar mejor conmigo.",
    ),
    (
        "Hello IBERFIT, I would like initial guidance about the IRI Assessment.",
        "Hello IBERFIT, I completed the guide and would like to know which training option might fit me best.",
    ),
)


def general_whatsapp(message: str) -> str:
    return f"https://wa.me/{PHONE}?text={quote(message, safe='')}"


def replace_contact_links(path: Path, message: str, labels: tuple[str, ...]) -> int:
    if not path.is_file():
        raise SystemExit(f"No existe {path}")
    html = path.read_text("utf-8")
    target = general_whatsapp(message)
    total = 0
    for label in labels:
        pattern = re.compile(
            rf'(<a\b[^>]*\bhref=")https://wa\.me/{PHONE}\?text=[^"]+("[^>]*>{re.escape(label)}</a>)'
        )
        html, count = pattern.subn(rf'\1{target}\2', html)
        total += count
    path.write_text(html, encoding="utf-8")
    return total


if not APP.is_file():
    raise SystemExit(f"No existe {APP}")

source = APP.read_text("utf-8")
if MARKER in source:
    raise SystemExit("El postprocesado del dock ya estaba presente antes de aplicarlo")
if "data-dock=\"home\"" not in source or "data-dock=\"iri\"" not in source or "data-dock=\"contact\"" not in source:
    raise SystemExit("No se encontró la estructura esperada del dock móvil")

for old, new in GUIDE_PREFIXES:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"El prefijo dinámico del orientador debía aparecer una vez y apareció {count}: {old}")
    source = source.replace(old, new, 1)

APP.write_text(source.rstrip() + "\n" + BLOCK.lstrip(), encoding="utf-8")

result = APP.read_text("utf-8")
required = [
    MARKER,
    "aria-current','page",
    "{home:'home',iri:'iri',contact:'contact'}",
    GUIDE_PREFIXES[0][1],
    GUIDE_PREFIXES[1][1],
]
missing = [token for token in required if token not in result]
if missing:
    raise SystemExit("Postprocesado incompleto: " + ", ".join(missing))
for old, _ in GUIDE_PREFIXES:
    if old in result:
        raise SystemExit(f"Persistió un prefijo antiguo del orientador: {old}")

for path, (message, labels) in GENERAL_MESSAGES.items():
    changed = replace_contact_links(path, message, labels)
    # Dos enlaces con el CTA principal y uno de escritura directa: tres por idioma.
    if changed != 3:
        raise SystemExit(f"{path}: se esperaban 3 enlaces generales de WhatsApp y se modificaron {changed}")
    html = path.read_text("utf-8")
    target = general_whatsapp(message)
    for label in labels:
        if f'>{label}</a>' not in html:
            raise SystemExit(f"{path}: falta el CTA esperado {label}")
    if html.count(target) != 3:
        raise SystemExit(f"{path}: el mensaje general no quedó exactamente en tres CTA")

print("Dock móvil: aria-current añadido. Contacto y orientador: intención de WhatsApp alineada en ES/EN.")
