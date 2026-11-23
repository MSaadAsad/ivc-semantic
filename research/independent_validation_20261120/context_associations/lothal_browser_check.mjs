import { chromium } from '../translation_catalogue/node_modules/playwright/index.mjs';

const browser = await chromium.launch({ headless: true, channel: 'chrome' });
const page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
const errors = [];
page.on('pageerror', error => errors.push(String(error)));
const visible = async () => page.locator('#objects tbody tr:not([hidden])').count();
try {
  await page.goto(new URL('./results/lothal_tables/lothal.html', import.meta.url).href);
  if (await visible() !== 93) throw new Error('Expected all93 source objects');
  await page.selectOption('#coverage', 'false');
  if (await visible() !== 25) throw new Error('Missing transcription filter failed');
  await page.click('#reset');
  await page.selectOption('#novelty', 'true');
  if (await visible() !== 69) throw new Error('Prior evidence filter failed');
  await page.selectOption('#coverage', 'true');
  if (await visible() !== 44) throw new Error('Joined new-label filter failed');
  await page.click('#reset');
  await page.fill('#search', 'L-142');
  if (await visible() !== 1) throw new Error('Exact specimen search failed');
  const specimen = await page.locator('#objects tbody tr:not([hidden])').innerText();
  if (!specimen.includes('Wooden box')) throw new Error('Specimen source classification missing');
  await page.click('#reset');
  await page.selectOption('#category', 'pottery_jar');
  if (await visible() !== 21) throw new Error('Jar category count failed');
  await page.click('#reset');
  const images = await page.evaluate(() => [...document.images].map(i => ({ src: i.src, ok: i.complete && i.naturalWidth > 0 })));
  if (images.length !== 2 || images.some(i => !i.ok)) throw new Error('Chart failed to load');
  if (await page.locator('h1').count() !== 1) throw new Error('Duplicate heading');
  await page.evaluate(async () => {scrollTo(0,0); await document.fonts.ready; await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));});
  await page.screenshot({ path: '/tmp/ivc-lothal-tables/report-desktop-top.png' });
  await page.locator('h2').filter({ hasText: 'same physical seal' }).scrollIntoViewIfNeeded();
  await page.screenshot({ path: '/tmp/ivc-lothal-tables/report-desktop-dies.png' });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(async () => {scrollTo(0,0); await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));});
  if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1)) throw new Error('Mobile page overflow');
  await page.screenshot({ path: '/tmp/ivc-lothal-tables/report-mobile-top.png' });
  if (errors.length) throw new Error(errors.join('\n'));
  console.log(JSON.stringify({ objects:93, missing:25, newLabels:69, newlyJoined:44, jars:21, chartImages:2, mobileOverflow:false, errors }));
} finally {
  await browser.close();
}
