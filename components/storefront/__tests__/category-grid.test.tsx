import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CategoryGrid } from "../category-grid";

describe("CategoryGrid", () => {
  it("renders simple category labels without descriptive subtitles", () => {
    render(
      <CategoryGrid
        categories={[
          { slug: "women", title: "زنانه", subtitle: "انتخاب زنانه" },
          { slug: "men", title: "مردانه", subtitle: "انتخاب مردانه" },
          { slug: "shoe-care", title: "هولدر کفش", subtitle: "برای حفظ فرم بهتر کفش" },
        ]}
      />,
    );

    expect(screen.getByRole("link", { name: "زنانه" })).toHaveAttribute("href", "/category/women");
    expect(screen.getByRole("link", { name: "مردانه" })).toHaveAttribute("href", "/category/men");
    expect(screen.getByRole("link", { name: "هولدر کفش" })).toHaveAttribute("href", "/category/shoe-care");
    expect(screen.queryByText("انتخاب زنانه")).not.toBeInTheDocument();
    expect(screen.queryByText("انتخاب مردانه")).not.toBeInTheDocument();
    expect(screen.queryByText("برای حفظ فرم بهتر کفش")).not.toBeInTheDocument();
  });
});
