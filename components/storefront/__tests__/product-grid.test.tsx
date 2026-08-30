import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ProductGrid } from "../product-grid";

describe("ProductGrid", () => {
  it("renders supplied products in the selected products section", () => {
    render(
      <ProductGrid
        products={[
          {
            slug: "sample-one",
            title: "محصول اول",
            brand: "Brand One",
            price: 210000,
            category: "women",
            available: true,
          },
          {
            slug: "sample-two",
            title: "محصول دوم",
            brand: "Brand Two",
            price: 320000,
            category: "men",
            available: true,
          },
        ]}
      />,
    );

    expect(screen.getByRole("heading", { name: "محصولات منتخب" })).toBeInTheDocument();
    expect(screen.getByText("محصول اول")).toBeInTheDocument();
    expect(screen.getByText("محصول دوم")).toBeInTheDocument();
  });
});
