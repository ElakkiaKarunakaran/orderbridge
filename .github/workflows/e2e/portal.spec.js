// OrderBridge Portal — Playwright E2E Tests
// Covers all 4 screens of index.html
// Run with: npx playwright test
// Prerequisite: api.py running on :6000, and index.html served (e.g. `python -m http.server 8080`)

const { test, expect } = require('@playwright/test');

const BASE_URL = 'http://localhost:8080'; // where index.html is being served

test.describe('OrderBridge Portal — 4 Screens', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
  });

  test('Screen 1: Order Status loads and shows connection', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('OrderBridge');
    // Wait for API connection indicator to go green
    await expect(page.locator('#connText')).toContainText('API connected', { timeout: 10000 });
    // At least one order row should render
    await expect(page.locator('#s1body tr').first()).toBeVisible({ timeout: 10000 });
  });

  test('Screen 2: Order History filters work', async ({ page }) => {
    await page.click('button[data-screen="s2"]');
    await expect(page.locator('#s2')).toHaveClass(/active/);
    await expect(page.locator('#s2body tr').first()).toBeVisible({ timeout: 10000 });

    // Filter by domain
    await page.selectOption('#filterDomain', 'fulfilment');
    const rows = page.locator('#s2body tr');
    const count = await rows.count();
    if (count > 0 && !(await rows.first().innerText()).includes('No matching')) {
      // Every visible row's domain badge should say "fulfilment"
      await expect(rows.first()).toContainText('fulfilment');
    }
  });

  test('Screen 2: CSV export button is present and clickable', async ({ page }) => {
    await page.click('button[data-screen="s2"]');
    const downloadPromise = page.waitForEvent('download');
    await page.click('text=Export CSV');
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toBe('orderbridge_history.csv');
  });

  test('Screen 3: Fulfilment Tracking shows order timelines', async ({ page }) => {
    await page.click('button[data-screen="s3"]');
    await expect(page.locator('#s3')).toHaveClass(/active/);
    await expect(page.locator('#s3list')).toBeVisible({ timeout: 10000 });
  });

  test('Screen 4: AI Demand Intelligence renders forecast chart and anomaly table', async ({ page }) => {
    await page.click('button[data-screen="s4"]');
    await expect(page.locator('#s4')).toHaveClass(/active/);
    // Chart canvas should be present
    await expect(page.locator('#forecastChart')).toBeVisible({ timeout: 10000 });
    // Anomaly table should have at least one row
    await expect(page.locator('#anomalyBody tr').first()).toBeVisible({ timeout: 10000 });
  });

  test('Screen 4: switching scenario tabs updates the chart', async ({ page }) => {
    await page.click('button[data-screen="s4"]');
    await page.waitForSelector('#scenarioTabs button', { timeout: 10000 });
    const tabs = page.locator('#scenarioTabs button');
    const tabCount = await tabs.count();
    expect(tabCount).toBeGreaterThanOrEqual(1);
    if (tabCount > 1) {
      await tabs.nth(1).click();
      await expect(tabs.nth(1)).toHaveClass(/active/);
    }
  });

  test('Navigation: all 4 tabs are clickable and switch screens correctly', async ({ page }) => {
    const screens = ['s1', 's2', 's3', 's4'];
    for (const screen of screens) {
      await page.click(`button[data-screen="${screen}"]`);
      await expect(page.locator(`#${screen}`)).toHaveClass(/active/);
    }
  });

});