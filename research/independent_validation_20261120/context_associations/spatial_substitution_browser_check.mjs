import { chromium } from '../translation_catalogue/node_modules/playwright/index.mjs';
import fs from 'node:fs';

const url = process.argv[2] || new URL('./results/spatial_substitution/spatial_substitution.html', import.meta.url).href;
const browser = await chromium.launch({ headless: true, channel: 'chrome', args: ['--allow-file-access-from-files'] });
const errors = [];
try {
  const page = await browser.newPage({ viewport: { width: 1400, height: 1050 } });
  page.on('pageerror', e => errors.push(String(e)));
  await page.goto(url);
  const data = await page.evaluate(() => ({
    images: [...document.images].map(i => ({ src: i.getAttribute('src'), loaded: i.complete && i.naturalWidth > 0 })),
    text: document.body.innerText,
  }));
  if (data.images.length !== 5 || data.images.some(i => !i.loaded)) throw new Error('A comparison image failed to load');
  for (const phrase of ['No primary longer-remainder match', 'No held-out prediction was scored', 'cloth has not been independently established', 'M-1200']) {
    if (!data.text.includes(phrase)) throw new Error('Missing material result: ' + phrase);
  }
  const links = await page.locator('a').evaluateAll(elements => elements.map(a => a.href).filter(x => x.startsWith('file:')));
  for (const link of links) if (!fs.existsSync(new URL(link))) throw new Error('Broken data link: ' + link);
  await page.screenshot({ path: '/tmp/ivc-spatial-desktop.png' });
  await page.setViewportSize({ width: 390, height: 844 });
  if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1)) throw new Error('Mobile page overflows');
  await page.screenshot({ path: '/tmp/ivc-spatial-mobile.png' });
  if (errors.length) throw new Error(errors.join('\n'));
  console.log(JSON.stringify({ imagesLoaded: data.images.length, localLinks: links.length, mobileOverflow: false, errors }));
} finally {
  await browser.close();
}
