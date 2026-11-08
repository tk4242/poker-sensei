/* Run against tests.test_app.make_app(), never production.
   SENSEI_TEST_URL=http://127.0.0.1:5065 PLAYWRIGHT_MODULE=/path/to/playwright node tests/test_menu_browser.js */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
(async () => {
  const base = process.env.SENSEI_TEST_URL || 'http://127.0.0.1:5065';
  assert(['127.0.0.1', 'localhost'].includes(new URL(base).hostname), 'Use a local test database');
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  try {
    for (const javaScriptEnabled of [true, false]) {
      const context = await browser.newContext({ javaScriptEnabled, hasTouch: true, viewport: { width: 390, height: 844 } });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(base + '/login');
      await page.locator('[name=user]').fill('koja');
      await page.locator('[name=password]').fill('correct-horse-battery');
      await page.locator('form button').click();
      const targets = await page.locator('header.top > .wrap > nav a').evaluateAll(links => links.map(a => a.getAttribute('href')));
      for (const width of [320, 390, 759, 760, 761, 1280]) {
        await page.setViewportSize({ width, height: width === 760 ? 390 : 844 });
        for (const target of targets) {
          await page.goto(base + '/');
          const mobile = width <= 760;
          const nav = page.locator(mobile ? '.mobile-menu nav' : 'header.top > .wrap > nav');
          if (mobile) {
            const toggle = page.locator('.mobile-menu summary');
            const before = await toggle.boundingBox();
            await toggle.tap();
            assert.deepEqual(await toggle.boundingBox(), before, 'Menu toggle must not move on opening');
          }
          await Promise.all([page.waitForNavigation({waitUntil: "domcontentloaded"}),
            nav.locator(`a[href="${target}"]`)[mobile ? "tap" : "click"]()]);
          assert.equal(new URL(page.url()).pathname, target);
          assert(!await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), `${target}: overflow at ${width}`);
          if (mobile) {
            await page.locator('.mobile-menu summary').tap();
            await page.locator('.mobile-menu summary').tap();
            assert.equal(await page.locator('.mobile-menu').getAttribute('open'), null);
          }
        }
      }
      assert.deepEqual(errors, []);
      await context.close();
    }
    console.log('PASS: all 12 navigation destinations, 6 widths, short landscape, JS on/off, stable toggle');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
