# Cambios V6.39

- Se integra AEO (Answer Engine Optimization) sobre contenido visible, no mediante texto oculto ni páginas duplicadas.
- Se añaden respuestas directas y autocontenidas en Home, IRI, Método, modalidades, Sobre IBERFIT y las 14 páginas locales ES/EN.
- Se refuerza la distinción IRI inicial vs seguimiento posterior, la lógica de ajuste y la definición de cada modalidad.
- Se normaliza la entidad estructurada de IBERFIT de LocalBusiness sin dirección publicada a Organization + Service + areaServed, evitando declarar una dirección inexistente.
- Se añade dateModified coherente con la revisión real y se mantiene el contenido estructurado alineado con el texto visible.
- robots.txt permite explícitamente OAI-SearchBot y ChatGPT-User, además del acceso general existente.
- llms.txt incorpora respuestas directas y declara las páginas HTML canónicas como fuente de verdad.
- No se añade FAQPage artificial ni marcado especial para IA: se prioriza contenido útil, rastreable y citable.

# Cambios V6.38

- Release guiada por datos reales de Google Search Console, sin reescribir la Home que ya muestra señales orgánicas saludables.
- Las Condes se refuerza como landing local prioritaria: title y metadatos alineados con la consulta real “personal trainer Las Condes”, manteniendo el cuerpo editorial en español.
- Se añade una capa de evidencia de servicio en Las Condes: Diagnóstico IRI, plan individual, registro útil y seguimiento.
- Structured data de Las Condes incorpora `alternateName` para conectar “personal trainer” con el servicio canónico de entrenamiento personal.
- `llms.txt` explicita las URLs locales canónicas para mejorar descubrimiento semántico y GEO sin crear nuevas páginas.
- Sitemap actualiza `lastmod` únicamente para Las Condes, la URL materialmente modificada.
- Se preservan V6.37, la semántica principal de Home, Online canónico, historia institucional y toda la capa de interacción/accesibilidad certificada.

# Cambios V6.37

- Se introduce un quality floor de interacción inspirado en principios de UI/UX Pro Max, adaptado a la identidad IBERFIT y sin copiar ningún sistema externo.
- Focus visible unificado para enlaces, botones y controles; objetivos táctiles mínimos de 44 px y formularios de 48 px.
- Botones con estados hover/pressed claros y sin elevaciones decorativas; el verde y el dorado pasan a tratamientos sólidos y más sobrios.
- Se eliminan lifts, escalados y profundidad 3D de cards, fotografías y superficies donde no aportaban significado.
- Reduced motion endurecido globalmente y movimiento limitado a feedback de causa/efecto.
- Inputs y choice chips quedan protegidos frente a zoom involuntario y problemas táctiles en móvil.
- Safe areas, scroll-margin y dock móvil reforzados.
- Se refina el lenguaje público de las escenas de evidencia para describir proceso y material, no decisiones internas de implementación.
- Se conserva la arquitectura V6.36: IRI, evidencia visual, Online canónico, páginas locales diferenciadas y marca no personalista.

# Cambios V6.36

- “Online” pasa a ser la nomenclatura canónica visible y semántica del servicio remoto; “a distancia” queda reservado como expresión editorial secundaria.
- La home reduce repetición conceptual: se elimina un bloque explicativo redundante y se sustituye la introducción fotográfica por una composición de evidencia de proceso (evaluar → entrenar/registrar → ajustar).
- Las imágenes dejan de atribuir rostros o personas concretas a la identidad de IBERFIT; los alt y captions describen la escena, no una persona como cara de la marca.
- Contacto prioriza WhatsApp directo y presenta el orientador como herramienta opcional para preparar la consulta.
- Se añaden breadcrumbs visibles y semánticos en páginas profundas y locales.
- Las páginas locales se dividen en tres familias editoriales (logística, entorno y ritmo urbano) para romper el patrón de landing parametrizada sin inventar información local.
- BreadcrumbList local pasa a Inicio → Presencial → comuna (y Home → In person → area en inglés).
- Home y versión inglesa comparten la misma lógica evidence-first.
- SEO/GEO: llms.txt declara “entrenamiento personal online” como término canónico y mantiene “a distancia” solo como sinónimo editorial.
- Se preservan IRI como línea de base, reseñas verificadas, origen de marca europeo y separación IRI/seguimiento.

