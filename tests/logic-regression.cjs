// Deterministic simulation with DOM/canvas stubs, NOT a browser/visual test.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
let now=1000;const pending=[];
const noop=()=>{};
const canvas=new Proxy({createLinearGradient:()=>({addColorStop:noop}),createRadialGradient:()=>({addColorStop:noop}),measureText:()=>({width:50})},{get:(o,k)=>k in o?o[k]:noop});
const el=()=>({style:{},appendChild:noop,className:'',classList:{add:noop,remove:noop,toggle:noop},getContext:()=>canvas,addEventListener:noop,querySelectorAll:()=>Array.from({length:8},el),textContent:'',offsetWidth:100});
const elements=new Map();const get=id=>{if(!elements.has(id))elements.set(id,el());return elements.get(id)};
const ctx={console,performance:{now:()=>now},requestAnimationFrame:noop,setInterval:()=>0,clearInterval:noop,setTimeout:(f,ms)=>pending.push({f,t:now+ms}),clearTimeout:noop,SpeechSynthesisUtterance:function(){},speechSynthesis:{speak:noop,cancel:noop},document:{getElementById:get,querySelector:get,querySelectorAll:()=>Array.from({length:8},el),addEventListener:noop}};
ctx.document.createElement=el;ctx.document.querySelectorAll=selector=>Array.from({length:selector.includes('core')?8:3},el);ctx.window=ctx;ctx.addEventListener=noop;vm.createContext(ctx);
const source=fs.readFileSync(process.argv[2]||'game.js','utf8');
vm.runInContext(source.replace('reset();requestAnimationFrame(loop);','window.probe=code=>eval(code);reset();'),ctx);
const p=code=>ctx.probe(code),key=(code,repeat=false)=>p(`keydown({code:'${code}',repeat:${repeat},preventDefault(){}})`),up=code=>p(`keyup({code:'${code}'})`);
const tick=ms=>{for(let t=0;t<ms;t+=16){now+=16;p('update(.016,performance.now());render(performance.now())');for(const x of pending.filter(x=>x.t<=now)){pending.splice(pending.indexOf(x),1);x.f()}}};
let checks=0;const eq=(code,value)=>{assert.deepEqual(JSON.parse(JSON.stringify(p(code))),value,code);checks++};
key('Space');tick(500);eq('progress',0);key('ArrowUp');tick(500);assert(p('progress')>50);up('ArrowUp');const stopped=p('progress');tick(500);eq('progress',stopped);
function fixture(d=100,lane=0){p(`state='run';branchPhase='none';keys={};swordAction=null;swordUntil=0;impactStop=0;recover=0;progress=400;laneIndex=0;lateral=targetLateral=0;playerHP=100;xp=0;xpNeed=60;upgradeQueue=[];minions=[{kind:'minion',at:400+${d},lane:${lane},done:false,defeated:false,style:0}];road=[]`)}
fixture();key('KeyA');tick(96);eq('minions[0].defeated',false);tick(80);eq('[minions[0].defeated,xp,playerHP]',[true,8,100]);tick(800);eq('[minions[0].done,xp]',[true,8]);
fixture(110,.58);eq('!!swordTarget()',true);key('KeyA');tick(176);eq('minions[0].defeated',true);
fixture(180,.58);eq('!!swordTarget()',false);fixture(260);key('KeyA');tick(500);eq('xp',0);
fixture(45);key('ArrowUp');tick(600);eq('[playerHP,xp,minions[0].done,minions[0].defeated]',[94,0,false,false]);tick(1500);eq('playerHP',94);up('ArrowUp');key('KeyA');tick(176);eq('[xp,playerHP]',[8,94]);
fixture(45);key('ArrowUp');tick(32);key('ArrowRight');tick(1600);up('ArrowUp');eq('[minions[0].done,minions[0].defeated,xp]',[true,false,0]);
fixture(45);p('playerHP=6');key('ArrowUp');tick(32);up('ArrowUp');eq('state','roadrecover');tick(950);eq('[state,playerHP]',['run',50]);
fixture(270,-.58);key('ArrowDown');eq('[state,forestBullets]',['forestgun',4]);
const frozen=p('progress');key('ArrowUp');tick(480);up('ArrowUp');eq('progress',frozen);
for(let i=0;i<4;i++){p('forestAimX=1100;forestAimY=200');key('Space')}eq('[state,forestBullets,xp,minions[0].defeated]',['forestgun',0,0,false]);
tick(900);eq('forestBullets',4);
p('forestAimX=project(minions[0].at,minions[0].lane,H*.43).x;forestAimY=project(minions[0].at,minions[0].lane,H*.43).y-28*project(minions[0].at,minions[0].lane,H*.43).scale');
key('Space');eq('[minions[0].defeated,xp,forestBullets,playerHP]',[true,8,3,100]);
key('Escape');eq('state','run');tick(900);eq('minions[0].done',true);
fixture(180,0);key('ArrowDown');key('ArrowRight');assert(p('forestAimX')>640);key('KeyA');eq('state','run');
// Rendering a forest road must never call the third-person runner; stage 2 still does.
p('let oldRunner=drawRunner;window.runnerCalls=0;drawRunner=()=>{window.runnerCalls++};render(performance.now());drawRunner=oldRunner');eq('window.runnerCalls',0);
p('stageIndex=1;let oldRunner=drawRunner;window.runnerCalls=0;drawRunner=()=>{window.runnerCalls++};render(performance.now());drawRunner=oldRunner');eq('window.runnerCalls',1);p('stageIndex=0');
for(const kind of ['rock','heal','core']){fixture();p(`minions=[];playerHP=60;cores=0;road=[{kind:'${kind}',at:405,lane:0,done:false}]`);key('ArrowUp');tick(32);up('ArrowUp');eq('road[0].done',true);if(kind==='heal')eq('playerHP',82);if(kind==='core')eq('cores',2)}
for(const choice of ['safe','risk']){p("loadStage(0);state='run';currentEncounter=1;minions=[];road=[];progress=stages[0].branchAt-11;branchPhase='approach'");key('ArrowUp');tick(100);up('ArrowUp');eq('branchPhase','choose');key(choice==='safe'?'ArrowLeft':'ArrowRight');key('Space');tick(1550);eq('[branchPhase,branchChosen,!!keys.ArrowUp]',['done',choice,false])}
fixture();p('xp=56');key('KeyA');tick(1000);eq('state','levelup');tick(2300);eq('state','run');
p("loadStage(0);state='run';minions=[];road=[];progress=encounters[0].at-1");key('ArrowUp');tick(32);up('ArrowUp');eq('[state,!!keys.ArrowUp]',['battle',false]);key('ArrowUp',true);eq('state','battle');
p('selected=options.indexOf(target)');key('Space');eq('[state,shotsLeft]',['aim',3]);p('aimX=315;aimY=500');key('Space');eq('[shotsLeft,enemyHP]',[2,100]);
for(let i=0;i<2;i++){p('aimX=aimingEnemyX(performance.now());aimY=H*.47');key('Space')}eq('state','shotresolve');tick(750);eq('state','enemyturn');
p('shieldX=orbTargetX;shieldY=orbTargetY');const hp=p('playerHP');tick(4000);eq('[guardSuccess,playerHP]',[true,hp]);tick(900);eq('state','battle');
p('startEnemyTurn();orbTargetX=825;orbTargetY=365;shieldX=365;shieldY=625');key('Space');tick(4000);eq('guardSuccess',false);assert(p('playerHP')<hp);tick(900);
p('selected=options.findIndex(x=>x!==target)');key('Space');eq('state','wrong');tick(2500);eq('state','enemyturn');
p("state='battle';resultLock=false;cores=8;enemyHP=100");key('ArrowUp');eq('state','special');key('ArrowLeft');key('ArrowLeft');key('Space');eq('cores',5);tick(4500);
p('reset();start()');
for(let s=0;s<10;s++){
 eq('stageIndex',s);assert(p('minions.length')>0);p('progress=minions[0].at-100;lateral=targetLateral=minions[0].lane;laneIndex=Math.round(lateral/.58)');key('KeyA');tick(900);assert(p('minions.some(m=>m.defeated)'));
 for(let e=0;e<3;e++){
  p("state='run';keys={};progress=encounters[currentEncounter].at;startBattle();selected=options.indexOf(target)");key('Space');p('enemyHP=1;aimX=aimingEnemyX(performance.now());aimY=H*.47');key('Space');tick(850);eq('state','victory');tick(1250);
  for(let n=0;n<12&&p("state==='levelup'");n++)tick(2300);
  if(e===2){if(s<3){eq('state','rescue');tick(2500)}if(s<9){eq('state','stageclear');tick(1900)}}
 }
}
eq('[state,companions.length]',['finish',3]);key('Enter');eq('[state,progress,!!keys.ArrowUp,swordAction]',['intro',0,false,null]);
// Root canvas renderer stays unchanged: no whole-screen camera offset.
assert(!/ctx\.translate\([^;]*Math\.random/.test(source));
console.log(`${checks} logic checks passed (DOM/canvas stubs; no visual claim).`);
