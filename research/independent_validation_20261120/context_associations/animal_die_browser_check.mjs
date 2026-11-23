import { chromium } from '../translation_catalogue/node_modules/playwright/index.mjs';

const browser = await chromium.launch({ headless: true, channel: 'chrome', args: ['--allow-file-access-from-files'] });
const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
const errors = [];
page.on('pageerror', error => errors.push(String(error)));
try {
  await page.goto(new URL('./results/animal_die_followup.html', import.meta.url).href);
  const report = await page.evaluate(() => ({
    title: document.title,
    images: [...document.images].map(i => ({ src: i.getAttribute('src'), loaded: i.complete && i.naturalWidth > 0 })),
    text: document.body.innerText,
  }));
  if (report.images.length !== 10 || report.images.some(i => !i.loaded)) throw new Error('Missing comparison photograph');
  if (!report.text.includes('No fresh 923-family prediction') || !report.text.includes('no issuer-versus-commodity test result')) throw new Error('Missing test-status explanation');
  await page.screenshot({ path: '/tmp/ivc-seal-review/animal-die-desktop.png', fullPage: true });
  await page.screenshot({ path: '/tmp/ivc-seal-review/animal-die-top.png' });
  await page.setViewportSize({ width: 390, height: 844 });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
  if (overflow) throw new Error('Mobile page overflows');
  await page.screenshot({ path: '/tmp/ivc-seal-review/animal-die-mobile.png', fullPage: true });
  if (errors.length) throw new Error(errors.join('\n'));
  console.log(JSON.stringify({ images: report.images.length, loaded: true, mobileOverflow: overflow, errors }));
} finally {
  await browser.close();
}
