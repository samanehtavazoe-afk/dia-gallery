import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const { notFound, loadProductCatalog } = vi.hoisted(() => ({
  notFound: vi.fn(() => {
    throw new Error("NOT_FOUND");
  }),
  loadProductCatalog: vi.fn(async (slug: string) =>
    slug === "sample"
      ? {
          id: 1,
          slug,
          name: "محصول تست",
          brand: "Dia",
          description: "شرح کامل",
          price: 200000,
          categoryId: 1,
          categorySlug: "hoodie",
          categoryTitle: "هودی",
          available: false,
          createdAt: "2026-09-14 10:00:00",
          colors: [],
          variants: [],
          images: [],
        }
      : null,
  ),
}));

vi.mock("next/navigation", () => ({ notFound }));
vi.mock("@/lib/catalog/runtime", () => ({ loadProductCatalog }));

import ProductPage from "./page";

describe("ProductPage", () => {
  it("renders product details", async () => {
    render(
      await ProductPage({ params: Promise.resolve({ slug: "sample" }) }),
    );

    expect(
      screen.getByRole("heading", { name: "محصول تست" }),
    ).toBeInTheDocument();
    expect(screen.getByText("شرح کامل")).toBeInTheDocument();
  });

  it("returns not found for an unknown product", async () => {
    await expect(
      ProductPage({ params: Promise.resolve({ slug: "missing" }) }),
    ).rejects.toThrow("NOT_FOUND");
    expect(notFound).toHaveBeenCalled();
  });
});
