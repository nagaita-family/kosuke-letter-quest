"""GREEN FOREST first-person vertical slice on top of the verified v12.5 build."""
from pathlib import Path

p=Path('game.js'); js=p.read_text()
def replace(old,new):
    global js
    assert js.count(old)==1, ('v12.6 replacement mismatch',js.count(old),old[:90])
    js=js.replace(old,new)

replace('const AIM_BOUNDS=', '''// This prototype is intentionally restricted to GREEN FOREST.
const forestView=()=>stageIndex===0;
// Translating sideways shifts nearby geometry more than the far horizon.
// A little foreground travel makes the lane change legible without sliding off screen.
const FOREST_PARALLAX=.78;
const forestTravel=()=>forestView()&&(state==="run"||state==="forestgun")?lateral*FOREST_PARALLAX:0;
const forestPlayerX=()=>W*.5+lateral*390*(1-FOREST_PARALLAX);
const forestWorldShift=y=>forestTravel()*(35+355*Math.max(0,(y-H*.43)/(H-H*.43)));
const forestGunUI=$("forest-gun-ui"),forestAmmo=$("forest-ammo"),forestGunMessage=$("forest-gun-message");
let forestAimX=W*.5,forestAimY=H*.60,forestBullets=4,forestReloadUntil=0;
let forestShotAt=0,forestShotHit=false,forestShotX=0,forestShotY=0;
const FOREST_GUN={capacity:4,reach:650,reload:850};
function updateForestGunHUD(now=performance.now()){
  forestAmmo.textContent="● ".repeat(forestBullets).trim()||"○ ○ ○ ○";
  forestGunMessage.textContent=now<forestReloadUntil?"RELOADING...":
    forestBullets?"← ↑ ↓ → AIM · SPACE FIRE · ESC HOLSTER":"RELOADING...";
  forestGunUI.classList.toggle("hidden",state!=="forestgun");
}
function enterForestGun(){
  if(!forestView()||state!=="run"||branchPhase==="choose"||branchPhase==="turn"||swordAction)return;
  state="forestgun";keys={};forestAimX=forestPlayerX();forestAimY=H*.59;
  forestShotAt=0;updateForestGunHUD();msg("AIM & SHOOT!");tone(450,.09,"triangle",.024);
}
function leaveForestGun(){if(state!=="forestgun")return;state="run";keys={};forestGunUI.classList.add("hidden");msg("↑ WALK · A SWORD")}
function forestGunTarget(){
  return minions.filter(m=>!m.done&&!m.defeated&&m.at-progress>=55&&m.at-progress<=FOREST_GUN.reach)
    .map(m=>({m,p:project(m.at,m.lane,H*.43)}))
    .filter(v=>v.p)
    .sort((a,b)=>Math.hypot(forestAimX-a.p.x,forestAimY-(a.p.y-28*a.p.scale))-
                 Math.hypot(forestAimX-b.p.x,forestAimY-(b.p.y-28*b.p.scale)))[0]||null;
}
function aimForestGun(dx,dy){
  forestAimX=Math.max(155,Math.min(W-155,forestAimX+dx));
  forestAimY=Math.max(200,Math.min(H-135,forestAimY+dy));
}
function fireForestGun(){
  if(state!=="forestgun"||forestReloadUntil||forestBullets===0)return;
  const now=performance.now(),v=forestGunTarget();
  const near=v&&Math.hypot(forestAimX-v.p.x,forestAimY-(v.p.y-28*v.p.scale))<Math.max(80,51*v.p.scale);
  forestShotAt=now;forestShotHit=!!near;forestShotX=near?v.p.x:forestAimX;forestShotY=near?v.p.y-28*v.p.scale:forestAimY;
  forestBullets--;tone(near?720:285,.10,near?"triangle":"square",.038);
  if(near){
    const m=v.m;m.defeated=true;m.defeatAt=now;spawnBurst(forestShotX,forestShotY,16);
    gainXP(8);msg("HIT! +8 XP",true);
  }else msg("MISS! TRY AGAIN");
  if(forestBullets===0){forestReloadUntil=now+FOREST_GUN.reload;tone(360,.1,"triangle",.025,.16)}
  updateForestGunHUD(now);
}
function updateForestGun(dt,now){
  // Stopping to aim prevents the child being rushed by incoming scenery.
  if(keys.ArrowLeft)aimForestGun(-340*dt,0);
  if(keys.ArrowRight)aimForestGun(340*dt,0);
  if(keys.ArrowUp)aimForestGun(0,-320*dt);
  if(keys.ArrowDown)aimForestGun(0,320*dt);
  if(forestReloadUntil&&now>=forestReloadUntil){forestReloadUntil=0;forestBullets=FOREST_GUN.capacity;
    tone(650,.09,"sine",.027);updateForestGunHUD(now)}
  updateRoadCombat(now);updateForestGunHUD(now);
}
function drawForestHands(now){
  const armed=state==="forestgun",swing=swordAction&&state==="run";
  const t=swing?Math.min(1,(now-swordAction.start)/ROAD_COMBAT.swing):0;
  const bob=state==="run"&&keys.ArrowUp?Math.sin(progress*.11)*4:0;
  ctx.save();
  // Ground contact and the held weapon move a little as the world shifts around them.
  ctx.fillStyle="rgba(12,37,32,.38)";ctx.beginPath();ctx.ellipse(forestPlayerX(),H*.975,62,12,0,0,7);ctx.fill();
  // Foreground weapon movement only; never translate or rotate the viewport.
  if(armed){
    const reload=forestReloadUntil>now,phase=reload?(forestReloadUntil-now)/FOREST_GUN.reload:0;
    const kick=now-forestShotAt<135?(1-(now-forestShotAt)/135)*22:0;
    ctx.translate(forestPlayerX()+W*.22,H*.87+phase*75+kick);ctx.rotate(reload?.37*phase:-.13);
    ctx.fillStyle="#d9ac85";ctx.beginPath();ctx.roundRect(-22,5,36,65,15);ctx.fill();
    ctx.fillStyle="#213d59";ctx.beginPath();ctx.roundRect(-70,-18,175,51,14);ctx.fill();
    ctx.fillStyle="#87e8f6";ctx.fillRect(-38,-13,103,10);
    ctx.fillStyle="#ebd574";ctx.beginPath();ctx.roundRect(-15,30,29,63,6);ctx.fill();
    ctx.strokeStyle="#e4f8ff";ctx.lineWidth=5;ctx.strokeRect(-70,-18,175,51);
    if(reload){ctx.fillStyle="#b8d5e2";ctx.fillRect(-13,32,25,50+phase*28)}
    if(now-forestShotAt<155){ctx.fillStyle="#fff0a1";ctx.beginPath();ctx.arc(-54,-5,20,0,7);ctx.fill()}
  }else{
    const strike=swing?Math.sin(Math.min(1,t/.7)*Math.PI):0;
    const handX=forestPlayerX()+W*.18+bob-(swing?20*strike:0),handY=H*.88+bob-(swing?25*strike:0);
    const targetAngle=swing?Math.atan2(swordAction.y-handY,swordAction.x-handX)+Math.PI/2:-.23;
    const reach=swing?Math.min(255,Math.max(0,Math.hypot(swordAction.x-handX,swordAction.y-handY)-300))*strike:0;
    ctx.translate(handX,handY);
    ctx.rotate(-.23+(targetAngle+.23)*strike);
    ctx.fillStyle="#d9ac85";ctx.beginPath();ctx.roundRect(-13,9,34,85,14);ctx.fill();
    ctx.fillStyle="#88674b";ctx.beginPath();ctx.roundRect(-23,-25,43,57,11);ctx.fill();
    ctx.fillStyle="#d9f8ff";ctx.beginPath();ctx.moveTo(-16,-25);ctx.lineTo(-25,-240-reach);ctx.lineTo(0,-295-reach);ctx.lineTo(14,-25);ctx.closePath();ctx.fill();
    ctx.strokeStyle="#7dcaff";ctx.lineWidth=5;ctx.stroke();
    if(swing){ctx.strokeStyle="#fff6af";ctx.lineWidth=8;ctx.shadowColor="#ffffbd";ctx.shadowBlur=14;
      ctx.beginPath();ctx.moveTo(-95,-210-reach*.6);ctx.quadraticCurveTo(20,-335-reach,195,-290-reach*.4);ctx.stroke()}
  }
  ctx.restore();
}
function drawForestGunAim(now){
  const v=forestGunTarget(),locked=v&&Math.hypot(forestAimX-v.p.x,forestAimY-(v.p.y-28*v.p.scale))<Math.max(80,51*v.p.scale);
  ctx.save();ctx.translate(forestAimX,forestAimY);ctx.strokeStyle=locked?"#d3ff86":"#e1faff";ctx.lineWidth=4;
  ctx.shadowColor=ctx.strokeStyle;ctx.shadowBlur=10;ctx.beginPath();ctx.arc(0,0,29,0,7);
  ctx.moveTo(-49,0);ctx.lineTo(-13,0);ctx.moveTo(13,0);ctx.lineTo(49,0);
  ctx.moveTo(0,-49);ctx.lineTo(0,-13);ctx.moveTo(0,13);ctx.lineTo(0,49);ctx.stroke();ctx.restore();
  if(now-forestShotAt<225){ctx.save();ctx.strokeStyle=forestShotHit?"#fdfaa0":"#a7dbff";
    ctx.lineWidth=6*(1-(now-forestShotAt)/225);ctx.beginPath();ctx.moveTo(forestPlayerX()+W*.17,H*.80);
    ctx.lineTo(forestShotX,forestShotY);ctx.stroke();ctx.restore()}
}
const AIM_BOUNDS=''' )

