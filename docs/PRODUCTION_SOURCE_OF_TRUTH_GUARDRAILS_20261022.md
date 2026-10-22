# IBERFIT — Barrera de seguridad para la web pública (22-10-2026)

> **ESTADO: NO APTO PARA PUBLICAR DESDE ESTA RAMA / `main` HISTÓRICO.** Este documento no autoriza ninguna publicación automática.

## Evidencia verificada
- Dominio comercial: `https://iberfit.cl/`. Aplicación privada: `https://app.iberfit.cl/` — completamente fuera de este trabajo.
- Search Console informó el 22-10-2026 de **32 URL descubiertas en sitemap**, y 18 páginas indexadas en su informe (datos de usuario); descubiertas no equivale a indexadas.
- Sitemap que el usuario comprobó en producción: **16 rutas ES + 16 EN**; `/en/method/`, `/en/about/`, `/en/online/` incluidas.
- La rama `main` de `iberfit/iberfitweb`, SHA `5eb558e8b9d0d52b916df82e25bb76bcdad8b50a`, expone **17 URL en sitemap** y únicamente `/en/index.html` para la versión inglesa. No refleja por sí sola la publicación activa. El checkpoint `checkpoint/v64327-sitemap-accuracy-production-2026-10-06` consultado tampoco contiene la matriz bilingüe completa.
- Se ha documentado un proyecto Cloudflare Pages denominado `web-iberfit`, pero **el origen del despliegue activo, su ID y sus artefactos todavía no se han verificado mediante Cloudflare**.
- `/en/method/` y `/personal-trainer-nunoa/`: solicitud de indexación comunicada como enviada; **Google no garantiza indexación**.
- `https://app.iberfit.cl/`: `noindex` intencional. No tocar.
- URL histórica `/en/contacto/` mostrada como 404 en Search Console. Considerar 301 a `/en/contact/` **solo después de verificar las rutas en producción**.

## P0 — Bloqueo obligatorio antes de cualquier deploy
1. Abrir Cloudflare Pages > proyecto `web-iberfit` > Deployments. Identificar **deployment activo** (ID, fecha, entorno, dominio, procedencia Git o Direct Upload y SHA si existe).
2. Extraer o localizar el **artefacto completo que origina el deployment activo**, no una copia antigua ni reconstruida de páginas aisladas. Incluir HTML de 32 rutas, CSS/JS, imágenes, fuentes, reglas de redirect y headers, robots y sitemap. Si Cloudflare no ofrece descarga del artefacto, recuperar **el paquete original publicado** del sistema que lo generó o de sus respaldos.
3. Comparar SHA-256 por archivo y manifest de 32 rutas entre la fuente y el activo. Guardar respaldo íntegro junto con el ID de deployment actual y posibilidad de rollback verificada.
4. Crear branch de trabajo desde la **fuente coincidente con producción**, NO desde `main` legado sin una reconciliación explícita; añadir protección para impedir eliminar rutas o hacer regresión bilingüe.
5. Mantener `app.iberfit.cl`, SIGNATURE, QA, Supabase y los datos de cliente completamente fuera del despliegue.

## Auditoría externa sin mutaciones
La herramienta `tools/iberfit-web-live-audit.mjs` (Node 20+) comprueba las 32 rutas esperadas con peticiones GET de solo lectura.

```bash
node tools/iberfit-web-live-audit.mjs > iberfit-web-audit.json
```

La salida incluye fecha, página, HTTP, idioma `lang`, canonical, `noindex`, `hreflang` (aviso), H1 y cotejo con sitemap. Código de salida != 0 significa fallo en la comprobación; **no significa automáticamente fallo de la web**, ya que bloqueos anti-bot, redirecciones legítimas y limitaciones de red deben revisarse. El ejecutor necesita acceso HTTP saliente y no usa cookies ni credenciales.

**Límite importante:** no sustituye pruebas de Core Web Vitals, accesibilidad, navegación, conversión, métricas Search Console o inspección visual en móviles.

## P1 — Mejoras premium, solo tras P0
- Revisar el enlazado bilingüe: self-canonical, `hreflang` `es-CL` / `en` recíprocos y `x-default` solo donde corresponda, sin inferir traducciones inexistentes.
- Mantener SEO local útil en Las Condes, Vitacura, Providencia, Lo Barnechea, Ñuñoa, La Reina, Peñalolén; textos **realmente específicos**, sin inventar cobertura, testimonios, instalaciones ni resultados.
- Revisar contenido humano y CTA sobre Diagnóstico IRI, método y modalidades; optimizar el flujo de WhatsApp/contexto y la medición de contacto.
- Comprobar semántica SEO, schema auténtico, OG, imágenes con alt apropiado, enlaces, JavaScript mínimo, CLS/LCP/INP, teclado/lector de pantalla, reduced-motion y responsive real.
- Respetar identidad oficial: verde oscuro/negro profundo, crema cálido y acentos dorados; fotografía real autorizada, tipografía editorial legible, texto natural de Chile; sin estética de SaaS genérico, claims grandilocuentes ni materiales inventados.
- Medir resultados: clics, impresiones, consultas y conversiones reales; no confundir solicitud con indexación.

## Criterios de aceptación para publicación
- Fuente de producción y rollback comprobados por evidencia independiente.
- 32/32 rutas esperadas verificadas en preview y en dominio final, sin pérdida de ES/EN.
- Canonical e idiomas correctos, sitemap válido, app privada no afectada.
- Evidencia de QA móvil/escritorio, accesibilidad, navegación y rendimiento.
- Despliegue por promoción controlada con comparación antes/después; rollback disponible.

**No fusionar PR de este bloque como paso previo automático a producción.** Primero resolver el origen activo de Cloudflare.
