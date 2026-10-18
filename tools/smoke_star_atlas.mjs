#!/usr/bin/env node
/**
 * Real browser smoke test. Requires: npm install --no-save playwright
 * Browser: npx playwright install chromium
 * Run: node tools/smoke_star_atlas.mjs
 */
import assert from "node:assert/strict";
import {readFileSync, mkdirSync} from "node:fs";
import path from "node:path";
import os from "node:os";
import {fileURLToPath, pathToFileURL} from "node:url";
import {chromium} from "playwright";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const local=pathToFileURL(path.join(root,"总览/可视化/赛场星图_2026-10-12.html")).toString();
const errors=[];
const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
try{
  const page=await browser.newPage({viewport:{width:1440,height:960},acceptDownloads:true,deviceScaleFactor:1});
  page.on("pageerror",e=>errors.push("JS: "+e.message));
  page.on("console",m=>{if(m.type()==="error")errors.push("CONSOLE: "+m.text())});
  await page.goto(local,{waitUntil:"load"});
  await page.waitForSelector(".problem");
  assert.match(await page.locator("#m-total").innerText(),/669/);
  assert.equal(await page.locator(".problem").count(),36);
  assert.equal(await page.locator(".heat-cell").count(),32);
  assert.equal(await page.locator(".chart-node").count(),8);
  assert.equal(await page.locator(".story-tab").count(),11);
  assert.equal(await page.locator(".task-card").count(),6);
  await page.locator("#filter-query").fill("今汐的巡防分区");
  assert.equal(await page.locator(".problem").count(),1);
  await page.locator("#reset").click();
  await page.locator("#filter-system").selectOption("代码部落");
  assert.equal(await page.locator(".problem").count(),4);
  await page.locator("#reset").click();
  await page.locator("#filter-day").selectOption("8");
  assert.equal(await page.locator(".problem").count(),4);
  await page.locator(".problem").filter({hasText:"今汐的巡防分区"}).click();
  assert.equal(await page.locator("#detail-backdrop").isVisible(),true);
  assert.match(await page.locator("#detail-score").innerText(),/15\/100/);
  await page.keyboard.press("Escape");
  assert.equal(await page.locator("#detail-backdrop").isVisible(),false);
  await page.locator("#reset").click();
  await page.locator(".story-tab").nth(9).click();
  assert.match(await page.locator("#story-title").innerText(),/C：修对一处/);
  const promise=page.waitForEvent("download");
  await page.locator("#export").click();
  const download=await promise;
  assert.match(download.suggestedFilename(),/\.csv$/);
  const body=readFileSync(await download.path(),"utf8");
  assert.match(body,/今汐的巡防分区/);
  const shot=process.env.ATLAS_SCREENSHOT || path.join(os.tmpdir(),"csp-s-evidence-atlas.png");
  mkdirSync(path.dirname(shot),{recursive:true});
  await page.screenshot({path:shot,fullPage:true,animations:"disabled"});
  const mobile=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1});
  mobile.on("pageerror",e=>errors.push("MOBILE JS: "+e.message));
  await mobile.goto(local,{waitUntil:"load"});
  await mobile.waitForSelector(".problem");
  assert.equal(await mobile.locator(".problem").count(),36);
  const geometry=await mobile.evaluate(()=>({width:innerWidth,document:document.documentElement.scrollWidth,body:document.body.scrollWidth,offenders:Array.from(document.querySelectorAll("body *")).map(e=>({tag:e.tagName,cls:e.className?.baseVal||e.className,id:e.id,right:e.getBoundingClientRect().right})).filter(o=>o.right>innerWidth+4).slice(0,12)}));
  console.log("ATLAS_MOBILE_GEOMETRY",JSON.stringify(geometry));
  assert.ok(geometry.document<=geometry.width+3&&geometry.body<=geometry.width+3,"mobile horizontal overflow");
  const mobileShot=path.join(path.dirname(shot),"atlas-mobile.png");
  await mobile.screenshot({path:mobileShot,fullPage:true,animations:"disabled"});
  assert.deepEqual(errors,[],"unexpected browser errors");
  console.log("ATLAS_BROWSER_PASS",JSON.stringify({desktop:1440,mobile:390,questions:36,heatmap:32,scoreDots:8,stories:11,download:true,screenshot:shot,mobileScreenshot:mobileShot}));
}finally{await browser.close()}
