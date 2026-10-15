const { test, expect } = require("@playwright/test");
const path = require("path");
const fs = require("fs");

const viewports = [
  { name: "mobile-375", width: 375, height: 667 },
  { name: "tablet-768", width: 768, height: 1024 },
  { name: "desktop-1280", width: 1280, height: 800 },
];

const outDir = path.join(__dirname, "..", "screenshots");
if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

async function checkViewportIssues(page, viewportName) {
  const issues = [];

  // Horizontal overflow
  const hasHorizontalScroll = await page.evaluate(() => {
    return document.documentElement.scrollWidth > document.documentElement.clientWidth + 1;
  });
  if (hasHorizontalScroll) {
    issues.push("overflow-horizontal");
  }

  // Overflow on body? (sometimes)
  const bodyOverflow = await page.evaluate(() => {
    const body = document.body;
    return body.scrollWidth > body.clientWidth + 1;
  });
  if (bodyOverflow && !hasHorizontalScroll) {
    issues.push("overflow-horizontal-body");
  }

  // Buttons with zero visible width
  const clippedButtons = await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll("button, [role=button]"));
    return buttons.filter(b => {
      const r = b.getBoundingClientRect();
      return r.width <= 2 || r.height <= 2;
    }).length;
  });
  if (clippedButtons > 0) {
    issues.push(`botoes-cortados:${clippedButtons}`);
  }

  // Images with overflow
  const imgOverflow = await page.evaluate(() => {
    const imgs = Array.from(document.querySelectorAll("img"));
    return imgs.filter(img => {
      const ir = img.getBoundingClientRect();
      const pr = img.parentElement ? img.parentElement.getBoundingClientRect() : {width: Infinity, height: Infinity};
      return ir.width > pr.width + 2 || ir.height > pr.height + 2;
    }).length;
  });
  if (imgOverflow > 0) {
    issues.push(`imagens-sobresalentes:${imgOverflow}`);
  }

  return issues;
}

async function capture(name, page, vp) {
  const file = path.join(outDir, `${name}-${vp.name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  return file;
}

test("visual: catálogo + carrinho + checkout + pedidos + admin (login)", async ({ page }) => {
  for (const vp of viewports) {
    await page.setViewportSize({ width: vp.width, height: vp.height });

    // Catálogo
    await page.goto("/catalogo", { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(500);
    const catFile = await capture("catalogo", page, vp);
    const catIssues = await checkViewportIssues(page, vp.name);

    // Login cliente (se necessário)
    await page.goto("/cliente", { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(400);

    // Tentar preencher login se campos existirem
    const emailInput = page.locator('input[name="email"], input[type="email"]').first();
    if (await emailInput.count() > 0 && await emailInput.isVisible()) {
      if (process.env.E2E_TEST_EMAIL) {
        await emailInput.fill(process.env.E2E_TEST_EMAIL);
      }
      const pass = page.locator('input[name="password"], input[type="password"]').first();
      if (await pass.count() > 0 && process.env.E2E_TEST_PASSWORD) {
        await pass.fill(process.env.E2E_TEST_PASSWORD);
        await page.getByRole("button", { name: /entrar/i }).first().click();
        await page.waitForTimeout(800);
      }
    }

    // Carrinho
    await page.goto("/carrinho", { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(500);
    const cartFile = await capture("carrinho", page, vp);
    const cartIssues = await checkViewportIssues(page, vp.name);

    // Checkout
    await page.goto("/checkout", { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(500);
    const chkFile = await capture("checkout", page, vp);
    const chkIssues = await checkViewportIssues(page, vp.name);

    // Pedidos
    await page.goto("/pedidos", { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(500);
    const ordFile = await capture("pedidos", page, vp);
    const ordIssues = await checkViewportIssues(page, vp.name);

    // Admin login/painel
    await page.goto("/interno", { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(500);
    const admFile = await capture("admin-interno", page, vp);
    const admIssues = await checkViewportIssues(page, vp.name);

    // Log por viewport
    console.log(`[${vp.name}] catálogo: ${catIssues.join(",") || "ok"} → ${catFile}`);
    console.log(`[${vp.name}] carrinho: ${cartIssues.join(",") || "ok"} → ${cartFile}`);
    console.log(`[${vp.name}] checkout: ${chkIssues.join(",") || "ok"} → ${chkFile}`);
    console.log(`[${vp.name}] pedidos: ${ordIssues.join(",") || "ok"} → ${ordFile}`);
    console.log(`[${vp.name}] admin-interno: ${admIssues.join(",") || "ok"} → ${admFile}`);
  }
});
