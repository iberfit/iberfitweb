from pathlib import Path
import re

root = Path('candidate/v628')
es = root / 'entrenador-personal-la-reina' / 'index.html'
en = root / 'en' / 'personal-trainer-la-reina' / 'index.html'

for p in (es, en):
    assert p.exists(), p

es_text = es.read_text()
en_text = en.read_text()

assert (root / 'VERSION').read_text().strip() == '6.43.16'
assert 'La escala residencial y los espacios verdes de La Reina' in es_text
assert 'Si ya caminas, pedaleas o haces actividad al aire libre' in es_text
assert 'class="grid cards-4"' in es_text
assert "La Reina’s residential scale and green spaces" in en_text
assert 'If walking, cycling or outdoor activity is already part of your week' in en_text
assert 'class="grid cards-4"' in en_text

es_text = es_text.replace('Entrenamiento personal en La Reina: domicilio, gimnasio de edificio, parque o zona verde, o formato híbrido según sector, entorno y horarios.','Entrenamiento personal en La Reina con cobertura presencial según sector, horario y espacio disponible, y opción híbrida u online cuando encaja mejor.')
es_text = es_text.replace('Entrenamiento personal en La Reina con diagnóstico, planificación y seguimiento, en domicilio, gimnasio de edificio o parque/zona verde según cobertura.','Entrenamiento personal en La Reina con diagnóstico, planificación y seguimiento, sujeto a cobertura, horario y espacio real de entrenamiento.')
en_text = en_text.replace('Personal training in La Reina with assessment, individual planning and ongoing review at home, in condominium gyms or suitable parks and green spaces.','Personal training in La Reina with assessment, individual planning and ongoing review, subject to area, schedule and a suitable training space.')

es_text = es_text.replace('<h1>Entrenar cerca, con continuidad y sin complicarlo de más.</h1><p class="lead">La escala residencial y los espacios verdes de La Reina permiten pensar el entrenamiento cerca de tu vida cotidiana. Nuestro trabajo es darle estructura.</p><p class="hero-support">Domicilio, espacio acordado o modalidad híbrida: elegimos contigo la forma que puedas repetir sin perder seguimiento.</p>','<h1>Primero confirmamos si podemos acompañarte bien en La Reina.</h1><p class="lead">Antes de recomendar presencial, revisamos tu sector, tus horarios y el espacio real donde entrenarías.</p><p class="hero-support">Si la cobertura y la frecuencia tienen sentido, definimos contigo la forma de trabajo. Si no, te proponemos híbrido u online con la misma claridad.</p>')
en_text = en_text.replace('<h1>Train close to everyday life, with enough structure to keep it going.</h1><p class="lead">La Reina’s residential scale and green spaces make it possible to think about training close to home. Our job is to give that convenience a clear structure.</p><p class="hero-support">Home, an agreed training space or hybrid support: we choose the option that is repeatable without losing review.</p>','<h1>First we confirm whether we can support you well in La Reina.</h1><p class="lead">Before recommending in-person training, we check your area, your schedule and the real space where you would train.</p><p class="hero-support">If coverage and frequency make sense, we define the format with you. If not, we will recommend hybrid or online support just as clearly.</p>')

old_es_strip = re.search(r'<div class="local-service-strip" aria-label="Opciones de entrenamiento en La Reina">.*?</div></div></div></section>', es_text, re.S)
assert old_es_strip
new_es_strip = '<div class="local-service-strip" aria-label="Qué confirmamos para el entrenamiento en La Reina"><div class="local-service-chip"><b>01</b><span><strong>Cobertura real</strong><br>Confirmamos sector y desplazamiento antes de cerrar una frecuencia.</span></div><div class="local-service-chip"><b>02</b><span><strong>Espacio útil</strong><br>Domicilio, gimnasio de edificio o exterior solo si permiten entrenar con calidad.</span></div><div class="local-service-chip"><b>03</b><span><strong>Horario sostenible</strong><br>La frecuencia tiene que encajar de verdad en tu semana.</span></div><div class="local-service-chip"><b>04</b><span><strong>Continuidad</strong><br>Si el presencial no basta, el híbrido conecta supervisión y trabajo guiado.</span></div></div></div></div></section>'
es_text = es_text[:old_es_strip.start()] + new_es_strip + es_text[old_es_strip.end():]

