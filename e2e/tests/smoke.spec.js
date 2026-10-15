const { test, expect } = require("@playwright/test");

const viewports = [
  { name: "mobile-375", width: 375, height: 667 },
  { name: "tablet-768", width: 768, height: 1024 },
  { name: "desktop-1280", width: 1280, height: 800 },
];

for (const vp of viewports) {
  test(`home carrega responsivamente em ${vp.name}`, async ({ page }) => {
    await page.setViewportSize({ width: vp.width, height: vp.height });
    const response = await page.goto("/", { waitUntil: "domcontentloaded" });
    expect(response, "sem resposta do servidor").not.toBeNull();
    expect(response.ok(), `status HTTP inesperado: ${response && response.status()}`).toBeTruthy();
    await expect(page).toHaveTitle(/Voltix/i);
    await expect(page.locator("body")).toContainText(/Voltix/i);
  });
}
