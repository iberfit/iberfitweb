# IBERFIT · Auditoría de producción web
Fecha: 11 de septiembre de 2026

## Objetivo
Establecer una base segura para elevar iberfit.cl al estándar IBERFIT sin mezclarla con app.iberfit.cl ni modificar producción antes de recuperar la fuente exacta desplegada.

## Regla de marca
- Producto, servicios, programas y módulos visibles: nombres comerciales en castellano.
- La identidad original nace en castellano; la versión inglesa es una traducción internacional.
- Evitar nombres comerciales en inglés como "Longevity", "Growth OS", "Coach Copilot" u otros equivalentes.
- Terminología técnica inevitable (WebAuthn, Supabase, API, nombres de ramas/archivos) puede mantenerse solo en documentación técnica.
- Marca: verde oscuro, dorado, crema; estética sobria, técnica y premium.
- Propuesta central: "Entrenamiento personal con criterio: diagnóstico, planificación, control y seguimiento."

## Repositorios
- Fuente destinada a ser canónica de la web: iberfit/iberfitweb.
- Estado actual de main: V5.20 importada el 22/06/2026, commit d716156e127ff0cc3acd325f36b319618cb700c0.
- Histórico archivado: iberfit/iberfit-web.
- Aplicación productiva separada: iberfit/iberfit-m26-app.
- Recursos compartidos: iberfit/iberfit-assets.

## Hallazgo P0 · GitHub no representa producción
La web que sirve hoy iberfit.cl contiene una generación posterior a la V5.20 existente en main. Se observan en producción una arquitectura de home más reciente, reseñas reales, orientador de modalidad/contacto, narrativa IRI evolucionada, fotografías, consentimiento/privacidad y páginas locales posteriores.

Existe evidencia histórica de candidatas V6.21 → V6.22 → V6.23 → V6.25 → V6.26 y de una candidata local posterior denominada IBERFIT_WEB_V6_27_1_PREMIUM_CANDIDATE.zip.

### Decisión
NO desarrollar nuevas funciones partiendo de V5.20.
Primero debe recuperarse la fuente exacta de producción o la candidata V6.27.1 y certificarse contra el sitio publicado.

## Hallazgo P0 · Dos generaciones visibles
La web productiva no es totalmente homogénea.

### Generación moderna observada
- Inicio
- Diagnóstico IRI
- Método
- Presencial
- Híbrido
- Online
- Sobre IBERFIT
- Contacto
- algunas landings locales actualizadas

Características:
- CTA "Solicitar IRI" / "Solicitar orientación".
- nuevo pie de página.
- "Sobre IBERFIT".
- orientador de tres pasos.
- reseñas reales enlazadas.
- narrativa centrada en decisiones, seguimiento y evolución.

### Superficies rezagadas detectadas
- Privacidad aparece con navegación/pie/textos de una generación anterior.
- El rastreo directo devolvió versiones antiguas de varias landings locales, mientras el índice de búsqueda muestra versiones posteriores para esas mismas rutas.
- La diferencia entre fuentes de rastreo indica que no debemos inferir la fuente de verdad desde una única copia indexada.

## Hallazgo P0 · IRI web desalineado con IRI 2.0
La versión inglesa de la home todavía muestra un ejemplo de informe con un "Overall index" numérico.

La dirección actual de IRI 2.0 en la aplicación es:
evaluación → interpretación → decisión → entrenamiento → reevaluación → evolución.

Reglas:
- no inventar un índice global/composite que mezcle dimensiones distintas;
- comparar solo mediciones con protocolos compatibles;
- separar cambio descriptivo de interpretación profesional;
- primera evaluación = línea basal, no progresión fabricada.

### Acción
Eliminar del contenido web cualquier puntuación global heredada y rediseñar el ejemplo IRI para que refleje la metodología longitudinal actual.

## Hallazgo P1 · Landings locales
Las páginas locales más recientes ya empiezan a diferenciar cobertura, logística y autonomía por comuna, pero comparten todavía mucha estructura común.

