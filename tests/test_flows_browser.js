// Run against tests.test_app.make_app(), never production. See test_menu_browser.js for environment.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict');
(async()=>{
 const b=await chromium.launch({headless:true,channel:'chrome'});const ctx=await b.newContext({viewport:{width:390,height:844}});const p=await ctx.newPage(); const errors=[];
 p.on('pageerror',e=>errors.push(e.message));
 const base=process.env.SENSEI_TEST_URL || 'http://127.0.0.1:5065'; assert(['127.0.0.1','localhost'].includes(new URL(base).hostname), 'Use a local test database');
 const go=async path=>{const r=await p.goto(base+path);assert(r.status()<400,path+':'+r.status());};
 await go('/login');await p.locator('[name=user]').fill('koja');await p.locator('[name=password]').fill('correct-horse-battery');await p.locator('form button').click();
 await go('/settings');await p.locator('[name=daily_quota]').fill('15');await p.locator('[name=batch_size]').fill('5');await p.locator('form').first().locator('button').click();assert.equal(await p.locator('[name=daily_quota]').inputValue(),'15');
 await go('/records/session/new');await p.locator('[name=event]').fill('UI audit session');await p.locator('[name=opponents]').fill('UI audit opponent memo');await p.locator('[name=opp_types]').first().check();await p.locator('form button').click();
 await p.locator('a[href^="/records/session/"]').filter({hasText:/^\d{4}-/}).first().click();assert.equal(await p.locator('[name=opponents]').inputValue(),'UI audit opponent memo');await p.locator('[name=event]').fill('UI audit session edited');await p.locator('form').first().locator('button').click();
 await go('/records/hand/new');await p.locator('[name=title]').fill('UI audit hand');await p.locator('[name=hero_cards]').fill('Ah Kh');await p.locator('[name=self_review]').fill('Review saved');await p.locator('form button').click();assert((await p.locator('body').innerText()).includes('UI audit hand'));
 await go('/records');await p.locator('[name=minutes]').fill('10');await p.locator('[name=topic]').fill('UI audit study');await p.locator('form[action="/records/study"] button').click();assert((await p.locator('body').innerText()).includes('UI audit study'));
 await go('/coach/mental');await p.locator('[name=c_game_signs]').fill('Audit sign');await p.locator('[name=correction]').fill('Audit correction');await p.locator('form').filter({has:p.locator('[name=c_game_signs]')}).locator('button').click();assert.equal(await p.locator('[name=c_game_signs]').inputValue(),'Audit sign');
 await p.locator('[name=budget_plan]').fill('Audit plan');await p.locator('form').filter({has:p.locator('[name=budget_plan]')}).locator('button').click();assert.equal(await p.locator('[name=budget_plan]').inputValue(),'Audit plan');
 await go('/practice/quick/positions');for(let i=0;i<5;i++){await p.locator('.q:not(.hide) label').first().click();if(i<4)await p.waitForTimeout(300);}await p.locator('form.quiz .submit button').click();await p.waitForSelector('.big-score');
 const routes=['/','/learn','/table','/table/ranges','/practice','/train','/quest','/records','/coach','/coach/mental','/library','/knowledge','/settings','/tools','/cheatsheet','/export'];
 for(const w of [320,390,760,768,1280]){await p.setViewportSize({width:w,height:700});for(const r of routes){await go(r);if(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth))errors.push(`overflow ${w} ${r}`);}}
 console.log(JSON.stringify({forms:'settings/session-create-edit/hand/study/mental/quiz passed',pageChecks:routes.length*5,errors}));assert.deepEqual(errors,[]);await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