# Cambios V6.35

- IBERFIT vuelve a ser el centro absoluto de la narrativa: se elimina la exposición pública del nombre y la identidad personal del fundador.
- “Sobre IBERFIT” presenta el origen como una trayectoria de marca: formación universitaria en España, conocimiento de los contextos español y alemán y adaptación posterior en Chile.
- El recorrido España → Alemania → España → Chile se conserva porque explica el origen metodológico de IBERFIT, pero deja de contar circunstancias personales.
- Alemania se vincula a precisión, proceso y consistencia; España a la formación y maduración metodológica; Chile a la adaptación de ese recorrido en una marca propia.
- Se eliminan la entidad Person y las referencias founder del schema público para evitar personalizar la entidad IBERFIT.
- Home y versión inglesa sustituyen cualquier llamada a “la persona detrás” por origen, filosofía y criterio de marca.
- llms.txt queda alineado con la misma regla: historia institucional, no marca personal.
- Estilos de identidad personal retirados; la nueva hoja V6.35 evita caché heredada de V6.34.
- Se conservan intactas las mejoras V6.34 de páginas locales, SEO online/a distancia, reseñas verificables, IRI y composición editorial.

# Cambios V6.34

- Arquitectura semántica cerrada para la modalidad remota: “entrenamiento personal online” se mantiene como término SEO y “a distancia” como lenguaje de marca; la URL canónica /online/ se conserva.
- Home menos modular y menos “builder/IA”: se fusionan filosofía y promesa en una composición editorial con ledger de principios, reduciendo bloques conceptuales consecutivos.
- Se reforzó la autenticidad de “Sobre IBERFIT”; esta línea se revisa en V6.35 para mantener la historia centrada en la marca y no en una persona concreta.
- Las siete páginas locales en español se reescriben con contexto propio de cada comuna y dejan de compartir el mismo patrón de chips/copy.
- Las siete páginas locales en inglés dejan de ser traducciones parametrizadas y reciben narrativa específica por comuna.
- Diseño local refinado: las cards repetitivas pasan a un tratamiento editorial más sobrio, con mejor jerarquía y menor apariencia SaaS/IA.
- Se añaden enlaces visibles a las reseñas completas en Google como evidencia verificable.
- llms.txt reforzado con contexto de marca y equivalencia semántica online/a distancia.
- Se preservan el nuevo hero, el IRI como línea de base, el orientador no-chatbot y la separación Diagnóstico IRI / seguimiento.

# Cambios V6.33

- Rediseño editorial del recorrido de marca en “Sobre IBERFIT”.
- Banderas SVG reales y consistentes en Windows, macOS, iOS y Android; se eliminan los emoji regionales que podían mostrarse como letras.
- El recorrido España → Alemania → España → Chile pasa a ocupar el ancho completo de la sección, con más aire y jerarquía.
- Las cuatro etapas se diferencian por narrativa: Origen, Expansión/Perspectiva, Consolidación e IBERFIT hoy.
- Responsive específico: 4 columnas en escritorio, 2 en tableta y 1 en móvil, sin columnas estrechas ni texto agolpado.
- Chile se destaca de forma sutil, sin convertir la última etapa en un bloque visualmente pesado.
- Paridad completa ES/EN y respeto por preferencias de movimiento reducido.

# Cambios V6.28

- Nombres comerciales visibles en castellano: Online pasa a A distancia; se conserva /online/ por compatibilidad.
- IRI web alineado con IRI 2.0: línea de base, seguimiento longitudinal y sin puntuación global.
- Informe IRI rasterizado antiguo sustituido por HTML accesible y adaptable.
- Caché CSS corregida y versionada con styles.v628.css.
- Controles automáticos contra regresiones de nomenclatura, IRI y versionado.
- Fotografía responsive sensible a densidad para pantallas Retina/alta resolución.
- SEO técnico reforzado: lastmod real, previews ampliadas de Google y datos estructurados preservados.
- Medición de conversión reforzada con evento GA4 recomendado generate_lead, siempre posterior al consentimiento.
- Interacción premium adaptativa: profundidad en escritorio, composición táctil específica en móvil/tableta y respeto estricto de reducir movimiento.
