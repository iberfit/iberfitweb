import { chromium } from "playwright";
import fs from "node:fs/promises";
import path from "node:path";

const base = process.env.BASE_URL || "http://127.0.0.1:4173";
const out = process.env.QA_OUT || "evidence/v628-devices";

const devices = [
  { name: "movil-360", width: 360, height: 800, touch: true },
  { name: "movil-430", width: 430, height: 932, touch: true },
  { name: "tableta-vertical", width: 768, height: 1024, touch: true },
  { name: "tableta-horizontal", width: 1024, height: 768, touch: true },
  { name: "portatil", width: 1366, height: 900, touch: false },
  { name: "escritorio", width: 1600, height: 1000, touch: false },
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
    isMobile: device.width <= 430,
    deviceScaleFactor: 1,
    locale: "es-CL",
  });

  for (const [route, label] of routes) {
    const page = await context.newPage();
    const consoleErrors = [];
    page.on("console", msg => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });
    page.on("pageerror", err => consoleErrors.push(String(err)));

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
    }));

    if (geometry.h1 !== 1) add(device.name, route, "H1", String(geometry.h1));
    const overflow = Math.max(geometry.bodyWidth, geometry.htmlWidth) - geometry.innerWidth;
    if (overflow > 2) add(device.name, route, "DESBORDE_HORIZONTAL", String(overflow));

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
            return r.width > 0 && r.height > 0 && s.visibility !== "hidden";
          }).map(el => {
            const r = el.getBoundingClientRect();
            return { w: r.width, h: r.height, text: (el.textContent || "").trim().slice(0, 50) };
          })
        );
        for (const box of boxes) {
          if (box.h < 36) add(device.name, route, "OBJETIVO_TACTIL", selector + " · " + box.text + " · " + Math.round(box.h) + "px");
        }
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

    if (consoleErrors.length) {
      for (const error of consoleErrors) add(device.name, route, "CONSOLA", error);
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

console.log("QA dispositivos V6.28: PASS · 6 perfiles · 7 rutas · 0 hallazgos");
