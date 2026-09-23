import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ProductGrid } from "../product-grid";

describe("ProductGrid", () => {
  it("renders supplied products in the selected products section", () => {
    render(
      <ProductGrid
        products={[
          {
            id: 1,
            slug: "sample-one",
            name: "محصول اول",
            brand: "Brand One",
            description: "",
            price: 210000,
            categoryId: 1,
            categorySlug: "women-underwear",
            categoryTitle: "لباس زیر زنانه",
            available: true,
            createdAt: "2026-09-14 10:00:00",
          },
          {
            id: 2,
            slug: "sample-two",
            name: "محصول دوم",
            brand: "Brand Two",
            description: "",
            price: 320000,
            categoryId: 2,
            categorySlug: "men-underwear",
            categoryTitle: "لباس زیر مردانه",
            available: true,
            createdAt: "2026-09-14 10:00:00",
          },
        ]}
      />,
    );

    expect(screen.getByRole("heading", { name: "محصولات منتخب" })).toBeInTheDocument();
    expect(screen.getByText("محصول اول")).toBeInTheDocument();
    expect(screen.getByText("محصول دوم")).toBeInTheDocument();
  });
});
