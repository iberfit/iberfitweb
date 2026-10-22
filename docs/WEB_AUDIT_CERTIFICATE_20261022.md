# IBERFIT · Certificación remota de disponibilidad y SEO básico · 22-10-2026

## Alcance y prueba verificable
- Workflow GitHub Actions: https://github.com/iberfit/iberfitweb/actions/runs/39835436218
- Código auditado en el PR #2: https://github.com/iberfit/iberfitweb/pull/2
- Hora de la ejecución: `2026-10-22T18:54:23.245Z` (15:54 en Santiago).
- Origen de red de la prueba: ejecutor remoto de GitHub Actions, haciendo peticiones HTTP reales a `https://iberfit.cl`; **no constituye una comprobación de Cloudflare Deployments ni un cambio de producción**.

## Resultado
| Comprobación | Resultado |
|---|---|
| Páginas esperadas del sitemap | 32 (16 ES + 16 EN) |
| Páginas alcanzadas HTTP 200 | 32/32 |
| URL canónica de cada página | 32/32 en ruta esperada |
| Lenguaje HTML (`es` / `en`) | 32/32 según ruta |
| Pareja alterna recíproca por `hreflang` ES/EN | 16/16 pares (32/32 páginas) |
| `x-default` | 32/32 apuntan a URL públicas conocidas |
| Títulos HTML | 32 presentes y 32 únicos |
| Metadescripciones | 32/32 presentes |
| H1 | 32/32 presentes |
| `noindex` inesperado | 0 detectados |
| Sitemap `/sitemap.xml` | 32 rutas esperadas presentes |
| Advertencias del verificador | 0 |
| Fallos del verificador | 0 |

## Interpretación con cautela
- Este resultado valida disponibilidad y una serie acotada de invariantes **técnicos**. NO demuestra que Google tenga 32 páginas indexadas: Search Console mostraba 18 indexadas cuando se revisó.
- No demuestra seguridad, privacidad, calidad de contenido, accesibilidad completa, LCP/CLS/INP, comportamiento JS completo, embudo de conversión ni buenas métricas comerciales.
- `x-default` apuntando a una portada general puede ser válido según la documentación de Google; por ello el test comprueba que el destino pertenezca al dominio público, sin imponer que sea el mismo par de traducción. Referencia: https://developers.google.com/search/docs/specialty/international/localized-versions
- La URL histórica `/en/contacto/` **no figura entre las 32 canónicas**; en Search Console aparece como 404 y requiere decisión separada sobre su redirección permanente.
- Se mantiene P0 de localizar el artefacto/origen del deployment activo de Cloudflare Pages `web-iberfit` y su copia segura con rollback. **La rama principal de este repositorio no coincide con el despliegue actual; no publicar desde ella.**

## Próximas acciones tras recuperar la fuente real
1. Comprobar en Cloudflare el deployment activo, origen y artefacto completo, más respaldo SHA-256 y ruta de reversión.
2. Certificar integridad del paquete de 32 páginas y redirecciones históricas.
3. Mejorar contenido local auténtico, enlazado contextual, proceso de contacto, accesibilidad, desempeño móvil y medición, usando identidad oficial de IBERFIT.
4. Lanzar preview controlada y pruebas funcionales ES/EN antes de producción.
