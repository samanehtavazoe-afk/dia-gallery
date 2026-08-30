import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Hero } from "../hero";

describe("Hero", () => {
  it("presents Diaa Gallery as a store for both women and men", () => {
    render(<Hero />);

    expect(screen.getByRole("heading", { name: "انتخاب برای خانم‌ها و آقایان" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "زنانه" })).toHaveAttribute("href", "/category/women");
    expect(screen.getByRole("link", { name: "مردانه" })).toHaveAttribute("href", "/category/men");
    expect(screen.getByRole("link", { name: "مشاهده محصولات" })).toHaveAttribute("href", "/shop");
  });
});
