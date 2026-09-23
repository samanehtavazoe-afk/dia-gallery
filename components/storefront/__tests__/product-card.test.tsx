import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ProductCard } from "../product-card";

describe("ProductCard", () => {
  it("shows product identity, price, discount price, and detail link", () => {
    render(
      <ProductCard
        product={{
          id: 1,
          slug: "sample",
          name: "محصول تست",
          brand: "Test Brand",
          description: "شرح محصول",
          price: 285000,
          compareAtPrice: 320000,
          categoryId: 1,
          categorySlug: "women-underwear",
          categoryTitle: "لباس زیر زنانه",
          available: false,
          createdAt: "2026-09-14 10:00:00",
          image: {
            id: 1,
            colorId: 1,
            path: "/categories/women-underwear.webp",
            alt: "محصول تست مشکی",
            sortOrder: 1,
          },
        }}
      />,
    );

    expect(screen.getByText("محصول تست")).toBeInTheDocument();
    expect(screen.getByText("Test Brand")).toBeInTheDocument();
    expect(screen.getByText("۲۸۵٬۰۰۰ تومان")).toBeInTheDocument();
    expect(screen.getByText("۳۲۰٬۰۰۰ تومان")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "محصول تست مشکی" })).toBeInTheDocument();
    expect(screen.getByText("ناموجود")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /مشاهده محصول/ })).toHaveAttribute("href", "/product/sample");
  });
});
