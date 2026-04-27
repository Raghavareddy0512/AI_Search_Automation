import { test, expect } from '@playwright/test';

test('Search UI validation', async ({ page }) => {

  // 1. Go to site
  await page.goto('https://beta.dazn.com/en-CA/welcome');

  // 2. Accept cookies (safe handling)
  try {
    await page.getByRole('button', { name: 'Accept' }).click();
  } catch {}

  // 3. Click Login
  await page.locator('button.tp-button-primary:has-text("Log in")').click();

  // 4. Enter Email
  await page.locator('[data-test-id="EMAIL"]').fill('adtechca@dazn.com');
  await page.locator('[data-test-id="refined-button-signin"]').click();

  // 5. Enter Password
  await page.locator('[data-test-id="PASSWORD"]').fill('55555eE');
  await page.locator('[data-test-id="refined-button-signin"]').click();

  // 6. Wait for login
   await page.waitForSelector('[data-test-id="SEARCH"]', { timeout: 20000 });
});