import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/lib/catalog/runtime", () => ({
  loadShopProducts: vi.fn(async () => [
    {
      id: 1,
      slug: "women-essential-01",
      name: "محصول زنانه منتخب",
      brand: "Diaa Selection",
      description: "",
      price: 285000,
      categoryId: 1,
      categorySlug: "women-underwear",
      categoryTitle: "لباس زیر زنانه",
      available: false,
      createdAt: "2026-09-14 10:00:00",
      image: undefined,
    },
    {
      id: 2,
      slug: "men-essential-01",
      name: "محصول مردانه منتخب",
      brand: "Bodyguard",
      description: "",
      price: 285000,
      compareAtPrice: 320000,
      categoryId: 2,
      categorySlug: "men-underwear",
      categoryTitle: "لباس زیر مردانه",
      available: true,
      createdAt: "2026-09-14 10:00:00",
      image: undefined,
    },
  ]),
}));

import ShopPage from "./page";

describe("ShopPage", () => {
  it("renders catalog products with price and stock state", async () => {
    render(await ShopPage());

    expect(screen.getByRole("heading", { name: "فروشگاه", level: 1 })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "همه محصولات", level: 2 })).toBeInTheDocument();

    expect(screen.getByText("محصول زنانه منتخب")).toBeInTheDocument();
    expect(screen.getByText("محصول مردانه منتخب")).toBeInTheDocument();
    expect(screen.getByText("ناموجود")).toBeInTheDocument();

    expect(
      screen.getByRole("link", { name: "مشاهده محصول محصول مردانه منتخب" }),
    ).toHaveAttribute("href", "/product/men-essential-01");
    expect(screen.getByRole("banner")).toBeInTheDocument();
    expect(screen.getByRole("contentinfo")).toBeInTheDocument();
  });
});
