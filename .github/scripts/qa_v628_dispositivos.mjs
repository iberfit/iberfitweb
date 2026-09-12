import { chromium } from "playwright";
import fs from "node:fs/promises";
import path from "node:path";

const base = process.env.BASE_URL || "http://127.0.0.1:4173";
const out = process.env.QA_OUT || "evidence/v628-devices";

const devices = [
  { name: "movil-compacto-320", width: 320, height: 568, touch: true, mobile: true },
  { name: "movil-360", width: 360, height: 800, touch: true, mobile: true },
  { name: "movil-390", width: 390, height: 844, touch: true, mobile: true },
  { name: "movil-430", width: 430, height: 932, touch: true, mobile: true },
  { name: "movil-horizontal", width: 844, height: 390, touch: true, mobile: true },
  { name: "tableta-vertical", width: 768, height: 1024, touch: true, mobile: false },
  { name: "tableta-horizontal", width: 1024, height: 768, touch: true, mobile: false },
  { name: "portatil", width: 1366, height: 900, touch: false, mobile: false },
  { name: "escritorio", width: 1600, height: 1000, touch: false, mobile: false },
];

const routes = [
  ["/", "inicio"],
  ["/diagnostico-iri/", "iri"],
  ["/contacto/", "contacto"],
  ["/online/", "a-distancia"],
  ["/entrenador-personal-las-condes/", "las-condes"],
  ["/privacidad/", "privacidad"],
  ["/en/", "inicio-en"],
];

const importantTouchSelectors = [
  ".btn",
  ".menu-toggle",
  ".lang-switch a",
  ".choice-chip",
  ".device-dock a",
  ".consent-link",
  ".consent-close",
  "select",
];

await fs.mkdir(out, { recursive: true });

const browser = await chromium.launch({ headless: true });
const findings = [];

function add(device, route, code, detail) {
  findings.push({ device, route, code, detail });
}

