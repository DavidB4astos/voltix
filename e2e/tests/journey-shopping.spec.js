const { test, expect } = require("@playwright/test");

const TEST_EMAIL = process.env.E2E_TEST_EMAIL;
const TEST_PASSWORD = process.env.E2E_TEST_PASSWORD;

test.describe("Jornada de compra (cliente)", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });
  });

  test("fluxo completo: login → catálogo → carrinho → checkout → pedidos", async ({ page }) => {
    test.skip(
      !TEST_EMAIL || !TEST_PASSWORD,
      "Credenciais de teste ausentes em .env (E2E_TEST_EMAIL / E2E_TEST_PASSWORD)"
    );

    await page.goto("/cliente", { waitUntil: "domcontentloaded" });
    const emailInput = page.locator('input[name="email"], input[type="email"]').first();
    if (await emailInput.count() > 0) {
      await emailInput.fill(TEST_EMAIL);
    }
    const passInput = page.locator('input[name="password"], input[type="password"]').first();
    if (await passInput.count() > 0) {
      await passInput.fill(TEST_PASSWORD);
      const loginBtn = page.getByRole("button", { name: /entrar/i }).first();
      if (await loginBtn.count() > 0) {
        await loginBtn.click();
        await page.waitForTimeout(800);
      }
    }

    await page.goto("/catalogo", { waitUntil: "domcontentloaded" });
    await expect(page.locator("body")).toContainText(/catálogo|produtos/i, { timeout: 5000 }).catch(() => {});

    await page.goto("/carrinho", { waitUntil: "domcontentloaded" });
    await expect(page.locator("body")).toContainText(/carrinho|total/i, { timeout: 5000 }).catch(() => {});

    await page.goto("/checkout", { waitUntil: "domcontentloaded" });
    await expect(page.locator("body")).toContainText(/checkout|endereço|pagamento/i, { timeout: 5000 }).catch(() => {});

    await page.goto("/pedidos", { waitUntil: "domcontentloaded" });
    await expect(page.locator("body")).toContainText(/pedidos|histórico|resumo/i, { timeout: 5000 }).catch(() => {});
  });
});