### Riesgo
- contenido excesivamente similar;
- menor utilidad real para el visitante;
- menor diferenciación SEO local.

### Acción
Cada comuna debe aportar información propia y útil:
- tipo de cobertura real;
- restricciones de desplazamiento/acceso;
- entorno típico de entrenamiento;
- modalidad que suele encajar mejor;
- cómo se confirma disponibilidad;
- CTA contextual;
- enlaces internos relevantes.

No crear texto artificial solo para variar palabras.

## Hallazgo P1 · Privacidad y confianza
La política visible necesita evolucionar desde una explicación básica a un centro de privacidad coherente con el nivel de la aplicación.

Debe cubrir, según corresponda al sitio:
- responsable y canal de contacto;
- categorías de datos;
- finalidad;
- base/consentimiento cuando aplique;
- analítica y publicidad;
- cookies/almacenamiento;
- proveedores;
- conservación;
- derechos;
- revocación/preferencias;
- relación con WhatsApp y correo;
- distinción entre web pública y aplicación;
- cambios/versionado de la política.

La redacción legal definitiva debe validarse conforme a la normativa aplicable antes de publicación.

## Hallazgo P1 · Conversión
El embudo correcto es:
IBERFIT → entender el método → Diagnóstico IRI → orientación → contacto → servicio → app.

No vender la aplicación como producto separado.

### Medición mínima
- clic a IRI;
- inicio/completado del orientador;
- clic WhatsApp;
- correo;
- selección de modalidad;
- navegación local;
- aceptación/revocación de consentimiento;
- conversión a IRI agendado cuando pueda medirse sin invadir privacidad.

## Hallazgo P1 · Multidispositivo
"No romperse responsive" no es suficiente.

### Matriz mínima
- móvil pequeño;
- móvil estándar;
- móvil grande;
- tableta vertical;
- tableta horizontal;
- portátil;
- escritorio;
- pantalla amplia.

### QA en cada familia
- cabecera/menú;
- legibilidad;
- jerarquía;
- CTA;
- orientador;
- tablas/informe IRI;
- imágenes y recortes;
- formularios/selectores;
- teclado/foco;
- touch targets;
- reduced motion;
- cambio ES/EN;
- consentimiento;
- WhatsApp;
- Core Web Vitals.

## Hallazgo P1 · CI/QA web
El repositorio web no tiene todavía el nivel de control del repositorio de la aplicación.

### Objetivo
Añadir, sobre la fuente recuperada:
1. validación HTML;
2. enlaces y recursos internos;
3. un H1 por página;
4. títulos/descripciones/canonical/hreflang;
5. sitemap/robots;
6. chequeo de términos de marca prohibidos;
7. comprobación de que IRI no reintroduzca índice global;
8. accesibilidad automática;
9. Playwright móvil/tableta/escritorio;
10. regresión visual;
11. Lighthouse;
12. prueba de orientador/WhatsApp;
13. consentimiento y analítica;
14. preview antes de producción;
15. promoción productiva solo desde commit certificado.

## Orden de trabajo
P0. Recuperar fuente exacta de producción/V6.27.1.
P0. Comparar contra iberfit.cl y generar manifiesto/hash de archivos.
P0. Restaurar GitHub como fuente única.
P0. Alinear IRI web con IRI 2.0.
P0. Unificar privacidad, navegación, pie y CTA.
P1. Diferenciar landings locales.
P1. Implementar CI/QA multidispositivo.
P1. Auditar rendimiento/accesibilidad/SEO.
P1. Refinar conversión y medición.
P2. Evolucionar nuevas líneas comerciales con nombres en castellano y validación comercial previa.

## Regla de despliegue web
fuente exacta
→ rama
→ cambios
→ pruebas
→ revisión visual multidispositivo
→ accesibilidad
→ rendimiento
→ SEO
→ preview
→ aprobación
→ producción
→ verificación de identidad de versión.

Nunca editar producción manualmente si el cambio puede quedar versionado y desplegado desde GitHub.
