#!/usr/bin/env node
/**
 * Source-consistency test for the self-contained CSP-S Evidence Atlas.
 *
 * Run: node tools/verify_star_atlas.mjs
 * Does not open browser or assert mathematical/OJ correctness.
 */
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {Script} from "node:vm";
import path from "node:path";
import {fileURLToPath} from "node:url";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const html=readFileSync(path.join(root,"总览/可视化/赛场星图_2026-10-12.html"),"utf8");
assert.equal(readFileSync(path.join(root,"赛场星图.html"),"utf8"),html,"root alias divergence");
assert.equal(readFileSync(path.join(root,"docs/index.html"),"utf8"),html,"Pages mirror divergence");
assert.equal(readFileSync(path.join(root,"总览/可视化/阶段成长仪表盘.html"),"utf8"),html,"legacy dashboard alias divergence");
const dataRaw=readFileSync(path.join(root,"总览/可视化/赛场星图_2026-10-12.json"),"utf8");
const css=readFileSync(path.join(root,"总览/可视化/星图源码/star-map.css"),"utf8");
const js=readFileSync(path.join(root,"总览/可视化/星图源码/star-map.js"),"utf8");
const match=html.match(/<script type="application\/json" id="app-data">([\s\S]*?)<\/script>/);
assert.ok(match,"embedded data missing");
const data=JSON.parse(match[1]),external=JSON.parse(dataRaw);
assert.deepEqual(data,external,"standalone embedded data diverges from canonical JSON");
assert.equal(data.questions.length,36,"expected 36 canonical problems");
assert.equal(data.questions.filter(q=>q.system==="代码源").length,32);
assert.equal(data.questions.filter(q=>q.system==="代码部落").length,4);
assert.equal(new Set(data.questions.map(q=>q.id)).size,36);
const scores=data.questions.filter(q=>q.system==="代码源").reduce((total,q)=>total+q.score,0);
assert.equal(scores,669);assert.deepEqual(data.scores,[45,130,204,0,15,115,145,15]);
for(let i=1;i<=8;i++){const day=data.questions.filter(q=>q.contest==="Day"+i);assert.equal(day.length,4);assert.equal(day.reduce((n,q)=>n+q.score,0),data.scores[i-1]);}
assert.equal(data.collected.replaySaves,113);
assert.equal(data.collected.semanticAllClosed,false);
assert.equal(data.postgame.A.verifiedIndependent,false);
assert.equal(data.postgame.C.verifiedIndependent,false);
assert.equal(data.events.length,11);
assert.equal(data.tasks.length,6);
assert.ok(html.includes("<style>"+css+"</style>"),"CSS divergence");
assert.ok(html.includes("<script>"+js+"</script>"),"JS divergence");
new Script(js,{filename:"star-map.js"});
const ids=new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]));
for(const x of js.matchAll(/\$\(["']#([A-Za-z0-9_-]+)["']/g)){assert.ok(ids.has(x[1]),"missing UI selector "+x[1]);}
const important=["m-total","m-best","m-records","heatmap","score-plot","filter-query","filter-day","filter-status","problem-grid","story-nav","task-list","detail-backdrop","app-data"];
for(const name of important)assert.ok(ids.has(name),"required UI element absent: "+name);
const hanzi=[...html].filter(c=>/[\u3400-\u9fff]/u.test(c)).length;
assert.ok(hanzi>=1500,"interface appears empty");
assert.ok(!html.includes("https://cdn."),"dependency-free offline file expected");
console.log("ATLAS_STATIC_PASS",JSON.stringify({problems:data.questions.length,contestScore:scores,days:8,events:data.events.length,missions:data.tasks.length,jsBytes:js.length,htmlBytes:html.length,hanzi}));
