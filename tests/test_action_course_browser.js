// Local test database only. See test_menu_browser.js for environment variables.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
(async () => {
  const base = process.env.SENSEI_TEST_URL || 'http://127.0.0.1:5065';
  assert(['127.0.0.1', 'localhost'].includes(new URL(base).hostname));
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  try {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(base + '/login');
    await page.locator('[name=user]').fill('koja');
    await page.locator('[name=password]').fill('correct-horse-battery');
    await page.locator('form button').click();
    const topics = ['actions', 'ranges', 'flop', 'sizing', 'threebet', 'turnriver', 'hu', 'bluff'];
    for (const topic of topics) {
      await page.goto(base + '/learn/actions/' + topic);
      await page.locator('.model-note summary').click();
      assert(await page.locator('.model-note ol').isVisible());
      await page.locator('form button').click();
      for (let i = 0; i < 5; i++) {
        const question = page.locator('.q').nth(i);
        await question.locator('label').first().click();
        if (i < 4) await page.locator('.q').nth(i + 1).waitFor({ state: 'visible' });
      }
      await page.locator('.submit button').click();
      await page.locator('.big-score').waitFor();
      await page.getByRole('link', { name: '考え方と例を見直す' }).click();
      assert.equal(new URL(page.url()).pathname, '/learn/actions/' + topic);
    }
    for (const width of [320, 390, 760, 1280]) {
      await page.setViewportSize({ width, height: 844 });
      for (const topic of ['', ...topics]) {
        const response = await page.goto(base + '/learn/actions' + (topic ? '/' + topic : ''));
        assert.equal(response.status(), 200);
        assert(!await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), `${width}: ${topic}`);
      }
    }
    const plain = await browser.newContext({ storageState: await context.storageState(), javaScriptEnabled: false });
    const p = await plain.newPage();
    await p.goto(base + '/learn/actions/flop');
    await p.locator('form button').click();
    for (const question of await p.locator('.q').all()) await question.locator('label').last().click();
    await p.locator('.submit button').click();
    await p.locator('.big-score').waitFor();
    await p.getByRole('link', { name: '復習する', exact: true }).click();
    assert(await p.locator('form.quiz').isVisible());
    assert.deepEqual(errors, []);
    console.log('PASS: 8 lessons / 40 answers / result-return links / 36 viewports / JS-off quiz and review');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
