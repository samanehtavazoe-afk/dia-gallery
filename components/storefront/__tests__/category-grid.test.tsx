import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CategoryGrid } from "../category-grid";

describe("CategoryGrid", () => {
  it("renders each supplied category as a navigable card", () => {
    render(
      <CategoryGrid
        categories={[
          { slug: "women", title: "زنانه", subtitle: "انتخاب زنانه" },
          { slug: "men", title: "مردانه", subtitle: "انتخاب مردانه" },
        ]}
      />,
    );

    expect(screen.getByRole("link", { name: /زنانه/ })).toHaveAttribute("href", "/category/women");
    expect(screen.getByRole("link", { name: /مردانه/ })).toHaveAttribute("href", "/category/men");
  });
});
