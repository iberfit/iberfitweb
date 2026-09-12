import { chromium } from "playwright";
import fs from "node:fs/promises";
import path from "node:path";

const BASE_URL = (process.env.BASE_URL || "https://iberfit.cl").replace(/\/$/, "");
const OUT = process.env.AUDIT_OUT || "evidence/live-web-ai";
const FAIL_ON_REGRESSION = process.env.FAIL_ON_REGRESSION !== "0";

const criticalRoutes = new Set([
  "/",
  "/diagnostico-iri/",
  "/metodo/",
  "/presencial/",
  "/hibrido/",
  "/online/",
  "/sobre-iberfit/",
  "/contacto/",
  "/en/",
  "/en/iri-assessment/",
  "/en/method/",
  "/en/contact/",
]);

const devices = [
  { name: "mobile", width: 390, height: 844, mobile: true, touch: true },
  { name: "tablet", width: 820, height: 1180, mobile: false, touch: true, criticalOnly: true },
  { name: "desktop", width: 1440, height: 1200, mobile: false, touch: false },
];

const findings = [];
const pages = [];

function addFinding({ severity = "warning", device, route, code, detail }) {
  findings.push({ severity, device, route, code, detail });
}

function slugFor(route) {
  if (route === "/") return "home";
  return route.replace(/^\/+|\/+$/g, "").replace(/[^a-z0-9]+/gi, "-").toLowerCase() || "home";
}

async function mkdirp(p) {
  await fs.mkdir(p, { recursive: true });
}

async function getSitemapRoutes() {
  const url = BASE_URL + "/sitemap.xml";
  const response = await fetch(url, {
    headers: { "user-agent": "IBERFIT-AI-Visual-Auditor/1.0 (+https://iberfit.cl)" },
  });
  if (!response.ok) throw new Error(`Sitemap HTTP ${response.status}`);
  const xml = await response.text();
  const routes = [];
  for (const match of xml.matchAll(/<loc>\s*(https?:\/\/[^<]+)\s*<\/loc>/gi)) {
    try {
      const parsed = new URL(match[1]);
      if (parsed.origin === new URL(BASE_URL).origin) {
        routes.push(parsed.pathname || "/");
      }
    } catch {}
  }
  return [...new Set(routes)];
}

await mkdirp(OUT);

let routes = [];
try {
  routes = await getSitemapRoutes();
} catch (error) {
  addFinding({
    severity: "critical",
    device: "global",
    route: "/sitemap.xml",
    code: "SITEMAP_UNAVAILABLE",
    detail: String(error),
  });
  routes = [...criticalRoutes];
}

for (const route of criticalRoutes) {
  if (!routes.includes(route)) routes.push(route);
}

const browser = await chromium.launch({ headless: true });

