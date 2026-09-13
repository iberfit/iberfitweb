# IBERFIT · Publicar la web V6.32

La candidata está en `candidate/v628/`. El nombre histórico de la carpeta se conserva; `VERSION` identifica la versión real. Esta carpeta contiene el sitio ya construido. No necesita `npm build`.

## Opción sin comandos: Cloudflare Pages

1. Inicia sesión en Cloudflare y abre **Workers & Pages**.
2. Abre el proyecto de la web corporativa, documentado como **web-iberfit**. Comprueba en **Custom domains** que tiene asociado **iberfit.cl**. La comprobación del dominio importa más que el nombre del proyecto: no publiques en el proyecto de la aplicación.
3. Si es un proyecto **Direct Upload**, entra en **Create deployment**, selecciona **Preview** y carga `IBERFIT_WEB_V6.32.zip`. En el ZIP, `index.html`, `assets/` y `VERSION` están directamente en la raíz.
4. Abre la URL de vista previa. Revisa inicio, menú, contacto, selección y edición de respuestas, preferencias de privacidad y versión inglesa en móvil y escritorio. `VERSION` debe mostrar `6.32`.
5. Crea otro deployment con el mismo ZIP, esta vez en **Production**. Conserva el deployment de producción anterior como punto de retorno.
6. Abre `https://iberfit.cl/VERSION` y comprueba `6.32`. Recarga la portada y prueba menú y orientador. No hace falta cambiar DNS, dominio, ni configuración de `app.iberfit.cl`.

Si no aparece la opción de arrastrar archivos, el proyecto puede estar integrado con Git. No crees un proyecto sustituto: usa la opción siguiente sobre el proyecto existente.

## Opción por terminal: proyecto Pages existente

Requiere Node.js y acceso a la cuenta Cloudflare propietaria del proyecto. Desde la carpeta del repositorio que contiene esta candidata:

```bash
npx wrangler@4.120.0 login
npx wrangler@4.120.0 pages project list
npx wrangler@4.120.0 pages deploy candidate/v628 --project-name web-iberfit --branch v632-review
```

La primera publicación es una vista previa. Antes de publicar producción, confirma en Cloudflare el proyecto con `iberfit.cl` asociado y su rama de producción. El contexto recuperado indica `production`; si la configuración actual muestra otra rama, usa esa rama en el comando siguiente:

```bash
npx wrangler@4.120.0 pages deploy candidate/v628 --project-name web-iberfit --branch production
```

Estos comandos usan **Pages**. El archivo `wrangler.web-iberfit.jsonc` del repositorio describe un Worker de staging anterior: no uses `wrangler deploy --config wrangler.web-iberfit.jsonc` para sustituir esta publicación de Pages.

## Volver a la versión anterior

En el mismo proyecto Pages, abre **Deployments**, localiza el deployment de producción anterior y usa **Rollback to this deployment**. Comprueba después la portada y el menú. No cambies registros DNS ni el proyecto de la app.

## Para que ChatGPT pueda publicar en una sesión futura

La autorización del usuario ya existe. Falta una herramienta disponible que pueda ejecutar el despliegue autorizado en la cuenta o disparar el workflow de publicación existente. El conector GitHub de esta sesión permite guardar código y ejecutar la QA mediante sus eventos de push, pero no expone una acción directa de `workflow_dispatch`. Un token pegado en el chat no añade esa capacidad y no es necesario compartirlo aquí. Cambiar de modelo tampoco la añade.

## Referencias oficiales

- Direct Upload y diferencia entre proyectos de carga directa y proyectos integrados con Git: https://developers.cloudflare.com/pages/get-started/direct-upload/
- Publicación con Wrangler y CI: https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/
