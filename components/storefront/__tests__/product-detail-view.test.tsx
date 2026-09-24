import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { ProductDetailView } from "../product-detail-view";

const product = {
  id: 1,
  slug: "sample",
  name: "محصول تست",
  brand: "Dia",
  description: "شرح کامل",
  price: 200000,
  compareAtPrice: 250000,
  categoryId: 1,
  categorySlug: "hoodie",
  categoryTitle: "هودی",
  available: true,
  createdAt: "2026-09-14 10:00:00",
  colors: [
    { id: 10, name: "مشکی", hexCode: "#000000", sortOrder: 0 },
    { id: 11, name: "کرم", hexCode: "#eaded4", sortOrder: 1 },
  ],
  variants: [
    {
      colorId: 10,
      size: "M",
      sku: "BLACK-M",
      stock: 3,
      available: true,
    },
    {
      colorId: 11,
      size: "L",
      sku: "CREAM-L",
      stock: 0,
      available: false,
    },
  ],
  images: [
    { id: 30, path: "/general.webp", alt: "تصویر عمومی", sortOrder: 0 },
    {
      id: 31,
      colorId: 10,
      path: "/black.webp",
      alt: "تصویر مشکی",
      sortOrder: 0,
    },
    {
      id: 32,
      colorId: 11,
      path: "/cream.webp",
      alt: "تصویر کرم",
      sortOrder: 0,
    },
  ],
};

afterEach(cleanup);

describe("ProductDetailView", () => {
  it("starts with the first color that has stock", () => {
    const productWithLaterStock = {
      ...product,
      variants: product.variants.map((variant) => ({
        ...variant,
        stock: variant.colorId === 11 ? 2 : 0,
        available: variant.colorId === 11,
      })),
    };

    render(<ProductDetailView product={productWithLaterStock} />);

    expect(screen.getByRole("button", { name: "رنگ کرم" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(screen.getByRole("img", { name: "تصویر کرم" })).toBeInTheDocument();
    expect(screen.getByText("سایز را انتخاب کنید")).toBeInTheDocument();
  });

  it("switches color images and reports independent size stock", () => {
    render(<ProductDetailView product={product} />);

    expect(screen.getByRole("img", { name: "تصویر مشکی" })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "تصویر عمومی" })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "رنگ کرم" }));

    expect(screen.getByRole("img", { name: "تصویر کرم" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "سایز L" })).toBeDisabled();
    expect(screen.getByText("ناموجود")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "افزودن به سبد خرید" }),
    ).toBeDisabled();
  });
});