for (const device of devices) {
  const context = await browser.newContext({
    viewport: { width: device.width, height: device.height },
    isMobile: device.mobile,
    hasTouch: device.touch,
    locale: "es-CL",
    deviceScaleFactor: 1,
    colorScheme: "light",
  });

  const deviceRoutes = device.criticalOnly
    ? routes.filter(route => criticalRoutes.has(route))
    : routes;

  for (const route of deviceRoutes) {
    const page = await context.newPage();
    const consoleErrors = [];
    const pageErrors = [];
    const failedRequests = [];
    const badResponses = [];
    const url = BASE_URL + route;
    const slug = slugFor(route);
    const pageDir = path.join(OUT, "pages", device.name);
    await mkdirp(pageDir);

    page.on("console", msg => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });
    page.on("pageerror", error => pageErrors.push(String(error)));
    page.on("requestfailed", request => {
      failedRequests.push({
        url: request.url(),
        error: request.failure()?.errorText || "request failed",
      });
    });
    page.on("response", response => {
      if (response.status() >= 400) {
        const u = response.url();
        if (u.startsWith(BASE_URL)) badResponses.push({ status: response.status(), url: u });
      }
    });

    let response = null;
    let navigationError = null;
    try {
      response = await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
      await page.waitForTimeout(1200);
      await page.emulateMedia({ reducedMotion: "reduce" });
    } catch (error) {
      navigationError = String(error);
    }

    const status = response?.status() ?? null;
    if (navigationError || !response || !response.ok()) {
      addFinding({
        severity: criticalRoutes.has(route) ? "critical" : "error",
        device: device.name,
        route,
        code: "NAVIGATION",
        detail: navigationError || `HTTP ${status}`,
      });
    }

    let metrics = null;
    let visibleText = "";
    let title = "";
    let canonical = "";
    let description = "";
    let brokenImages = [];
    let interactive = null;

    if (response) {
      try {
        metrics = await page.evaluate(() => {
          const body = document.body;
          const html = document.documentElement;
          const h1 = [...document.querySelectorAll("h1")].filter(el => {
            const r = el.getBoundingClientRect();
            const s = getComputedStyle(el);
            return r.width > 0 && r.height > 0 && s.display !== "none" && s.visibility !== "hidden";
          });
          const main = document.querySelector("main");
          const mainRect = main?.getBoundingClientRect();
          return {
            innerWidth: window.innerWidth,
            innerHeight: window.innerHeight,
            bodyScrollWidth: body?.scrollWidth || 0,
            htmlScrollWidth: html?.scrollWidth || 0,
            documentHeight: Math.max(body?.scrollHeight || 0, html?.scrollHeight || 0),
            h1Count: h1.length,
            mainPresent: Boolean(main),
            mainRect: mainRect
              ? { left: mainRect.left, right: mainRect.right, width: mainRect.width }
              : null,
            lang: html.lang || "",
          };
        });

        title = await page.title();
        canonical = (await page.locator('link[rel="canonical"]').first().getAttribute("href")) || "";
        description = (await page.locator('meta[name="description"]').first().getAttribute("content")) || "";

        visibleText = await page.locator("body").innerText().catch(() => "");
        visibleText = visibleText.replace(/\s+/g, " ").trim().slice(0, 12000);

        brokenImages = await page.locator("img").evaluateAll(nodes =>
          nodes
            .filter(img => img.complete && img.naturalWidth === 0)
            .map(img => img.currentSrc || img.getAttribute("src") || "(sin src)")
        );

        interactive = await page.locator("a,button,input,select,textarea").evaluateAll(nodes => {
          const visible = nodes.filter(el => {
            const r = el.getBoundingClientRect();
            const s = getComputedStyle(el);
            return r.width > 0 && r.height > 0 && s.display !== "none" && s.visibility !== "hidden";
          });
          const unnamed = visible.filter(el => {
            const tag = el.tagName.toLowerCase();
            const label =
              el.getAttribute("aria-label") ||
              el.getAttribute("title") ||
              (el.textContent || "").trim() ||
              (tag === "input" ? el.getAttribute("placeholder") || el.getAttribute("name") || "" : "");
            return !label;
          });
          return { visibleCount: visible.length, unnamedCount: unnamed.length };
        });

        const overflow = Math.max(metrics.bodyScrollWidth, metrics.htmlScrollWidth) - metrics.innerWidth;
        if (overflow > 4) {
          addFinding({
            severity: "critical",
            device: device.name,
            route,
            code: "HORIZONTAL_OVERFLOW",
            detail: `${Math.round(overflow)}px`,
          });
        }

        if (!metrics.mainPresent) {
          addFinding({
            severity: criticalRoutes.has(route) ? "error" : "warning",
            device: device.name,
            route,
            code: "MAIN_MISSING",
            detail: "No se encontró <main>",
          });
        }

        if (metrics.h1Count !== 1) {
          addFinding({
            severity: criticalRoutes.has(route) ? "error" : "warning",
            device: device.name,
            route,
            code: "H1_COUNT",
            detail: String(metrics.h1Count),
          });
        }

        for (const src of brokenImages) {
          addFinding({
            severity: "critical",
            device: device.name,
            route,
            code: "BROKEN_IMAGE",
            detail: src,
          });
        }

        if (!title.trim()) {
          addFinding({
            severity: "error",
            device: device.name,
            route,
            code: "TITLE_MISSING",
            detail: "title vacío",
          });
        }
        if (!canonical.trim()) {
          addFinding({
            severity: "warning",
            device: device.name,
            route,
            code: "CANONICAL_MISSING",
            detail: "canonical ausente",
          });
        }
        if (!description.trim()) {
          addFinding({
            severity: "warning",
            device: device.name,
            route,
            code: "DESCRIPTION_MISSING",
            detail: "meta description ausente",
          });
        }

        if (pageErrors.length) {
          for (const detail of pageErrors) {
            addFinding({
              severity: "critical",
              device: device.name,
              route,
              code: "PAGE_ERROR",
              detail,
            });
          }
        }

        if (consoleErrors.length) {
          for (const detail of consoleErrors.slice(0, 10)) {
            addFinding({
              severity: "warning",
              device: device.name,
              route,
              code: "CONSOLE_ERROR",
              detail,
            });
          }
        }

        if (badResponses.length) {
          for (const item of badResponses.slice(0, 20)) {
            addFinding({
              severity: "error",
              device: device.name,
              route,
              code: "HTTP_SUBRESOURCE",
              detail: `${item.status} ${item.url}`,
            });
          }
        }

        const importantFailed = failedRequests.filter(item => item.url.startsWith(BASE_URL));
        if (importantFailed.length) {
          for (const item of importantFailed.slice(0, 20)) {
            addFinding({
              severity: "error",
              device: device.name,
              route,
              code: "REQUEST_FAILED",
              detail: `${item.error} · ${item.url}`,
            });
          }
        }

        if (device.name === "mobile" && criticalRoutes.has(route)) {
          const toggle = page.locator(".menu-toggle");
          if (await toggle.count()) {
            try {
              if (await toggle.isVisible()) {
                await toggle.click({ timeout: 2000 });
                await page.waitForTimeout(100);
                const nav = page.locator(".navlinks");
                const opened = await nav.count() && await nav.evaluate(el => {
                  const s = getComputedStyle(el);
                  return s.display !== "none" && s.visibility !== "hidden" && Number.parseFloat(s.opacity || "1") > 0.5;
                });
                if (!opened) {
                  addFinding({
                    severity: "critical",
                    device: device.name,
                    route,
                    code: "MOBILE_MENU",
                    detail: "el menú no abrió",
                  });
                }
                await page.keyboard.press("Escape").catch(() => null);
              }
            } catch (error) {
              addFinding({
                severity: "error",
                device: device.name,
                route,
                code: "MOBILE_MENU",
                detail: String(error),
              });
            }
          }
        }

        await page.screenshot({
          path: path.join(pageDir, `${slug}.png`),
          fullPage: true,
          animations: "disabled",
        });
      } catch (error) {
        addFinding({
          severity: "error",
          device: device.name,
          route,
          code: "AUDIT_EXCEPTION",
          detail: String(error),
        });
      }
    }

    const pageRecord = {
      auditedAt: new Date().toISOString(),
      baseUrl: BASE_URL,
      device: device.name,
      viewport: { width: device.width, height: device.height },
      route,
      url,
      status,
      title,
      canonical,
      description,
      metrics,
      brokenImages,
      interactive,
      consoleErrors,
      pageErrors,
      failedRequests,
      badResponses,
      visibleText,
      screenshot: `pages/${device.name}/${slug}.png`,
    };
    pages.push(pageRecord);
    await fs.writeFile(
      path.join(pageDir, `${slug}.json`),
      JSON.stringify(pageRecord, null, 2),
      "utf8"
    );

    await page.close();
  }

  await context.close();
}