old_en_strip = re.search(r'<div class="local-service-strip" aria-label="Training options in La Reina">.*?</div></div></div></section>', en_text, re.S)
assert old_en_strip
new_en_strip = '<div class="local-service-strip" aria-label="What we confirm for personal training in La Reina"><div class="local-service-chip"><b>01</b><span><strong>Real coverage</strong><br>We confirm area and travel before agreeing a frequency.</span></div><div class="local-service-chip"><b>02</b><span><strong>Usable space</strong><br>Home, condominium gym or outdoors only when the setting supports good training.</span></div><div class="local-service-chip"><b>03</b><span><strong>Sustainable schedule</strong><br>The frequency has to fit your real week.</span></div><div class="local-service-chip"><b>04</b><span><strong>Continuity</strong><br>If in-person alone is not enough, hybrid connects supervision and guided work.</span></div></div></div></div></section>'
en_text = en_text[:old_en_strip.start()] + new_en_strip + en_text[old_en_strip.end():]

es_block = re.search(r'</section><section class="section"><div class="container"><div class="section-head reveal"><div class="kicker">Entrenar aquí</div>.*?</section><section class="section compact-section">', es_text, re.S)
assert es_block
new_es_block = '</section><section class="section"><div class="container"><div class="section-head reveal"><div class="kicker">Antes de recomendar presencial</div><h2>La decisión depende de tres cosas concretas.</h2><p class="lead">No damos por hecha la cobertura solo porque estés en La Reina. Primero comprobamos que podamos prestar el servicio con continuidad y calidad.</p></div><div class="principle-stack"><article class="principle-row reveal"><h3>Cobertura que podamos cumplir</h3><p>Sector, acceso y desplazamiento tienen que permitir una frecuencia realista.</p></article><article class="principle-row reveal"><h3>Un espacio donde se pueda entrenar bien</h3><p>Revisamos el lugar y el material disponible antes de decidir qué formato tiene sentido.</p></article><article class="principle-row reveal"><h3>Una frecuencia que puedas sostener</h3><p>Si el presencial añade demasiada fricción, el híbrido u online pueden dar más continuidad sin perder seguimiento.</p></article></div></div></section><section class="section compact-section">'
es_text = es_text[:es_block.start()] + new_es_block + es_text[es_block.end():]

en_block = re.search(r'</section><section class="section"><div class="container"><div class="section-head reveal"><div class="kicker">Training here</div>.*?</section><section class="section compact-section">', en_text, re.S)
assert en_block
new_en_block = '</section><section class="section"><div class="container"><div class="section-head reveal"><div class="kicker">Before recommending in-person training</div><h2>The decision depends on three concrete things.</h2><p class="lead">We do not assume coverage simply because you are in La Reina. We first check that the service can be delivered with continuity and quality.</p></div><div class="principle-stack"><article class="principle-row reveal"><h3>Coverage we can actually deliver</h3><p>Area, access and travel need to support a realistic training frequency.</p></article><article class="principle-row reveal"><h3>A space where training can be done well</h3><p>We review the setting and available equipment before deciding which format makes sense.</p></article><article class="principle-row reveal"><h3>A frequency you can sustain</h3><p>If in-person adds too much friction, hybrid or online support may provide better continuity without losing follow-up.</p></article></div></div></section><section class="section compact-section">'
en_text = en_text[:en_block.start()] + new_en_block + en_text[en_block.end():]

es_text = es_text.replace('<a class="text-link" href="/online/">Conocer entrenamiento online</a>', '<a class="text-link" href="/hibrido/">Conocer entrenamiento híbrido</a>')
en_text = en_text.replace('<a class="text-link" href="/en/online/">Explore online training</a>', '<a class="text-link" href="/en/hybrid/">Explore hybrid training</a>')

for forbidden in ('escala residencial','espacios verdes','caminas, pedaleas','cards-4','Tu objetivo</h3>','Tu autonomía</h3>','Antes de reservar'):
    assert forbidden not in es_text, forbidden
for forbidden in ('residential scale','green spaces','walking, cycling','cards-4','Your goal</h3>','Your autonomy</h3>','Before booking'):
    assert forbidden not in en_text, forbidden
for required in ('Cobertura real','Espacio útil','Horario sostenible','Cobertura que podamos cumplir','Una frecuencia que puedas sostener'):
    assert required in es_text, required
for required in ('Real coverage','Usable space','Sustainable schedule','Coverage we can actually deliver','A frequency you can sustain'):
    assert required in en_text, required

es.write_text(es_text)
en.write_text(en_text)
(root / 'VERSION').write_text('6.43.17\n')
changelog = root / 'CHANGELOG.md'
old = changelog.read_text()
entry = '## 6.43.17 — La Reina: operational local fit\n\n- Removes decorative territorial assumptions from the La Reina local landing.\n- Grounds the page in real coverage, usable training space, schedule and sustainable frequency.\n- Replaces the old Objective/Autonomy/Follow-up card template with a shorter operational decision block.\n- Fixes the hybrid recommendation link so its label and destination match.\n- Spanish and English updated consistently; SEO architecture, AEO answers and contextual WhatsApp intent are preserved.\n\n'
changelog.write_text(entry + old)
print('Built V6.43.17 La Reina operational landing')