# Per-stage reset and transitions must never leave a modal weapon active.
replace('progress=0;currentEncounter=0;keys={};swordAction=null;', 'progress=0;currentEncounter=0;forestBullets=FOREST_GUN.capacity;forestReloadUntil=0;forestShotAt=0;forestGunUI.classList.add("hidden");keys={};swordAction=null;')
replace('function startBattle(){swordAction=null;', 'function startBattle(){forestGunUI.classList.add("hidden");swordAction=null;')
replace('ctx.save();ctx.translate(turnShift,0);', '''ctx.save();ctx.translate(turnShift,0);
  if(forestTravel()){
    const slope=-forestTravel()*355/(H-hz);
    ctx.transform(1,0,slope,1,forestTravel()*355*hz/(H-hz)-forestTravel()*35,0);
  }''')
replace('  drawScenery(hz,now);drawRouteFork(hz);drawRoadObjects(hz,now);drawRunner(now);if(state==="run")drawSword(now);ctx.restore();',
'''  ctx.restore();ctx.save();ctx.translate(turnShift,0);
  drawScenery(hz,now);drawRouteFork(hz);drawRoadObjects(hz,now);
  if(!forestView())drawRunner(now);
  if(state==="run"&&!forestView())drawSword(now);ctx.restore();''')
