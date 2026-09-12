import { chromium } from 'playwright';

const base = process.env.BASE_URL || 'http://127.0.0.1:4173';
const browser = await chromium.launch({ headless: true });

const thirdParty = url =>
  /https:\/\/(www\.googletagmanager\.com|www\.google-analytics\.com|region1\.google-analytics\.com|analytics\.google\.com|connect\.facebook\.net|www\.facebook\.com)\//.test(url);

async function scenario({ name, selector, expectGoogle, expectMeta, blockStorage = false }) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, locale: 'es-CL' });
  const page = await context.newPage();
  const requests = [];
  const errors = [];

  page.on('request', req => {
    if (thirdParty(req.url())) requests.push(req.url());
  });
  page.on('pageerror', err => errors.push(String(err)));

  if (blockStorage) {
    await page.addInitScript(() => {
      Storage.prototype.getItem = function(){ throw new Error('storage-blocked-test'); };
      Storage.prototype.setItem = function(){ throw new Error('storage-blocked-test'); };
    });
  }

  const response = await page.goto(base + '/', { waitUntil: 'networkidle', timeout: 30000 });
  if (!response?.ok()) throw new Error(name + ': inicio no cargó');

  await page.waitForTimeout(700);
  if (requests.length) {
    throw new Error(name + ': hubo tracking antes del consentimiento: ' + JSON.stringify(requests));
  }

  const banner = page.locator('.consent-banner');
  if (await banner.count() !== 1) throw new Error(name + ': banner de privacidad ausente');

  if (blockStorage) {
    const unrelated = errors.filter(x => !x.includes('storage-blocked-test'));
    if (unrelated.length) throw new Error(name + ': error con almacenamiento bloqueado: ' + unrelated.join(' | '));
    await context.close();
    return;
  }

  await page.locator(selector).click();
  await page.waitForTimeout(1400);

  const google = requests.some(url => url.includes('googletagmanager.com') || url.includes('google-analytics.com') || url.includes('analytics.google.com'));
  const meta = requests.some(url => url.includes('connect.facebook.net') || url.includes('www.facebook.com'));

  if (google !== expectGoogle) throw new Error(name + ': Google esperado=' + expectGoogle + ' observado=' + google + ' · ' + JSON.stringify(requests));
  if (meta !== expectMeta) throw new Error(name + ': Meta esperado=' + expectMeta + ' observado=' + meta + ' · ' + JSON.stringify(requests));
  if (errors.length) throw new Error(name + ': errores JS: ' + errors.join(' | '));

  await context.close();
}

await scenario({
  name: 'solo necesarias',
  selector: '[data-consent-necessary]',
  expectGoogle: false,
  expectMeta: false
});
await scenario({
  name: 'solo audiencia',
  selector: '[data-consent-audience]',
  expectGoogle: true,
  expectMeta: false
});
await scenario({
  name: 'aceptar todo',
  selector: '[data-consent-all]',
  expectGoogle: true,
  expectMeta: true
});
await scenario({
  name: 'almacenamiento bloqueado',
  selector: '[data-consent-necessary]',
  expectGoogle: false,
  expectMeta: false,
  blockStorage: true
});

await browser.close();
console.log('Privacidad V6.28: PASS · 0 tracking previo · consentimiento granular · almacenamiento bloqueado tolerado');
