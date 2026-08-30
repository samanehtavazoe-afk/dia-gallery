import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MobileNav } from "../mobile-nav";

describe("MobileNav", () => {
  it("keeps the main shopping destinations available on small screens", () => {
    render(<MobileNav />);

    expect(screen.getByRole("navigation", { name: "دسترسی سریع موبایل" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "خانه" })).toHaveAttribute("href", "/");
    expect(screen.getByRole("link", { name: "فروشگاه" })).toHaveAttribute("href", "/shop");
    expect(screen.getByRole("link", { name: "علاقه‌مندی‌ها" })).toHaveAttribute("href", "/wishlist");
    expect(screen.getByRole("link", { name: "سبد خرید" })).toHaveAttribute("href", "/cart");
  });
});
