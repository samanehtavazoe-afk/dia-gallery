import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/lib/catalog/runtime", () => ({
  loadHomepageCatalog: vi.fn(async () => ({
    categories: [
      {
        id: 1,
        slug: "hoodie",
        title: "هودی",
        imagePath: "/categories/hoodie.webp",
        imageAlt: "هودی",
        sortOrder: 1,
      },
    ],
    collections: {
      today: [
        {
          id: 1,
          slug: "today",
          name: "محصول امروز",
          brand: "Dia",
          description: "",
          price: 100000,
          categoryId: 1,
          categorySlug: "hoodie",
          categoryTitle: "هودی",
          available: false,
          createdAt: "2026-09-14",
        },
      ],
      latest: [
        {
          id: 2,
          slug: "latest",
          name: "محصول جدید",
          brand: "Dia",
          description: "",
          price: 110000,
          categoryId: 1,
          categorySlug: "hoodie",
          categoryTitle: "هودی",
          available: false,
          createdAt: "2026-09-14",
        },
      ],
      discounted: [],
    },
  })),
}));

import Home from "../page";

describe("Home", () => {
  it("composes the database-backed storefront homepage", async () => {
    render(await Home());

    expect(screen.getByRole("banner")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "انتخاب خوب، خرید آسان" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "راحت‌تر انتخاب کن" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "منتخب امروز" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "جدیدترین‌ها" })).toBeInTheDocument();
    expect(screen.getByText("محصول امروز")).toBeInTheDocument();
    expect(screen.getByText("محصول جدید")).toBeInTheDocument();
    expect(
      screen.queryByRole("heading", { name: "تخفیف‌دارها" }),
    ).not.toBeInTheDocument();
    expect(screen.getByLabelText("مزایای خرید از دیا گالری")).toBeInTheDocument();
    expect(screen.getByRole("contentinfo")).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "دسترسی سریع موبایل" })).toBeInTheDocument();
  });
});