replace('x=W/2+lane*half,scale=', 'x=W/2+lane*half-forestWorldShift(y),scale=')
replace('x:p?p.x:W/2+lateral*300,y:p?', 'x:p?p.x:(forestView()?forestPlayerX():W/2+lateral*300),y:p?')
replace('ctx.save();ctx.translate(x,y);\n  let animScale=1;', 'ctx.save();ctx.translate(x-forestWorldShift(y),y);\n  let animScale=1;')
replace('if(!dead&&swordTarget()===monster&&!swordAction)drawAttackCue(p);', 'if(!dead&&state==="run"&&swordTarget()===monster&&!swordAction)drawAttackCue(p);')
replace('if(state==="run")updateRoadCombat(now);', 'if(state==="run")updateRoadCombat(now);\nif(state==="forestgun")updateForestGun(dt,now);')
replace('runStatus.textContent=state==="run"?', '''$("game-shell").classList.toggle("road-mode",state==="forestgun"||state==="run"||state==="bossintro"||state==="roadrecover");
$("game-shell").classList.toggle("forest-gun",state==="forestgun");
runStatus.textContent=state==="forestgun"?"↓ GUN · SPACE FIRE":state==="run"?''')
replace('if(state==="shotresolve")return;', '''if(state==="forestgun"){
  if(c==="Escape"||c==="KeyA"||(c==="ArrowDown"&&!e.repeat&&!keys.ArrowDown)){
    if(c!=="ArrowDown"||forestAimY>H-160){leaveForestGun();return}
  }
  if(c==="Space"&&!e.repeat)fireForestGun();
  else if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].includes(c)){
    keys[c]=true;
    if(!e.repeat)aimForestGun(c==="ArrowLeft"?-36:c==="ArrowRight"?36:0,c==="ArrowUp"?-36:c==="ArrowDown"?36:0);
  }
  return;
}
if(state==="shotresolve")return;''')
# ↓ first arms; Escape or A holsters. ↓ remains an aiming direction, so it does not also holster.
replace('if(c==="Escape"||c==="KeyA"||(c==="ArrowDown"&&!e.repeat&&!keys.ArrowDown)){\n    if(c!=="ArrowDown"||forestAimY>H-160){leaveForestGun();return}\n  }',
        'if(c==="Escape"||c==="KeyA"){leaveForestGun();return}')
