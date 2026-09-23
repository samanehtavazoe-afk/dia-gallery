import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const { notFound, loadCategoryCatalog } = vi.hoisted(() => ({
  notFound: vi.fn(() => {
    throw new Error("NOT_FOUND");
  }),
  loadCategoryCatalog: vi.fn(async (slug: string) =>
    slug === "hoodie"
      ? {
          category: {
            id: 4,
            slug,
            title: "هودی",
            imagePath: "/categories/hoodie.webp",
            imageAlt: "هودی مینیمال",
            sortOrder: 4,
          },
          products: [],
        }
      : null,
  ),
}));

vi.mock("next/navigation", () => ({ notFound }));
vi.mock("@/lib/catalog/runtime", () => ({ loadCategoryCatalog }));

import CategoryPage from "./page";

describe("CategoryPage", () => {
  it("renders an active category and its empty state", async () => {
    render(
      await CategoryPage({ params: Promise.resolve({ slug: "hoodie" }) }),
    );

    expect(screen.getByRole("heading", { name: "هودی" })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "هودی مینیمال" })).toBeInTheDocument();
    expect(
      screen.getByText("در این دسته هنوز محصولی ثبت نشده است."),
    ).toBeInTheDocument();
  });

  it("returns not found for an unknown category", async () => {
    await expect(
      CategoryPage({ params: Promise.resolve({ slug: "missing" }) }),
    ).rejects.toThrow("NOT_FOUND");
    expect(notFound).toHaveBeenCalled();
  });
});
