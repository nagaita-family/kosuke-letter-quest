// Run against a locally reconstructed build. Probe exists only in this intercepted test response.
// NODE_PATH=<directory containing playwright> node tests/road-regression.cjs http://127.0.0.1:8765
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const base = process.argv[2] || 'http://127.0.0.1:8765';
(async () => {
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage({viewport:{width:1280,height:720}});
  const errors=[];
  await page.route('**/favicon.ico',route=>route.fulfill({status:204,body:''}));
  page.on('pageerror', e=>errors.push(e.message));
  page.on('console', m=>{if(m.type()==='error')errors.push(m.text())});
  await page.addInitScript(()=>{
    window.__now=1000;
    Object.defineProperty(performance,'now',{value:()=>window.__now});
    window.requestAnimationFrame=()=>0;
  });
  await page.route('**/game.js',async route=>{
    const response=await route.fetch();
    const source=await response.text();
    assert(source.includes('reset();requestAnimationFrame(loop);'));
    await route.fulfill({response,body:source.replace('reset();requestAnimationFrame(loop);','window.__probe = code => eval(code); reset();requestAnimationFrame(loop);')});
  });
  await page.goto(base);
  const probe = code=>page.evaluate(code=>window.__probe(code),code);
  const step = ms=>probe(`(()=>{for(let n=0;n<${ms};n+=16){window.__now+=16;update(.016,performance.now())}render(performance.now())})()`);
  const check = async (code,expected,label)=>{assert.deepEqual(await probe(code),expected,label);console.log('PASS',label)};
  const key = code=>page.keyboard.press(code);
  await key('Space');await step(700);
  await check('progress',0,'road waits for forward input');
  await page.keyboard.down('ArrowUp');await step(500);
  assert(await probe('progress')>50);
  await page.keyboard.up('ArrowUp');const stopped=await probe('progress');await step(500);
  await check('progress',stopped,'release immediately stops');
  await key('ArrowLeft');await step(300);await check('laneIndex',-1,'left lane');
  await check('forestCameraX() < -160 && forestCameraX() >= -174',true,'forest view follows left movement');
  await check('Math.round(project(progress+150,0,H*.43).x-forestCameraX())>W/2',true,'center lane moves right on screen');
  await key('ArrowRight');await step(300);await check('laneIndex',0,'right lane');
  await check('Math.abs(forestCameraX()) < 5',true,'forest view returns to center');
  await page.keyboard.down('ArrowUp');await page.evaluate(()=>window.dispatchEvent(new Event('blur')));
  await step(500);await check('progress',stopped,'focus loss clears forward input');await page.keyboard.up('ArrowUp');

  const fixture=async (distance=100,lane=0)=>probe(`state='run';branchPhase='none';keys={};swordAction=null;swordUntil=0;impactStop=0;recover=0;progress=400;laneIndex=0;lateral=targetLateral=0;playerHP=100;xp=0;xpNeed=60;upgradeQueue=[];minions=[{kind:'minion',at:400+${distance},lane:${lane},done:false,defeated:false,style:0}];road=[];`);
  await fixture();await key('KeyA');await step(96);
  await check('minions[0].defeated',false,'wind-up precedes impact');
  await step(80);await check('[minions[0].defeated,xp,playerHP]',[true,8,100],'sword impact awards XP without HP loss');
  await check('minions[0].done',false,'defeated enemy remains visible for recoil');
  await key('KeyA');await step(800);await check('[minions[0].done,xp]',[true,8],'single reward and completed defeat animation');

  await fixture(110,.58);await check('!!swordTarget()',true,'near adjacent lane assisted');
  await key('KeyA');await step(176);await check('minions[0].defeated',true,'assisted attack hits');
  await fixture(180,.58);await check('!!swordTarget()',false,'distant adjacent lane not auto-hit');
  await fixture(260,0);await key('KeyA');await step(500);await check('xp',0,'out-of-range swing does not grant XP');

  await fixture(45);await page.keyboard.down('ArrowUp');await step(600);
  await check('[playerHP,xp,minions[0].defeated,minions[0].done]',[94,0,false,false],'contact hurts but enemy stays alive');
  assert(await probe('minions[0].at-progress')>=42);
  await step(1500);await check('playerHP',94,'contact does not repeatedly drain stationary player');
  await page.keyboard.up('ArrowUp');await key('KeyA');await step(176);
  await check('[minions[0].defeated,xp,playerHP]',[true,8,94],'enemy can be defeated after a bump');
  await fixture(45);await page.keyboard.down('ArrowUp');await step(32);await key('ArrowRight');await step(1600);await page.keyboard.up('ArrowUp');
  await check('[minions[0].done,minions[0].defeated,xp]',[true,false,0],'sidestep and pass is not a defeat');
  await fixture(45);await probe('playerHP=6');await page.keyboard.down('ArrowUp');await step(32);await page.keyboard.up('ArrowUp');
  await check('state','roadrecover','zero HP enters short road recovery');await step(950);
  await check('[state,playerHP,!!keys.ArrowUp]', ['run',50,false],'road recovery resumes safely');

  await fixture(270,-.58);await key('ArrowDown');await check('[state,forestBullets]',['forestgun',4],'Green Forest first-person gun draws');
  const gunStop=await probe('progress');await page.keyboard.down('ArrowUp');await step(480);await page.keyboard.up('ArrowUp');
  await check('progress',gunStop,'gun aiming pauses travel');
  for(let i=0;i<4;i++){await probe('forestAimX=1100;forestAimY=200');await key('Space')}
  await check('[forestBullets,xp,minions[0].defeated]',[0,0,false],'four misses consume only ammunition');
  await check('forestGunMessage.textContent','RELOADING...','visible automatic reload');
  await step(900);await check('forestBullets',4,'reload restores bullets');
  await probe('let p=project(minions[0].at,minions[0].lane,H*.43);forestAimX=p.x;forestAimY=p.y-28*p.scale');
  await key('Space');await check('[minions[0].defeated,xp,forestBullets,playerHP]',[true,8,3,100],'aimed gun hit defeats enemy');
  await key('Escape');await check('state','run','holster returns to walking');

  for(const kind of ['rock','heal','core']){
    await fixture();await probe(`minions=[];playerHP=60;cores=0;road=[{kind:'${kind}',at:405,lane:0,done:false}]`);
    await page.keyboard.down('ArrowUp');await step(32);await page.keyboard.up('ArrowUp');
    await check('road[0].done',true,kind+' collected / collided');
    if(kind==='heal')await check('playerHP',82,'healing amount');
    if(kind==='core')await check('cores',2,'core amount');
    if(kind==='rock')assert(await probe('impactStop')>0);
  }
  for(const choice of ['safe','risk']){
    await probe("loadStage(0);state='run';currentEncounter=1;minions=[];road=[];progress=stages[0].branchAt-11;branchPhase='approach';");
    await page.keyboard.down('ArrowUp');await step(100);await page.keyboard.up('ArrowUp');
    await check('branchPhase','choose','route fork reached '+choice);
    await key(choice==='safe'?'ArrowLeft':'ArrowRight');await key('Space');await step(1550);
    await check('[branchPhase,branchChosen,!!keys.ArrowUp]',['done',choice,false],'route turn and stopped exit '+choice);
  }
  await fixture();await probe('xp=56');await key('KeyA');await step(1000);
  await check('state','levelup','road XP triggers level-up');await step(2300);await check('state','run','level-up returns to road');

  await probe("loadStage(0);state='run';minions=[];road=[];progress=encounters[0].at-1;");
  await page.keyboard.down('ArrowUp');await step(32);await page.keyboard.up('ArrowUp');
  await check('[state,!!keys.ArrowUp]',['battle',false],'forward reaches main battle without held input leaking');
  await key('KeyR');
  await probe('selected=options.indexOf(target)');await key('Space');
  await check('[state,shotsLeft]',['aim',3],'correct answer gives three shots');
  const ax=await probe('aimX');await key('ArrowRight');assert(await probe('aimX')>ax);
  await probe('aimX=315;aimY=500');await key('Space');await check('[shotsLeft,enemyHP]',[2,100],'miss consumes ammo only');
  for(let i=0;i<2;i++){await probe('aimX=aimingEnemyX(performance.now());aimY=H*.47');await key('Space')}
  await check('state','shotresolve','third shot ends aiming');assert(await probe('enemyHP')<100);
  await step(750);await check('state','enemyturn','remaining enemy attacks');
  const shield=await probe('[shieldX,shieldY]');await key('ArrowLeft');assert((await probe('shieldX'))<shield[0]);
  await probe('shieldX=orbTargetX;shieldY=orbTargetY');const hp=await probe('playerHP');
  await step(4000);await check('[guardSuccess,playerHP]',[true,hp],'positioned guard takes zero damage');
  await page.waitForTimeout(850);await check('state','battle','guard returns to question');
  await probe('startEnemyTurn();orbTargetX=825;orbTargetY=365;shieldX=365;shieldY=625');await key('Space');await step(4000);
  await check('guardSuccess',false,'Space does not auto-guard');assert(await probe('playerHP')<hp);
  await page.waitForTimeout(850);
  await probe('selected=options.findIndex(x=>x!==target)');await key('Space');await check('state','wrong','incorrect answer retained');await step(2500);await check('state','enemyturn','incorrect answer leads to guard');
  await probe("state='battle';resultLock=false;cores=8;enemyHP=100");await key('ArrowUp');await check('state','special','special menu retained');await key('ArrowLeft');await key('ArrowLeft');await key('Space');await check('cores',5,'special spends cores');await step(4500);
  // Every world's generated road layout, main battles, XP and stage/rescue transitions.
  await probe('reset();start()');
  for(let stage=0;stage<10;stage++){
    await check('stageIndex',stage,'stage progression '+(stage+1));
    assert(await probe('minions.length')>0);
    await probe('progress=minions[0].at-100;lateral=targetLateral=minions[0].lane;laneIndex=Math.round(lateral/.58)');
    await key('KeyA');await step(900);assert(await probe('minions.some(m=>m.defeated)'));
    for(let encounter=0;encounter<3;encounter++){
      await probe("state='run';keys={};progress=encounters[currentEncounter].at;startBattle();selected=options.indexOf(target)");
      await key('Space');
      await probe('enemyHP=1;aimX=aimingEnemyX(performance.now());aimY=H*.47');await key('Space');await step(850);
      await check('state','victory','early kill ends shots '+stage+'/'+encounter);
      await step(1250);
      for(let n=0;n<12&&await probe("state==='levelup'");n++)await step(2300);
      if(encounter===2){
        if(stage<3){await check('state','rescue','boss rescues companion');await step(2500)}
        if(stage<9){await check('state','stageclear','stage clear');await step(1900)}
      }
    }
  }
  await check('[state,companions.length]',['finish',3],'ten worlds and three companions complete');
  await key('Enter');await check('[state,progress,!!keys.ArrowUp,swordAction]',['intro',0,false,null],'restart clears road state');
  // Road screenshots for visual review, generated only when requested.
  if(process.env.QA_SCREENSHOTS){
    fs.mkdirSync(process.env.QA_SCREENSHOTS,{recursive:true});
    await key('Space');await probe('progress=400;lateral=targetLateral=-.58;laneIndex=-1');await step(16);
    await page.screenshot({path:process.env.QA_SCREENSHOTS+'/road-ready.png'});
    await key('KeyA');await step(176);await page.screenshot({path:process.env.QA_SCREENSHOTS+'/road-hit.png'});
    await step(200);await page.screenshot({path:process.env.QA_SCREENSHOTS+'/road-defeat.png'});
  }
  assert.deepEqual(errors,[],'no browser runtime errors');
  await browser.close();console.log('All road and battle regression checks passed.');
})().catch(e=>{console.error(e);process.exit(1)});
