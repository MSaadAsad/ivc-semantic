// Run from the repo with the catalogue's existing Playwright install and Chrome.
// Optional argument: the exported report directory instead of source results.
import { chromium } from '../translation_catalogue/node_modules/playwright/index.mjs';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const base=path.dirname(fileURLToPath(import.meta.url));
const root=process.argv[2]?path.resolve(process.argv[2]):path.join(base,'results');
const browser=await chromium.launch({headless:true,channel:'chrome'});
const checks=[];
try {
 for(const [name,viewport] of [['desktop',{width:1280,height:1050}],['mobile',{width:390,height:844}]]){
  const page=await browser.newPage({viewport});const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.join(root,'open_rebus.html')).href);
  await page.locator('img').evaluateAll(imgs=>Promise.all(imgs.map(i=>i.decode())));
  const stats=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,
   rows:document.querySelectorAll('tbody tr').length,cards:document.querySelectorAll('.card').length,
   images:[...document.images].every(i=>i.complete&&i.naturalWidth>0),
   links:[...document.querySelectorAll('a')].map(a=>a.href)}));
  const missing=stats.links.filter(u=>u.startsWith('file:')&&!fs.existsSync(fileURLToPath(u)));
  if(stats.overflow||!stats.images||errors.length||missing.length||stats.rows!==680||stats.cards!==8)
    throw Error(JSON.stringify({name,stats,errors,missing}));
  await page.locator('#filter').fill('enemy');
  const visible=await page.locator('tbody tr:visible').count();
  if(!visible||visible>=680)throw Error('Filter failed: '+visible);
  await page.locator('#filter').fill('');
  await page.screenshot({path:path.join(root,`open_rebus-${name}-preview.png`)});
  if(name==='desktop')await page.locator('#priority').screenshot({path:path.join(root,'open_rebus_priority.png')});
  checks.push({name,overflow:stats.overflow,rows:stats.rows,cards:stats.cards,filtered_rows:visible,errors,missing});
  await page.close();
 }
}finally{await browser.close();}
fs.writeFileSync(path.join(root,'open_rebus_browser_checks.json'),JSON.stringify(checks,null,2)+'\n');
console.log(JSON.stringify(checks));
