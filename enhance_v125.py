"""Apply the v12.5 road UX to the verified v12.4 generated assets.

Base chunks and the v12.4 upgrade remain unchanged. Run only after v12.4.
"""
from pathlib import Path

path = Path('game.js')
js = path.read_text()

def replace(old, new):
    global js
    assert js.count(old) == 1, ('v12.5 replacement mismatch', js.count(old), old[:100])
    js = js.replace(old, new)

replace('const AIM_BOUNDS=', '''// Road input and combat are isolated from letter / aiming / guard states.
let swordAction=null,roadHurtUntil=0;
const ROAD_COMBAT={reach:220,assistReach:130,laneReach:.34,assistLane:.66,contact:42,swing:460,impact:145,defeat:760};
const runStatus=$("run-status");
const AIM_BOUNDS=''')
replace('progress=0;currentEncounter=0;', 'progress=0;currentEncounter=0;keys={};swordAction=null;swordUntil=0;roadHurtUntil=0;')
replace('branchShown=true;branchPhase="choose";', 'branchShown=true;branchPhase="choose";keys={};')
replace('branchPhase="done";branchCamera=0;', 'branchPhase="done";branchCamera=0;keys={};')
replace('started=true;state="run";', 'started=true;keys={};state="run";')
replace('msg("KEEP RUNNING!")', 'keys={};msg("↑  LET’S GO!")')
replace('warning=currentEncounter;state="bossintro";', 'warning=currentEncounter;keys={};state="bossintro";')
replace('function startBattle(){const e=currentEnemy();', 'function startBattle(){swordAction=null;swordUntil=0;const e=currentEnemy();')

