import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CategoryGrid } from "../category-grid";

describe("CategoryGrid", () => {
  it("renders the five approved product categories with their images", () => {
    render(
      <CategoryGrid
        categories={[
          { id: 1, slug: "women-underwear", title: "لباس زیر زنانه", imagePath: "/categories/women-underwear.jpg", imageAlt: "لباس زیر زنانه مشکی", sortOrder: 1 },
          { id: 2, slug: "men-underwear", title: "لباس زیر مردانه", imagePath: "/categories/men-underwear.jpg", imageAlt: "لباس زیر مردانه خاکستری", sortOrder: 2 },
          { id: 3, slug: "men-undershirt", title: "زیرپوش مردانه", imagePath: "/categories/men-undershirt.png", imageAlt: "زیرپوش مردانه طوسی", sortOrder: 3 },
          { id: 4, slug: "hoodie", title: "هودی", imagePath: "/categories/hoodie.png", imageAlt: "هودی مینیمال", sortOrder: 4 },
          { id: 5, slug: "shoe-holder", title: "هولدر کفش", imagePath: "/categories/shoe-holder.png", imageAlt: "هولدر داخل کفش زنانه و مردانه", sortOrder: 5 },
        ]}
      />,
    );

    expect(screen.getByRole("link", { name: "لباس زیر زنانه" })).toHaveAttribute("href", "/category/women-underwear");
    expect(screen.getByRole("link", { name: "لباس زیر مردانه" })).toHaveAttribute("href", "/category/men-underwear");
    expect(screen.getByRole("link", { name: "زیرپوش مردانه" })).toHaveAttribute("href", "/category/men-undershirt");
    expect(screen.getByRole("link", { name: "هودی" })).toHaveAttribute("href", "/category/hoodie");
    expect(screen.getByRole("link", { name: "هولدر کفش" })).toHaveAttribute("href", "/category/shoe-holder");
    expect(screen.getByRole("img", { name: "لباس زیر زنانه مشکی" })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "هولدر داخل کفش زنانه و مردانه" })).toBeInTheDocument();
  });
});

