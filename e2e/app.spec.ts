import { test, expect, type Page } from '@playwright/test';

// End-to-end coverage of the fully-static judge (vite preview build). The flows
// mirror real usage: pick a problem, write a per-line solution, submit, and read
// the verdict - plus a responsive check that the layout never overflows.

// Wait until the catalog + first problem have loaded (picker count + editor).
async function waitReady(page: Page) {
  await expect(page.getByRole('heading', { name: 'Polyglot CP' })).toBeVisible();
  await expect(page.locator('.picker-count')).toContainText('問');
  await expect(page.locator('.editor-textarea')).toBeVisible();
}

// Toggle a rotation language by its checkbox label in the rotation bar.
function langToggle(page: Page, lang: string) {
  return page.locator('.rotation-toggles label', { hasText: new RegExp(`^${lang}\\*?\\u2020?$`) }).locator('input');
}

test('(a) loads the catalog and shows the problem picker', async ({ page }) => {
  await page.goto('/');
  await waitReady(page);
  // The bundled catalog has hundreds of problems and a selected one by default.
  await expect(page.locator('.picker-item').first()).toBeVisible();
  const count = await page.locator('.picker-item').count();
  expect(count).toBeGreaterThan(0);
  await expect(page.locator('.picker-item.selected')).toHaveCount(1);
});

test('(b) python solution submits to AC', async ({ page }) => {
  await page.goto('/');
  await waitReady(page);
  // Pick the first (A + B) problem explicitly.
  await page.locator('.picker-item').first().click();
  // Rotation = python only; one self-contained Pyodide program reads "A B" -> A+B.
  await langToggle(page, 'javascript').uncheck();
  await page.locator('.editor-textarea').fill('import sys; a,b=map(int,sys.stdin.read().split()); print(a+b)');
  await expect(page.locator('.rotation-bar .lang-badge')).toHaveText(['PY']);
  await page.getByRole('button', { name: /提出/ }).click();
  // First run loads CPython (WASM) from the CDN, so allow a generous wait.
  await expect(page.locator('.verdict-row .verdict')).toHaveText('AC', { timeout: 150_000 });
  await expect(page.locator('.score')).toContainText('/');
});

test('(c) javascript solution is graded to AC', async ({ page }) => {
  await page.goto('/');
  await waitReady(page);
  await page.locator('.picker-item').first().click();
  // Rotation = javascript only; runs entirely in the JS worker (no CDN).
  await langToggle(page, 'python').uncheck();
  await page
    .locator('.editor-textarea')
    .fill("const [a,b]=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number); console.log(a+b);");
  await expect(page.locator('.rotation-bar .lang-badge')).toHaveText(['JS']);
  await page.getByRole('button', { name: /提出/ }).click();
  await expect(page.locator('.verdict-row .verdict')).toHaveText('AC', { timeout: 60_000 });
});

test('(d) language rotation can be switched via the toggles', async ({ page }) => {
  await page.goto('/');
  await waitReady(page);
  // Default rotation: python -> javascript.
  await expect(page.locator('.rotation-bar .lang-badge')).toHaveText(['PY', 'JS']);
  await langToggle(page, 'ruby').check(); // add a judge0 language to the rotation
  await expect(page.locator('.rotation-bar .lang-badge')).toHaveText(['PY', 'JS', 'RB']);
  await langToggle(page, 'javascript').uncheck();
  await expect(page.locator('.rotation-bar .lang-badge')).toHaveText(['PY', 'RB']);
});

test('(e) no horizontal overflow at a narrow 375px viewport', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 800 });
  await page.goto('/');
  await waitReady(page);
  const overflow = await page.evaluate(() => {
    const el = document.documentElement;
    return Math.max(el.scrollWidth - el.clientWidth, document.body.scrollWidth - document.body.clientWidth);
  });
  expect(overflow).toBeLessThanOrEqual(1); // <=1px tolerance for sub-pixel rounding
});
