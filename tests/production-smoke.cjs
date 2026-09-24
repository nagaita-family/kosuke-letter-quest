const {chromium}=require('playwright');
const fs=require('node:fs'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const base='https://family.nagaita.jp/kosuke-letter-quest/';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
  // Wait for Pages/CDN propagation; compare every published runtime asset to this build.
  let ready=false;
  for(let attempt=0;attempt<24;attempt++){
    try{
      for(const file of ['index.html','game.js','style.css']){
        const res=await fetch(base+file+'?verify='+Date.now(),{signal:AbortSignal.timeout(15000)});
        assert(res.ok);assert.equal(hash(Buffer.from(await res.arrayBuffer())),hash(fs.readFileSync(file)),file);
      }
      ready=true;break;
    }catch(e){console.log('Waiting for published assets',attempt+1,e.message);await new Promise(r=>setTimeout(r,10000))}
  }
  assert(ready,'production assets must match release');
  const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1280,height:720}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error'&&!m.text().includes('404'))errors.push(m.text())});
  await page.goto(base+'?v=12.6');assert.equal(await page.title(),'Kosuke Letter Quest v12.6');
  await page.keyboard.press('Space');await page.waitForTimeout(200);
  assert.equal(await page.locator('#run-status').textContent(),'↑  HOLD TO WALK');
  await page.keyboard.press('ArrowLeft');await page.keyboard.down('ArrowUp');await page.waitForTimeout(3050);await page.keyboard.up('ArrowUp');await page.waitForTimeout(150);
  assert.equal(await page.locator('#run-status').textContent(),'A  ⚔');
  if(process.env.QA_SCREENSHOTS)await page.screenshot({path:process.env.QA_SCREENSHOTS+'/production-ready.png'});
  await page.keyboard.press('ArrowDown');await page.waitForFunction(()=>document.querySelector('#run-status').textContent==='↓ GUN · SPACE FIRE');
  if(process.env.QA_SCREENSHOTS)await page.screenshot({path:process.env.QA_SCREENSHOTS+'/production-gun.png'});
  for(let i=0;i<4;i++)await page.keyboard.press('ArrowLeft');
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('Space');await page.waitForTimeout(200);
  assert.equal(await page.locator('#xp-text').textContent(),'8 / 60');
  if(process.env.QA_SCREENSHOTS)await page.screenshot({path:process.env.QA_SCREENSHOTS+'/production-gun-hit.png'});
  await page.reload();await page.keyboard.press('Space');await page.keyboard.press('ArrowLeft');
  await page.keyboard.down('ArrowUp');await page.waitForTimeout(3050);await page.keyboard.up('ArrowUp');
  await page.keyboard.press('KeyA');await page.waitForTimeout(190);
  if(process.env.QA_SCREENSHOTS)await page.screenshot({path:process.env.QA_SCREENSHOTS+'/production-hit.png'});
  assert.equal(await page.locator('#xp-text').textContent(),'8 / 60');
  await page.waitForTimeout(1000);assert.equal(await page.locator('#run-status').textContent(),'↑  HOLD TO WALK');
  assert.deepEqual(errors,[]);await browser.close();
  console.log('Production v12.6: all three asset hashes match; real keyboard walk / stop / first-person gun / sword / XP passed.');
})().catch(e=>{console.error(e);process.exit(1)});
