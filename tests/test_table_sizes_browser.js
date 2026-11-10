// Use only the disposable tests.test_app.make_app() server.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
(async () => {
  const base = process.env.SENSEI_TEST_URL || 'http://127.0.0.1:5065';
  assert(['127.0.0.1', 'localhost'].includes(new URL(base).hostname));
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  try {
    for (const javaScriptEnabled of [true, false]) {
      const context = await browser.newContext({ javaScriptEnabled, viewport: { width: 390, height: 844 } });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(base + '/login');
      await page.locator('[name=user]').fill('koja');
      await page.locator('[name=password]').fill('correct-horse-battery');
      await page.locator('form button').click();
      await page.goto(base + '/table');
      assert.deepEqual(await page.locator('[name=players] option').evaluateAll(xs => xs.map(x => x.value)), ['2','3','4','5','6','7','8']);
      await page.locator('[name=players]').selectOption('8');
      await page.locator('[name=mode][value=range]').check();
      assert.equal(await page.locator('[name=players]').inputValue(), '8');
      assert.equal(await page.locator('[name=players] option:disabled').count(), 0);
      if (javaScriptEnabled) {
        assert(await page.locator('.start-table').isDisabled());
        assert.match(await page.locator('#setup-note').textContent(), /8人.*未収録/);
        await page.locator('[name=mode][value=positions]').check();
        assert.equal(await page.locator('[name=players]').inputValue(), '8');
        assert(await page.locator('.start-table').isEnabled());
        assert(!await page.locator('[data-switch-hu]').isVisible());
        await page.locator('[name=mode][value=range]').check();
        await page.locator('[data-switch-hu]').click();
        assert.equal(await page.locator('[name=players]').inputValue(), '2');
        assert(await page.locator('.start-table').isEnabled());
        await page.locator('[name=players]').selectOption('5');
        assert(await page.locator('.start-table').isDisabled());
        await page.locator('[name=mode][value=flop]').check();
        assert.equal(await page.locator('[name=players]').inputValue(), '5');
        assert(await page.locator('.start-table').isEnabled());
      } else {
        await page.locator('.start-table').click();
        assert.match(await page.locator('body').textContent(), /未収録/);
      }
      for (let n = 2; n <= 8; n++) {
        for (const mode of ['positions', 'flop']) {
          await page.goto(base + '/table');
          await page.locator('[name=players]').selectOption(String(n));
          await page.locator(`[name=mode][value=${mode}]`).check();
          await page.locator('.start-table').click();
          assert.equal(await page.locator('.poker-table .seat').count(), n);
          assert(!await page.evaluate(() => document.documentElement.scrollWidth > innerWidth));
          await page.locator('.table-actions button').first().click();
          assert(await page.locator('.table-feedback').isVisible());
        }
      }
      assert.deepEqual(errors, []);
      await context.close();
    }
    console.log('PASS: 2–8 seats, mode changes preserve selection, explicit HU switch, unavailable model guard, JS on/off');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