replace('      if(c==="ArrowUp"){keys.ArrowUp=true;return}', '      if(c==="ArrowDown"&&forestView()){enterForestGun();return}\n      if(c==="ArrowUp"){keys.ArrowUp=true;return}')
replace('function render(now){ctx.save();ctx.clearRect(0,0,W,H);drawWorld(now);', 'function render(now){ctx.save();ctx.clearRect(0,0,W,H);drawWorld(now);')
replace('if(state==="aim"||state==="shotresolve")drawAim(now);',
'''if(state==="aim"||state==="shotresolve")drawAim(now);
if(forestView()&&(state==="run"||state==="forestgun"||state==="bossintro"||state==="battle"||state==="enemyturn"||state==="enemyresolve")){
  drawForestHands(now);if(state==="forestgun")drawForestGunAim(now);
}''')
# Don't render an old big encounter in front of the held weapon while aiming at a small monster.
replace('if((state==="run"||state==="bossintro")&&dist<680)', 'if((state==="run"||state==="bossintro"||state==="forestgun")&&dist<680)')
replace('const hz=H*.43,n=1-Math.min(1,dist/680),s=state==="run"?', 'const hz=H*.43,n=1-Math.min(1,dist/680),s=(state==="run"||state==="forestgun")?')
replace('y=state==="run"?hz+n*85:H*.47;', 'y=(state==="run"||state==="forestgun")?hz+n*85:H*.47;')
p.write_text(js)
css=Path('style.css');css.write_text(css.read_text()+'''
/* GREEN FOREST only: pause-and-aim gun mode. Keep targets unobscured. */
#forest-gun-ui{position:absolute;left:50%;top:22%;transform:translateX(-50%);z-index:24;
  text-align:center;pointer-events:none;color:#fff;font-weight:1000;text-shadow:0 2px 8px #11272a}
#forest-gun-ui #forest-ammo{color:#f5eea6;font-size:36px;letter-spacing:8px}
#forest-gun-ui #forest-ammo{line-height:1.3;margin-bottom:18px}
#forest-gun-message{display:block;border-radius:99px;background:rgba(3,23,29,.75);padding:9px 20px;font-size:17px;white-space:nowrap}
#game-shell.forest-gun #road-tip{display:none}
''')
print('v12.6 forest first-person assets built')
