import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Hero } from "../hero";

describe("Hero", () => {
  it("presents Diaa Gallery as a store for both women and men", () => {
    render(<Hero />);

    expect(screen.getByRole("heading", { name: "انتخاب خوب، خرید آسان" })).toBeInTheDocument();
      expect(screen.queryByRole("link", { name: "زنانه" })).not.toBeInTheDocument();
      expect(screen.queryByRole("link", { name: "مردانه" })).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "مشاهده محصولات" })).toHaveAttribute("href", "/shop");
      expect(screen.queryByRole("link", { name: "دسته‌بندی‌ها" })).not.toBeInTheDocument();
  });
});
