# GLOBAL COMMERCIAL GROWTH 360 — control operativo
Fecha de referencia: 26-11-2026 (Chile). Fuente: Search Console vía Windsor.ai, propiedad sc-domain:iberfit.cl; GitHub PR 6 y ejecución 45920249771.
Base pública: V6.43.30, SHA 01ecf69798904651f706b2379dccc20ee0e21e9d. No se cambia ningún archivo del sitio público en esta PR.

## Línea base
| Período | Impresiones | Clics | CTR | Posición |
|---|---:|---:|---:|---:|
| 29/09–26/10 | 131 | 5 | 3,82% | 10,73 |
| 27/10–23/11 | 140 | 5 | 3,57% | 7,44 |
| 24/11 (dato parcial) | 14 | 0 | 0% | 19,21 |

Los datos de noviembre anteriores a la publicación no miden su impacto. Los datos de consultas visibles no concilian necesariamente con totales de propiedad. Chile 68 impresiones/5 clics; Portugal 35/0; España 7/0; EEUU 8/0. Móvil 59/3; escritorio 81/2. No hay datos GA4 ni GBP conectados al momento de la comprobación. No extrapolar ventas.

## Decisiones
- Mantener las páginas consolidadas, incluida la página principal y Las Condes. No crear páginas nuevas sin demanda e intención demostrables.
- Las Condes: consulta personal trainer las condes 8 impresiones, posición 20,75, sin clics; revisar cobertura e intención de búsqueda a domicilio, ya ofrecida en presencial. Providencia: 15 impresiones y 3 clics; preservar. Ñuñoa: investigar relevancia antes de editar. No modificar precios.
- Competidores observados en búsqueda: MOVUM, SCV, SilvaFIT, ProTrainer, personal-trainer.cl. Diferenciar mediante evaluación, criterio, evidencia y seguimiento; no imitar promesas ni precios.
- SEO/GEO: mantener robots, llms.txt, pares ES/EN y entidades existentes. La capacidad de rastreo no equivale a citación ni recomendación. Verificar acceso de bots legítimos en Cloudflare con datos reales, no solo user-agent.
- Revisión local GBP: validar categorías, zona de servicio, enlace, reseñas auténticas y fotografías; no crear ubicación ni ficha duplicada. Usar enlaces UTM públicos sin datos personales cuando sea posible.
- Marketing orgánico: Instagram como evidencia de método y trabajo; Facebook para presencia local; TikTok solo si hay recursos para contenido original y evaluación de captación; Google Business Profile para demanda local. No lanzar anuncios.
- Revisar Core Web Vitals con datos de campo cuando existan; separar laboratorio. No afirmar métricas no medidas.

## Medición comercial
GA4: comprobar propiedad y flujo web G-JXD1JSN7K3. Crear dimensión de alcance evento acquisition_source solo si no existe; comprobar recepción real de acquisition_context, contact_intent y generate_lead con consentimiento en DebugView/Realtime. Revisar configuración de medición mejorada y exclusión de parámetros sensibles. No registrar generate_lead como venta real. No publicar identificadores de contactos ni exportar mensajes.

Registro operativo privado: una fila por contacto recibido, identificador aleatorio local, fecha de recepción, procedencia declarada/ desconocida, modalidad solicitada, etapa (recibido, conversación, IRI contratado, entrenamiento contratado, recurrente, cerrado), fechas de cambios y resultado. No almacenar nombres, teléfonos, correos, datos clínicos ni mensajes en el registro analítico. No guardar datos reales en Git. Mantener el archivo bajo control del propietario, sin Supabase. No unir automáticamente los registros con GA4 ni atribuir causalidad.
Indicadores por período: contactos únicos recibidos, conversaciones, contrataciones IRI, contrataciones entrenamiento, recurrentes; tasas con denominador explícito. Clics de WhatsApp y generate_lead son intenciones, no contactos. Fuente desconocida se conserva como tal.
Evaluar semanalmente visibilidad, consultas no marca, país, dispositivo, entradas y embudo comercial; comparar períodos de 28 días completos, sin imputar días faltantes. Revisar a partir de datos posteriores al lanzamiento. No confundir cambios de posición promedio con crecimiento.
 
## Puertas de entrega
Todas las versiones deben ejecutar las regresiones comerciales estáticas y de navegador. El alcance exacto del diff de V6.43.30 permanece como contrato histórico; cambios posteriores requieren alcance nuevo explícito y certificación de integridad. Mantener congelación de páginas del certificador general. Cambios futuros de contenido requieren preview noindex, verificación de SHA, regresión, promoción exacta y recuperación. Si el sitio no cambia, no hay motivo para desplegar de nuevo.

## Consolidación operativa — 26/11/2026
El Panel operativo de IBERFIT ya dispone de las pestañas 06_LEADS, 18_EMBUDO_COMERCIAL y 20_PUBLICACIONES_RESEÑAS. No crear un CRM paralelo. La medición comercial debe reutilizar este sistema y distinguir contactos recibidos de intenciones GA4; el embudo existente requiere revisión de rangos fijos (filas 5:200) y de etapas que pueden omitirse, porque IRI no es obligatorio. No exportar registros personales al repositorio.
Metricool: marca 6943596; Instagram, Facebook y GBP conectados. Instagram registra 9 seguidores; los campos de actividad presentan datos faltantes y ceros. No hay posts programados del 27/11 al 27/12. No interpretar nulos como ceros. GA4 sigue sin conexión a Windsor.
Enlaces etiquetados para utilizar cuando se autorice la edición del canal:
- GBP ficha: https://iberfit.cl/?utm_source=google_business_profile&utm_medium=organic&utm_campaign=perfil
- GBP IRI: https://iberfit.cl/diagnostico-iri/?utm_source=google_business_profile&utm_medium=organic&utm_campaign=iri
- Instagram perfil: https://iberfit.cl/?utm_source=instagram&utm_medium=organic_social&utm_campaign=perfil
- Facebook perfil: https://iberfit.cl/?utm_source=facebook&utm_medium=organic_social&utm_campaign=perfil
No enviar nombres, teléfonos, correos ni identificadores individuales en UTM. El parámetro acquisition_source clasifica la fuente; no verifica identidad ni contratación. El cambio de categoría se activa únicamente tras el despliegue de V6.43.31 y el consentimiento de audiencia. No cambiar fichas ni publicar posts sin verificar el destino y la autorización correspondiente.