start=js.index('function swingSword(){')
end=js.index('function drawMinion(', start)
js=js[:start]+'''function swordTarget(){
  if(state!=="run"||branchPhase==="choose"||branchPhase==="turn")return null;
  // Prefer the lane Kosuke chose. Adjacent-lane assistance only works close up.
  return minions.filter(m=>{
    const dz=m.at-progress,side=Math.abs(lateral-m.lane);
    return !m.done&&!m.defeated&&dz>=-8&&
      ((dz<=ROAD_COMBAT.reach&&side<=ROAD_COMBAT.laneReach)||
       (dz<=ROAD_COMBAT.assistReach&&side<=ROAD_COMBAT.assistLane));
  }).sort((a,b)=>(Math.abs(lateral-a.lane)*280+a.at)-(Math.abs(lateral-b.lane)*280+b.at))[0]||null;
}
function swingSword(){
  if(state!=="run"||branchPhase==="choose"||branchPhase==="turn")return;
  const now=performance.now();if(now<swordUntil)return;
  const target=swordTarget();
  swordUntil=now+ROAD_COMBAT.swing;swordConnected=false;
  const p=target?project(target.at,target.lane,H*.43):null;
  swordAction={start:now,target,hit:false,x:p?p.x:W/2+lateral*300,y:p?p.y-34*p.scale:H*.66};
  tone(310,.10,"triangle",.022);
}
function updateRoadCombat(now){
  if(swordAction&&!swordAction.hit&&now-swordAction.start>=ROAD_COMBAT.impact){
    swordAction.hit=true;
    const m=swordAction.target;
    if(m&&!m.done&&!m.defeated){
      m.defeated=true;m.defeatAt=now;swordConnected=true;impactStop=.065;
      spawnBurst(swordAction.x,swordAction.y,12);
      gainXP(8);msg("+8 XP  ·  GREAT HIT!",true);
      tone(680,.08,"triangle",.038);tone(1040,.14,"sine",.026,.065);
    }
  }
  for(const m of minions){
    if(m.defeated&&now-m.defeatAt>=ROAD_COMBAT.defeat)m.done=true;
    // A living enemy only leaves the view after Kosuke deliberately passes in another lane.
    if(!m.defeated&&m.at-progress<-65)m.done=true;
  }
  if(swordAction&&now>=swordUntil)swordAction=null;
}
function roadLunge(now){
  if(!swordAction)return {x:0,y:0};
  const t=Math.max(0,Math.min(1,(now-swordAction.start)/ROAD_COMBAT.swing));
  const amount=t<.32?Math.sin(t/.32*Math.PI/2):Math.pow((1-t)/.68,2);
  return {x:(swordAction.x-(W/2+lateral*300))*.24*amount,y:-40*amount};
}
function drawSword(now){
  if(!swordAction||now>swordUntil)return;
  const t=(now-swordAction.start)/ROAD_COMBAT.swing,lunge=roadLunge(now);
  const x=W/2+lateral*300+lunge.x+19,y=H*.91-43+lunge.y;
  const dx=swordAction.x-x,dy=swordAction.y-y,angle=Math.atan2(dy,dx);
  const extension=t<.32?Math.sin(t/.32*Math.PI/2):Math.max(.24,1-(t-.32)/.68);
  const length=Math.max(52,Math.hypot(dx,dy)*extension),sweep=(.32-t)*.9;
  ctx.save();ctx.translate(x,y);ctx.rotate(angle+sweep);
  // The blade travels from Kosuke's hand to the selected enemy, not around his body.
  ctx.strokeStyle=swordConnected?"#fff1a0":"#c9f6ff";ctx.lineWidth=5;
  ctx.shadowColor="#b5efff";ctx.shadowBlur=9;
  ctx.fillStyle="#edfaff";ctx.beginPath();ctx.moveTo(8,-9);ctx.lineTo(length-12,-5);
  ctx.lineTo(length+8,0);ctx.lineTo(length-12,6);ctx.lineTo(8,9);ctx.closePath();ctx.fill();ctx.stroke();
  ctx.shadowBlur=0;ctx.strokeStyle="#efbd54";ctx.lineWidth=9;ctx.beginPath();ctx.moveTo(7,-19);ctx.lineTo(7,19);ctx.stroke();
  ctx.strokeStyle="#69503d";ctx.beginPath();ctx.moveTo(-17,0);ctx.lineTo(4,0);ctx.stroke();ctx.restore();
}
function drawAttackCue(p){
  ctx.save();ctx.strokeStyle="#d5ff9a";ctx.lineWidth=3;ctx.shadowColor="#c9ff8e";ctx.shadowBlur=10;
  ctx.beginPath();ctx.ellipse(p.x,p.y+5,48*p.scale,13*p.scale,0,0,Math.PI*2);ctx.stroke();
  const y=p.y-94*p.scale;
  ctx.shadowBlur=0;ctx.fillStyle="#efffcf";ctx.beginPath();ctx.roundRect(p.x-23,y-20,46,40,12);ctx.fill();
  ctx.fillStyle="#294333";ctx.font="900 27px Arial";ctx.textAlign="center";ctx.fillText("A",p.x,y+9);ctx.restore();
}
''' + js[end:]
replace('ctx.save();ctx.translate(p.x,p.y+Math.sin(now/270+monster.at)*3);ctx.scale(p.scale*.54,p.scale*.54);', '''const dead=monster.defeated,age=dead?Math.min(1,(now-monster.defeatAt)/ROAD_COMBAT.defeat):0;
  if(!dead&&swordTarget()===monster&&!swordAction)drawAttackCue(p);
  ctx.save();
  if(dead){
    ctx.save();ctx.globalAlpha=1-age;ctx.fillStyle="#efffcf";ctx.font="900 27px Arial";ctx.textAlign="center";
    ctx.fillText("+8 XP",p.x,p.y-95-age*75);ctx.restore();
    ctx.globalAlpha=Math.max(0,1-Math.max(0,age-.35)/.65);
  }
  const recoil=dead?Math.sin(Math.min(1,age*1.6)*Math.PI/2):0;
  ctx.translate(p.x+recoil*(monster.lane>=0?36:-36),p.y+Math.sin(now/270+monster.at)*3-recoil*85);
  if(dead)ctx.rotate((monster.lane>=0?1:-1)*age*1.1);
  if(dead&&age<.16){ctx.shadowColor="#fff4a8";ctx.shadowBlur=16}
  ctx.scale(p.scale*.54*(1-age*.25),p.scale*.54*(1-age*.25));''')
replace('if(o.done)continue;if(o.route && !branchChosen)continue;const p=project(o.at,o.lane,hz);', 'if(o.done)continue;if(o.route && !branchChosen)continue;const p=project(o.at,o.lane,hz);')
replace('function drawRunner(now){const x=W/2+lateral*300,y=H*.91,bob=', 'function drawRunner(now){const lunge=roadLunge(now),x=W/2+lateral*300+lunge.x,y=H*.91+lunge.y,bob=')
replace('ctx.translate(x,y+bob);ctx.shadowColor=', '''ctx.translate(x,y+bob);
if(now<roadHurtUntil){ctx.save();ctx.strokeStyle="#ff9c84";ctx.lineWidth=4;ctx.globalAlpha=Math.min(1,(roadHurtUntil-now)/300);ctx.beginPath();ctx.ellipse(0,-35,51,76,0,0,7);ctx.stroke();ctx.restore()}
ctx.shadowColor=''')

