import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CategoryGrid } from "../category-grid";

describe("CategoryGrid", () => {
  it("renders the five approved product categories with their images", () => {
    render(
      <CategoryGrid
        categories={[
          { slug: "women-underwear", title: "لباس زیر زنانه", image: "/categories/women-underwear.jpg", imageAlt: "لباس زیر زنانه مشکی" },
          { slug: "men-underwear", title: "لباس زیر مردانه", image: "/categories/men-underwear.jpg", imageAlt: "لباس زیر مردانه خاکستری" },
          { slug: "men-undershirt", title: "زیرپوش مردانه", image: "/categories/men-undershirt.png", imageAlt: "زیرپوش مردانه طوسی" },
          { slug: "hoodie", title: "هودی", image: "/categories/hoodie.png", imageAlt: "هودی مینیمال" },
          { slug: "shoe-holder", title: "هولدر کفش", image: "/categories/shoe-holder.png", imageAlt: "هولدر داخل کفش زنانه و مردانه" },
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

