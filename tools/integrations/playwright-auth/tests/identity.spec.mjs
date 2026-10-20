import { test, expect } from '../fixture.mjs';
// Explicitly opted-in smoke test: no message, business submit or extra API request.
test('authenticated Beta page is handed to test body', async ({ page }) => {
  await expect(page.locator('textarea')).toBeVisible();
  await expect(page.locator('textarea')).toBeEditable();
});