await browser.close();

const counts = findings.reduce(
  (acc, item) => {
    acc[item.severity] = (acc[item.severity] || 0) + 1;
    return acc;
  },
  { critical: 0, error: 0, warning: 0 }
);

const report = {
  schema: "iberfit.web.ai-audit.v1",
  auditedAt: new Date().toISOString(),
  baseUrl: BASE_URL,
  sitemapRoutes: routes,
  devices: devices.map(({ criticalOnly, ...device }) => ({ ...device, criticalOnly: Boolean(criticalOnly) })),
  pagesAudited: pages.length,
  counts,
  findings,
  pages,
};

await fs.writeFile(path.join(OUT, "audit.json"), JSON.stringify(report, null, 2), "utf8");

const lines = [
  "# IBERFIT · Auditoría visual IA",
  "",
  `- Fecha: ${report.auditedAt}`,
  `- Objetivo: ${BASE_URL}`,
  `- Páginas/dispositivos auditados: ${pages.length}`,
  `- Hallazgos críticos: ${counts.critical || 0}`,
  `- Errores: ${counts.error || 0}`,
  `- Advertencias: ${counts.warning || 0}`,
  "",
  "## Hallazgos",
  "",
];

if (!findings.length) {
  lines.push("Sin hallazgos.");
} else {
  for (const item of findings) {
    lines.push(`- **${item.severity.toUpperCase()}** · ${item.device} · ${item.route} · ${item.code}: ${item.detail}`);
  }
}

lines.push(
  "",
  "## Evidencias",
  "",
  "Las capturas PNG y los JSON por página están en `pages/<dispositivo>/`.",
  "El archivo `audit.json` contiene el informe completo para análisis automático por IA.",
  ""
);

await fs.writeFile(path.join(OUT, "README.md"), lines.join("\n"), "utf8");

console.log(JSON.stringify({
  baseUrl: BASE_URL,
  routes: routes.length,
  pagesAudited: pages.length,
  counts,
}, null, 2));

if (FAIL_ON_REGRESSION && (counts.critical || 0) > 0) {
  process.exit(1);
}