for (const device of devices) {
  const context = await browser.newContext({
    viewport: { width: device.width, height: device.height },
    hasTouch: device.touch,
    isMobile: device.mobile,
    deviceScaleFactor: 1,
    locale: "es-CL",
  });

  for (const [route, label] of routes) {
    const page = await context.newPage();
    const consoleErrors = [];
    const failedResponses = [];

    page.on("console", msg => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });
    page.on("pageerror", err => consoleErrors.push(String(err)));
    page.on("response", response => {
      if (response.status() >= 400) failedResponses.push(response.status() + " " + response.url());
    });

    const response = await page.goto(base + route, { waitUntil: "networkidle", timeout: 30000 });
    if (!response || !response.ok()) {
      add(device.name, route, "HTTP", response ? String(response.status()) : "sin respuesta");
      await page.close();
      continue;
    }

    await page.emulateMedia({ reducedMotion: "reduce" });

    const geometry = await page.evaluate(() => ({
      innerWidth: window.innerWidth,
      bodyWidth: document.body.scrollWidth,
      htmlWidth: document.documentElement.scrollWidth,
      h1: document.querySelectorAll("h1").length,
      main: (() => {
        const el = document.querySelector("main");
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { left: r.left, right: r.right, width: r.width };
      })(),
    }));

    if (geometry.h1 !== 1) add(device.name, route, "H1", String(geometry.h1));
    const overflow = Math.max(geometry.bodyWidth, geometry.htmlWidth) - geometry.innerWidth;
    if (overflow > 2) add(device.name, route, "DESBORDE_HORIZONTAL", String(overflow));
    if (!geometry.main) {
      add(device.name, route, "MAIN", "contenido principal ausente");
    } else if (geometry.main.left < -2 || geometry.main.right > geometry.innerWidth + 2) {
      add(device.name, route, "MAIN_DESBORDE", JSON.stringify(geometry.main));
    }

    const brokenImages = await page.locator("img").evaluateAll(nodes =>
      nodes.filter(img => img.complete && img.naturalWidth === 0)
        .map(img => img.getAttribute("src") || "(sin src)")
    );
    for (const src of brokenImages) add(device.name, route, "IMAGEN_ROTA", src);

    const menuState = await page.evaluate(() => {
      const toggle = document.querySelector(".menu-toggle");
      const nav = document.querySelector(".navlinks");
      if (!toggle || !nav) return null;
      return {
        toggleDisplay: getComputedStyle(toggle).display,
        navDisplay: getComputedStyle(nav).display,
      };
    });

    if (device.width <= 980) {
      if (!menuState || menuState.toggleDisplay === "none") add(device.name, route, "MENU_MOVIL", "botón ausente");
      if (menuState && menuState.navDisplay !== "none") add(device.name, route, "MENU_MOVIL", "navegación abierta al cargar");
      if (menuState && menuState.toggleDisplay !== "none") {
        await page.locator(".menu-toggle").click();
        const open = await page.locator(".navlinks").evaluate(el => getComputedStyle(el).display !== "none");
        if (!open) add(device.name, route, "MENU_MOVIL", "no abre");
        await page.keyboard.press("Escape");
        const closed = await page.locator(".navlinks").evaluate(el => getComputedStyle(el).display === "none");
        if (!closed) add(device.name, route, "MENU_MOVIL", "Escape no cierra");
      }
    } else {
      if (!menuState || menuState.toggleDisplay !== "none") add(device.name, route, "MENU_ESCRITORIO", "botón móvil visible");
      if (menuState && menuState.navDisplay === "none") add(device.name, route, "MENU_ESCRITORIO", "navegación oculta");
    }

    if (device.touch) {
      for (const selector of importantTouchSelectors) {
        const boxes = await page.locator(selector).evaluateAll(nodes =>
          nodes.filter(el => {
            const r = el.getBoundingClientRect();
            const s = getComputedStyle(el);
            return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none";
          }).map(el => {
            const r = el.getBoundingClientRect();
            return {
              w: r.width,
              h: r.height,
              text: (el.textContent || el.getAttribute("aria-label") || "").trim().slice(0, 50)
            };
          })
        );
        for (const box of boxes) {
          if (box.h < 44 || box.w < 44) {
            add(
              device.name,
              route,
              "OBJETIVO_TACTIL_44",
              selector + " · " + box.text + " · " + Math.round(box.w) + "×" + Math.round(box.h) + "px"
            );
          }
        }
      }
    }

    if (device.width <= 430) {
      const smallFormControls = await page.locator("input,select,textarea").evaluateAll(nodes =>
        nodes.filter(el => {
          const r = el.getBoundingClientRect();
          const s = getComputedStyle(el);
          return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && parseFloat(s.fontSize) < 16;
        }).map(el => ({
          tag: el.tagName.toLowerCase(),
          name: el.getAttribute("name") || el.getAttribute("id") || "",
          fontSize: getComputedStyle(el).fontSize
        }))
      );
      for (const item of smallFormControls) {
        add(device.name, route, "ZOOM_FORMULARIO_IOS", JSON.stringify(item));
      }
    }

    if (route === "/" || route === "/diagnostico-iri/") {
      const iri = page.locator(".report-preview-v2");
      if (await iri.count() !== 1) {
        add(device.name, route, "IRI", "vista longitudinal ausente");
      } else {
        const box = await iri.boundingBox();
        if (!box || box.width > device.width + 2) add(device.name, route, "IRI_DESBORDE", box ? String(box.width) : "sin caja");
        const text = (await iri.innerText()).toLowerCase();
        for (const forbidden of ["overall index", "iri global", "índice global", "puntuación global"]) {
          if (text.includes(forbidden)) add(device.name, route, "IRI_PUNTUACION_GLOBAL", forbidden);
        }
      }
    }

    if (route === "/contacto/") {
      if (await page.locator("[data-orientador-form]").count() !== 1) add(device.name, route, "ORIENTADOR", "formulario ausente");
      const selects = await page.locator("[data-orientador-form] select").count();
      if (selects < 2) add(device.name, route, "ORIENTADOR", "selectores incompletos");
    }

    if (route === "/online/") {
      const visible = (await page.locator("body").innerText()).toLowerCase();
      if (/(^|\s)online(\s|$)/i.test(visible)) add(device.name, route, "NOMBRE_COMERCIAL", "Online visible en español");
      if (!visible.includes("a distancia")) add(device.name, route, "NOMBRE_COMERCIAL", "A distancia ausente");
    }

    if (failedResponses.length) {
      for (const failure of failedResponses) add(device.name, route, "HTTP_RECURSO", failure);
    }
    if (consoleErrors.length) {
      const generic404 = failedResponses.some(item => item.startsWith("404 "));
      for (const error of consoleErrors) {
        if (generic404 && error.includes("404 (File not found)")) continue;
        add(device.name, route, "CONSOLA", error);
      }
    }

    if (["inicio", "iri", "contacto"].includes(label)) {
      await page.screenshot({
        path: path.join(out, device.name + "-" + label + ".png"),
        fullPage: true,
      });
    }

    await page.close();
  }

  await context.close();

  // Segunda serie visual para revisión humana sin el banner de primera visita.
  // Se ejecuta en un contexto aislado para no alterar las pruebas de consentimiento anteriores.
  const reviewContext = await browser.newContext({
    viewport: { width: device.width, height: device.height },
    hasTouch: device.touch,
    isMobile: device.mobile,
    deviceScaleFactor: 1,
    locale: "es-CL",
  });
  const reviewPage = await reviewContext.newPage();
  await reviewPage.goto(base + "/", { waitUntil: "networkidle", timeout: 30000 });
  const necessary = reviewPage.locator("[data-consent-necessary]");
  if (await necessary.count() === 1 && await necessary.isVisible()) {
    await necessary.click();
    await reviewPage.waitForTimeout(250);
  }
  for (const [reviewRoute, reviewLabel] of routes.filter(([, label]) => ["inicio", "iri", "contacto"].includes(label))) {
    if (reviewRoute !== "/") {
      await reviewPage.goto(base + reviewRoute, { waitUntil: "networkidle", timeout: 30000 });
    }

    // Activar cada reveal como lo haría un usuario al recorrer la página.
    // Evita depender de scroll suave/timings del navegador headless.
    const revealItems = reviewPage.locator(".reveal");
    const revealCount = await revealItems.count();
    for (let index = 0; index < revealCount; index += 1) {
      const item = revealItems.nth(index);
      if (await item.isVisible()) {
        await item.scrollIntoViewIfNeeded();
        await reviewPage.waitForTimeout(45);
      }
    }
    await reviewPage.waitForFunction(() => {
      return Array.from(document.querySelectorAll(".reveal")).every(node => {
        const style = getComputedStyle(node);
        const rect = node.getBoundingClientRect();
        const rendered = style.display !== "none" && style.visibility !== "hidden" && rect.width > 0 && rect.height > 0;
        if (!rendered || !node.classList.contains("visible")) return true;
        return Number.parseFloat(style.opacity || "1") >= 0.95;
      });
    }, null, { timeout: 2500 }).catch(() => {});

    await reviewPage.evaluate(() => {
      document.documentElement.style.scrollBehavior = "auto";
      window.scrollTo(0, 0);
    });
    await reviewPage.waitForTimeout(120);

    const hiddenReveal = await reviewPage.locator(".reveal").evaluateAll(nodes =>
      nodes.flatMap((node, index) => {
        const style = getComputedStyle(node);
        const rect = node.getBoundingClientRect();
        const rendered = style.display !== "none" && style.visibility !== "hidden" && rect.width > 0 && rect.height > 0;
        const hidden = Number.parseFloat(style.opacity || "1") < 0.95;
        if (!(rendered && hidden)) return [];
        return [{
          index,
          tag: node.tagName.toLowerCase(),
          id: node.id || "",
          className: String(node.className || "").slice(0,120),
          text: String(node.textContent || "").replace(/\s+/g," ").trim().slice(0,140),
          opacity: style.opacity,
          top: Math.round(rect.top),
          height: Math.round(rect.height),
        }];
      })
    );
    if (hiddenReveal.length) {
      add(device.name, reviewRoute, "REVEAL_NO_VISIBLE", JSON.stringify(hiddenReveal));
    }

    await reviewPage.evaluate(() => {
      document.documentElement.style.scrollBehavior = "auto";
      window.scrollTo(0, 0);
    });
    await reviewPage.waitForTimeout(120);
    await reviewPage.screenshot({
      path: path.join(out, device.name + "-" + reviewLabel + "-sin-banner.png"),
      fullPage: true,
    });
  }
  await reviewContext.close();

  // Accesibilidad: con movimiento reducido ningún contenido reveal renderizado
  // puede depender del IntersectionObserver para ser legible.
  const reducedContext = await browser.newContext({
    viewport: { width: device.width, height: device.height },
    hasTouch: device.touch,
    isMobile: device.mobile,
    deviceScaleFactor: 1,
    locale: "es-CL",
    reducedMotion: "reduce",
  });
  const reducedPage = await reducedContext.newPage();
  await reducedPage.goto(base + "/", { waitUntil: "networkidle", timeout: 30000 });
  const hiddenReduced = await reducedPage.locator(".reveal").evaluateAll(nodes =>
    nodes.filter(node => {
      const style = getComputedStyle(node);
      const rect = node.getBoundingClientRect();
      const rendered = style.display !== "none" && style.visibility !== "hidden" && rect.width > 0 && rect.height > 0;
      return rendered && Number.parseFloat(style.opacity || "1") < 0.95;
    }).length
  );
  if (hiddenReduced) {
    add(device.name, "/", "REDUCED_MOTION_CONTENIDO_OCULTO", String(hiddenReduced));
  }
  await reducedContext.close();
}

await browser.close();

const report = {
  version: "6.28",
  generatedAt: new Date().toISOString(),
  devices,
  routes: routes.map(([route]) => route),
  findings,
  ok: findings.length === 0,
};

await fs.writeFile(path.join(out, "report.json"), JSON.stringify(report, null, 2) + "\n", "utf8");

if (findings.length) {
  console.error(JSON.stringify(report, null, 2));
  process.exit(1);
}

console.log("QA dispositivos V6.28: PASS · 9 perfiles · 7 rutas · 0 hallazgos");
