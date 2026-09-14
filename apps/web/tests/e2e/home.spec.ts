import { expect, test } from "@playwright/test";

test("shows the scaffold dashboard", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "AI Job Search Copilot" })).toBeVisible();
  await expect(page.getByText("First vertical slice")).toBeVisible();
});
