
"use strict";
(function(){
const DATA=JSON.parse(document.getElementById("app-data").textContent);
const root=document.documentElement;
const state={day:"all",system:"all",status:"all",q:"",event:8};
const problems=DATA.questions;
const $=(s,r=document)=>r.querySelector(s);
const $$=(s,r=document)=>Array.from(r.querySelectorAll(s));
const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=String(text);return e};
const node=(p,tag,cls,text)=>{const e=el(tag,cls,text);p.append(e);return e};
const set=(s,text)=>{$(s).textContent=String(text)};
const fmt=n=>Number(n).toLocaleString("zh-CN");
const contest=q=>q.system==="代码源"?"代码源 "+q.contest:"CodeLands";
const baseRepo="https://github.com/sutong-claude/Day1/blob/chatgpt/oct7-stage-maintenance/";
const repoPath=path=>baseRepo+path.split("/").map(encodeURIComponent).join("/");
function titleData(){
const scores=DATA.scores;set("#m-total",fmt(scores.reduce((a,b)=>a+b,0))+" / 3200");
set("#m-best",Math.max(...scores)+" / 400");set("#m-count",DATA.questions.length+" 道");set("#m-records",DATA.collected.replaySaves);
set("#source-tag",DATA.snapshot+" / 来源锁定");set("#summary-note",DATA.scoreScope);
set("#e-records",DATA.collected.replaySaves);set("#e-chat",DATA.collected.originalChatMessages);
set("#e-archives",DATA.collected.rawArchives);set("#e-gap",DATA.collected.chatTruncations);}
function scoreChart(){
const svg=$("#score-plot"),NS="http://www.w3.org/2000/svg";const mk=(t,attrs,parent=svg)=>{const x=document.createElementNS(NS,t);for(const [k,v]of Object.entries(attrs||{}))x.setAttribute(k,v);parent.append(x);return x};
const ds=mk("defs");const grad=mk("linearGradient",{id:"scorearea",x1:"0",x2:"0",y1:"0",y2:"1"},ds);mk("stop",{offset:"0%","stop-color":"#47edd8","stop-opacity":".28"},grad);mk("stop",{offset:"100%","stop-color":"#47edd8","stop-opacity":"0"},grad);
const W=850,H=270,ml=46,mr=26,mt=22,mb=42,w=W-ml-mr,h=H-mt-mb;
const X=i=>ml+i*w/7,Y=s=>mt+(400-s)*h/400;
for(let y=0;y<=400;y+=100){mk("line",{x1:ml,x2:W-mr,y1:Y(y),y2:Y(y),class:"chart-grid"});const t=mk("text",{x:ml-11,y:Y(y)+4,"text-anchor":"end",class:"chart-label"});t.textContent=String(y)}
const pts=DATA.days.map((d,i)=>[X(i),Y(d.score)]),poly=pts.map(p=>p.join(",")).join(" "),region=ml+","+(mt+h)+" "+poly+" "+(W-mr)+","+(mt+h);
mk("polygon",{points:region,class:"chart-area"});mk("polyline",{points:poly,class:"chart-line"});
for(let i=0;i<8;i++){const d=DATA.days[i];const dot=mk("circle",{cx:X(i),cy:Y(d.score),r:7,fill:i===2?"#f4c579":"#47edd8",class:"chart-node",tabindex:"0",role:"button","aria-label":"第"+d.day+"场，"+d.score+"分"});dot.addEventListener("click",()=>chooseChart(i));dot.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();chooseChart(i)}});const label=mk("text",{x:X(i),y:H-10,"text-anchor":"middle",class:"chart-label"});label.textContent="D"+d.day;}
chooseChart(7)}
function chooseChart(i){const d=DATA.days[i];set("#focus-day","DAY "+String(d.day).padStart(2,"0"));set("#focus-score",d.score+"/400");set("#focus-title",d.focus);set("#focus-note","赛时正式分数。点击下方题目矩阵可查看该场四题。");$$(".chart-node").forEach((x,j)=>{x.setAttribute("stroke",i===j?"#fff":"#0b151e");x.setAttribute("r",i===j?"9":"7")});}
function classify(s){return s===100?"ace":s>0?"partial":"none"}
function makeHeatmap(){
const grid=$("#heatmap");grid.textContent="";node(grid,"div","heat-head","DAY");
for(const h of ["A","B","C","D"])node(grid,"div","heat-head",h);
for(let d=1;d<=8;d++){node(grid,"div","heat-day","D"+String(d).padStart(2,"0"));for(const letter of ["A","B","C","D"]){const q=problems.find(x=>x.id==="D"+d+"-"+letter);if(!q)continue;
const b=node(grid,"button","heat-cell "+classify(q.score));b.type="button";b.setAttribute("aria-label",q.contest+" "+letter+" "+q.score+"分，查看详情");const val=node(b,"strong","",q.score);node(b,"span","",letter);b.title=q.title+" · "+q.verdict;b.addEventListener("click",()=>openProblem(q));}}
}
function isShown(q){
if(state.system!=="all"&&state.system!==q.system)return false;
if(state.day!=="all"&&q.contest!=="Day"+state.day)return false;
if(state.status==="ac"&&q.score!==100)return false;
if(state.status==="partial"&&!(q.score>0&&q.score<100))return false;
if(state.status==="zero"&&q.score!==0)return false;
const needle=state.q.trim().toLocaleLowerCase();if(needle&&!([q.title,q.id,q.current,q.next,q.verdict,q.contestProcess,q.contest].join(" ").toLocaleLowerCase().includes(needle)))return false;
return true}
function renderProblems(){
const grid=$("#problem-grid");grid.textContent="";
const shown=problems.filter(isShown);set("#result-count",shown.length+" / "+problems.length+" MATCHED");
const slice=shown;
if(!slice.length){node(grid,"div","empty","没有找到符合条件的题目。试试重置筛选。");return}
for(const q of slice){const b=node(grid,"button","glass problem");b.type="button";b.setAttribute("aria-label","打开"+q.id+" "+q.title+" 的复盘详情");
const top=node(b,"div","problem-head");node(top,"span","code",q.id+" / "+(q.system==="代码源"?"CODESOURCE":"CODELANDS"));const sc=node(top,"span","score");node(sc,"b","",q.score);sc.append(" / 100");
node(b,"div","problem-title",q.title);
const tags=node(b,"div","problem-meta");node(tags,"span","status-chip",q.verdict);node(tags,"span","status-chip",q.difficulty);node(tags,"span","status-chip",q.reliability==="高"?"证据较完整":"证据:"+q.reliability);
node(b,"div","problem-brief",q.contestProcess);
node(b,"div","more","OPEN CASE FILE ↗");b.addEventListener("click",()=>openProblem(q));}}
function setDayFilter(day){state.day=day;$("#filter-day").value=day;renderProblems();$("#cases").scrollIntoView({behavior:window.matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth",block:"start"})}
function setupFilters(){
const day=$("#filter-day");for(let i=1;i<=8;i++){const o=node(day,"option","", "Day "+i);o.value=String(i)}
day.addEventListener("change",e=>{state.day=e.target.value;renderProblems()});
$("#filter-system").addEventListener("change",e=>{state.system=e.target.value;if(state.system!=="代码源"){state.day="all";day.value="all"}renderProblems()});
$("#filter-status").addEventListener("change",e=>{state.status=e.target.value;renderProblems()});
$("#filter-query").addEventListener("input",e=>{state.q=e.target.value;renderProblems()});
$("#reset").addEventListener("click",()=>{state.day="all";state.system="all";state.status="all";state.q="";day.value="all";$("#filter-system").value="all";$("#filter-status").value="all";$("#filter-query").value="";renderProblems()});
$("#heat-all").addEventListener("click",()=>{state.day="all";day.value="all";renderProblems();$("#cases").scrollIntoView({behavior:"smooth"})});
$("#export").addEventListener("click",exportCSV);}
function exportCSV(){
const head=["ID","平台","场次","题号","标题","赛时分","状态","当前正确性描述","下一步"];
const rows=[head,...problems.filter(isShown).map(q=>[q.id,q.system,q.contest,q.letter,q.title,q.score,q.verdict,q.current,q.next])];
const csv=rows.map(row=>row.map(x=>'"'+String(x).replaceAll('"','""')+'"').join(",")).join("\r\n");
const url=URL.createObjectURL(new Blob(["\ufeff"+csv],{type:"text/csv;charset=utf-8;"}));const a=el("a");a.href=url;a.download="CSP-S_复盘题目_"+DATA.snapshot+".csv";document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),2000)}
let lastFocus=null;
function openProblem(q){
const b=$("#detail-backdrop"),pane=$("#detail-drawer");lastFocus=document.activeElement;set("#detail-id",q.id+" / EVIDENCE FILE");set("#detail-title",q.title);set("#detail-score",q.score+"/100");set("#detail-verdict",q.verdict);set("#detail-system",contest(q));
set("#detail-process",q.contestProcess);set("#detail-current",q.current);set("#detail-next",q.next);set("#detail-source","题目总表："+q.evidence+" / "+q.review+"；当前评级为仓库分析，不是官方定级。");
const links=$("#detail-links");links.textContent="";
const a=node(links,"a","","查看比赛文件夹 ↗");a.href="https://github.com/sutong-claude/Day1/tree/chatgpt/oct7-stage-maintenance/"+q.path.split("/").map(encodeURIComponent).join("/");a.target="_blank";a.rel="noopener noreferrer";
const c=node(links,"a","","查看权威36题总表 ↗");c.href=repoPath("全题总表_2026-10-11.md");c.target="_blank";c.rel="noopener noreferrer";
b.hidden=false;document.body.classList.add("modal-open");pane.focus();history.replaceState(null,"","#"+q.id)}
function closeProblem(){const b=$("#detail-backdrop");if(b.hidden)return;b.hidden=true;document.body.classList.remove("modal-open");if(location.hash.startsWith("#D")||location.hash.startsWith("#CL-"))history.replaceState(null,"",location.pathname+location.search);if(lastFocus&&lastFocus.focus)lastFocus.focus();}
function setupDetail(){$("#detail-close").addEventListener("click",closeProblem);$("#detail-backdrop").addEventListener("click",e=>{if(e.target===$("#detail-backdrop"))closeProblem()});document.addEventListener("keydown",e=>{if(e.key==="Escape")closeProblem();if(!$("#detail-backdrop").hidden&&e.key==="Tab"){const f=$$('a,button,[tabindex="0"]',$("#detail-drawer")).filter(x=>!x.hasAttribute("disabled"));if(f.length){const first=f[0],last=f[f.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}}}})}
function renderStory(){
const nav=$("#story-nav");nav.textContent="";
DATA.events.forEach((e,i)=>{const b=node(nav,"button","story-tab");b.type="button";b.setAttribute("role","tab");b.setAttribute("aria-selected",String(i===state.event));node(b,"span","mini","DAY "+String(e.day).padStart(2,"0")+" · "+e.moment);node(b,"span","",e.title);b.addEventListener("click",()=>chooseEvent(i));});
$("#story-prev").addEventListener("click",()=>chooseEvent((state.event-1+DATA.events.length)%DATA.events.length));
$("#story-next").addEventListener("click",()=>chooseEvent((state.event+1)%DATA.events.length));
chooseEvent(state.event)}
function chooseEvent(i){state.event=i;const e=DATA.events[i];set("#story-index","EVENT "+String(i+1).padStart(2,"0")+" / "+DATA.events.length+"  ·  DAY "+e.day);set("#story-title",e.title);set("#story-copy",e.text);set("#story-state",e.status);set("#story-source","证据口径："+e.evidence);$$(".story-tab").forEach((b,j)=>{b.setAttribute("aria-selected",String(j===i));b.tabIndex=j===i?0:-1;});}
function renderTasks(){const list=$("#task-list");list.textContent="";DATA.tasks.forEach((t,i)=>{const card=node(list,"article","glass task-card");node(card,"span","seq",String(i+1).padStart(2,"0"));const info=node(card,"div","");node(info,"span","task-tag",t.priority+" / "+t.id);node(info,"h3","",t.name);node(info,"p","",t.detail);node(info,"p","", "证据限制："+t.evidence);})}
function initStars(){
const c=$("#stars");if(!c||window.matchMedia("(prefers-reduced-motion: reduce)").matches)return;const ctx=c.getContext("2d");if(!ctx)return;let pts=[],w=0,h=0,frame=0;
function resize(){const b=c.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2);w=b.width;h=b.height;c.width=Math.round(w*dpr);c.height=Math.round(h*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);pts=Array.from({length:Math.min(130,Math.round(w*h/12000))},(_,i)=>({x:(Math.sin(i*74.8+12.7)*42758.54%1+1)%1*w,y:(Math.sin(i*12.98+63.2)*15814.2%1+1)%1*h,r:i%7===0?1.6:.8,phase:i*.63}))}
resize();window.addEventListener("resize",resize,{passive:true});
let visible=true;document.addEventListener("visibilitychange",()=>visible=!document.hidden);
function draw(){requestAnimationFrame(draw);if(!visible)return;ctx.clearRect(0,0,w,h);frame++;for(const p of pts){const alpha=.18+.25*(1+Math.sin(frame*.009+p.phase))/2;ctx.fillStyle="rgba(155,219,245,"+alpha+")";ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();}}draw()}
function setupNav(){const links=$$(".topnav a");const obs=new IntersectionObserver(entries=>{for(const e of entries){if(e.isIntersecting){links.forEach(a=>a.classList.toggle("active",a.getAttribute("href")==="#"+e.target.id))}}},{rootMargin:"-23% 0px -65% 0px"});$$("section[id]").forEach(s=>obs.observe(s))}
function setupHash(){const id=decodeURIComponent(location.hash.slice(1));const q=problems.find(q=>q.id===id);if(q)openProblem(q)}
titleData();scoreChart();makeHeatmap();setupFilters();renderProblems();renderStory();renderTasks();setupDetail();initStars();setupNav();setupHash();
})();
