import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ProductCard } from "../product-card";

describe("ProductCard", () => {
  it("shows product identity, price, discount price, and detail link", () => {
    render(
      <ProductCard
        product={{
          slug: "sample",
          title: "محصول تست",
          brand: "Test Brand",
          price: 285000,
          compareAtPrice: 320000,
          category: "women",
          available: true,
        }}
      />,
    );

    expect(screen.getByText("محصول تست")).toBeInTheDocument();
    expect(screen.getByText("Test Brand")).toBeInTheDocument();
    expect(screen.getByText("۲۸۵٬۰۰۰ تومان")).toBeInTheDocument();
    expect(screen.getByText("۳۲۰٬۰۰۰ تومان")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /مشاهده محصول/ })).toHaveAttribute("href", "/product/sample");
  });
});