replace('function update(dt,now){if(state==="run"){let mult=1;', '''function update(dt,now){
if(state==="run")updateRoadCombat(now);
$("game-shell").classList.toggle("road-mode",state==="run"||state==="bossintro"||state==="roadrecover");
runStatus.textContent=state==="run"?(branchPhase==="choose"?"← →  ·  SPACE":branchPhase==="turn"?"↗":swordTarget()?"A  ⚔":keys.ArrowUp?"↑  EXPLORING":"↑  HOLD TO WALK"):"";
if(state==="roadrecover"&&now-eventStart>=900){playerHP=50;updateHUD();state="run";keys={};msg("↑  TRY AGAIN!",true)}
if(state==="run"){let mult=keys.ArrowUp?1:0;''')
replace('mult=.25+r*.75;', 'mult*=.25+r*.75;')
replace('progress+=(runSpeed+Math.min(36,progress/180))*mult*dt;', '''if(swordAction)mult=0;
      const nextProgress=progress+(runSpeed+Math.min(24,progress/220))*mult*dt;
      const blocking=minions.filter(m=>!m.done&&!m.defeated&&m.at-progress>=-8&&Math.abs(lateral-m.lane)<.28&&nextProgress>=m.at-ROAD_COMBAT.contact).sort((a,b)=>a.at-b.at)[0];
      progress=blocking?Math.max(progress,Math.min(nextProgress,blocking.at-ROAD_COMBAT.contact)):nextProgress;
      if(blocking&&mult>0&&!blocking.bumped){
        blocking.bumped=true;playerHP=Math.max(0,playerHP-6);impactStop=.20;roadHurtUntil=now+650;
        updateHUD();msg("OUCH! −6 HP  ·  A ⚔ / ← →");tone(170,.11,"triangle",.026);
        if(playerHP===0){state="roadrecover";eventStart=now;keys={};msg("TAKE A BREATH ❤",true)}
      }''')
old='''      for(const m of minions){
        if(m.done)continue;
        if(m.at-progress<-24){m.done=true;
          if(Math.abs(lateral-m.lane)<.26){playerHP=Math.max(0,playerHP-6);updateHUD();msg("MINI MONSTER! -6 HP");tone(175,.12,"square",.022)}
        }
      }'''
replace(old, '''      for(const m of minions){
        // No repeated damage while resting against an enemy. Sidestepping re-arms contact.
        if(Math.abs(lateral-m.lane)>.42)m.bumped=false;
      }
      if(upgradeQueue.length&&!swordAction&&!minions.some(m=>m.defeated&&!m.done)){keys={};showUpgrade();return}''')

# Up is exclusively forward on the road. Clear held keys at transitions, and ignore OS repeats
# as new commands so an Up held during an encounter cannot accidentally open SPECIAL.
replace('if(state==="shotresolve")return;', 'if(state==="shotresolve")return;')
replace('if(c==="ArrowLeft"||c==="KeyA"){branchSelection=', 'if(c==="ArrowLeft"){branchSelection=')
replace('else if(c==="ArrowRight"||c==="KeyD"){branchSelection=', 'else if(c==="ArrowRight"){branchSelection=')
replace('      if(c==="KeyA"){swingSword();return}', '      if(c==="ArrowUp"){keys.ArrowUp=true;return}\n      if(c==="KeyA"){swingSword();return}')
replace('}else if(c==="ArrowRight"||c==="KeyD"){', '}else if(c==="ArrowRight"){')
replace('window.addEventListener("blur",()=>keys={});', 'window.addEventListener("blur",()=>keys={});document.addEventListener("visibilitychange",()=>{if(document.hidden)keys={}});')
path.write_text(js)
css = Path('style.css')
css.write_text(css.read_text() + '''
/* v12.5: a quiet road HUD and large visual keyboard cues. Battle layouts stay intact. */
#game-shell.road-mode #top-ui{grid-template-columns:1fr 240px}
#game-shell.road-mode #player-hud{grid-column:2;width:240px;padding:8px}
#game-shell.road-mode .gear{display:none}
#game-shell.road-mode #special-hud{padding:5px;margin-top:5px}
#game-shell.road-mode #special-ready{display:none}
#game-shell.road-mode #message{font-size:clamp(20px,3vw,38px);top:26%;max-width:94%;white-space:normal;text-align:center}
#run-status:empty{display:none}
#game-shell.road-mode #run-status{display:block;width:fit-content;font-size:15px;padding:7px 13px}
#road-tip{display:flex;align-items:center;gap:18px;padding:8px 18px;background:rgba(7,25,25,.85);border:1px solid #ffffff30;color:#e6f5e6;font-size:13px;white-space:nowrap;bottom:8px}
#road-tip span{display:flex;align-items:center;gap:7px}
#road-tip kbd,.controls kbd{display:inline-block;min-width:30px;padding:3px 7px;border-radius:7px;background:#f1ffe3;color:#23442f;font:bold 23px Arial;box-shadow:0 3px 0 #91b49c;text-align:center}
.controls span{font-size:14px;display:flex;align-items:center;gap:8px}
''')
print('v12.5 manual adventure applied')
