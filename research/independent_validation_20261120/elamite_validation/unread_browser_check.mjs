import { chromium } from '../translation_catalogue/node_modules/playwright/index.mjs';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
const base=path.dirname(fileURLToPath(import.meta.url));
const root=process.argv[2]?path.resolve(process.argv[2]):path.join(base,'results');
const browser=await chromium.launch({headless:true,channel:'chrome'});
const checks=[];
try{
 for(const [name,viewport] of [['desktop',{width:1280,height:1050}],['mobile',{width:390,height:844}]]){
  const page=await browser.newPage({viewport});const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.join(root,'unread_elamite.html')).href);
  await page.locator('img').evaluateAll(imgs=>Promise.all(imgs.map(i=>i.decode())));
  const result=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,
   cards:document.querySelectorAll('article').length,images:[...document.images].every(i=>i.complete&&i.naturalWidth>0),
   links:[...document.querySelectorAll('a')].map(a=>a.href)}));
  const missing=result.links.filter(u=>u.startsWith('file:')&&!fs.existsSync(fileURLToPath(u)));
  if(result.overflow||result.cards!==6||!result.images||missing.length||errors.length)throw Error(JSON.stringify({result,missing,errors}));
  await page.screenshot({path:path.join(root,`unread-${name}-preview.png`)});
  checks.push({name,overflow:result.overflow,cards:result.cards,images:result.images,missing,errors});
  await page.close();
 }
}finally{await browser.close();}
fs.writeFileSync(path.join(root,'unread_browser_checks.json'),JSON.stringify(checks,null,2)+'\n');
console.log(JSON.stringify(checks));
