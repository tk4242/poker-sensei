// Run on the disposable make_app() test server, not on production.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
(async () => {
  const base = process.env.SENSEI_TEST_URL || 'http://127.0.0.1:5065';
  assert(['127.0.0.1', 'localhost'].includes(new URL(base).hostname));
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  try {
    for (const javaScriptEnabled of [true, false]) {
      const context = await browser.newContext({ javaScriptEnabled, viewport: { width: 390, height: 844 } });
      const page = await context.newPage(); const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(base + '/login');
      await page.locator('[name=user]').fill('koja');
      await page.locator('[name=password]').fill('correct-horse-battery');
      await page.locator('form button').click();
      await page.locator('.course-tile[href*="mode=decisions"]').click();
      assert(await page.locator('[name=mode][value=decisions]').isChecked());
      if (javaScriptEnabled) {
        assert(await page.locator('[name=position]').isDisabled());
        assert(await page.locator('[name=stack]').isDisabled());
      }
      for (const [players, format] of [[2, 'mtt'], [6, 'cash'], [8, 'mtt']]) {
        await page.goto(base + `/table?mode=decisions&format=${format}`);
        await page.locator('[name=players]').selectOption(String(players));
        await page.locator('.start-table').click();
        for (let i = 0; i < 5; i++) {
          assert.equal(await page.locator('.poker-table .seat').count(), players);
          assert(await page.locator('.decision-panel > .coach-tip').isVisible());
          assert.equal(await page.locator('.table-actions .primary').count(), 0);
          if (i === 0) {
            for (const width of [320, 390, 768, 1280]) {
              await page.setViewportSize({ width, height: 844 });
              assert(!await page.evaluate(() => document.documentElement.scrollWidth > innerWidth));
              for (const button of await page.locator('.table-actions button').all()) await button.click({ trial: true });
            }
            await page.setViewportSize({ width: 390, height: 844 });
          }
          await page.locator('.table-actions button').first().click();
          await page.locator('.table-feedback').waitFor({ state: 'visible' });
          await page.locator('a.start-table').click();
        }
        assert(await page.locator('.table-summary').isVisible());
        await page.locator('.table-summary form button').click();
        assert(await page.locator('.table-actions').isVisible());
      }
      assert.deepEqual(errors, []);
      await context.close();
    }
    console.log('PASS: decisions entry, fixed conditions, 2/6/8 seats, 5 answers/results/retry, JS on/off, 4 widths');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
