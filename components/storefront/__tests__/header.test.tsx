import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Header } from "../header";

describe("Header", () => {
  it("shows the store identity and primary shopping actions", () => {
    render(<Header />);

    expect(screen.getByText("DIAA GALLERY")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "فروشگاه" })).toHaveAttribute("href", "/shop");
    expect(screen.getByRole("link", { name: "علاقه‌مندی‌ها" })).toHaveAttribute("href", "/wishlist");
    expect(screen.getByRole("link", { name: "سبد خرید" })).toHaveAttribute("href", "/cart");
    expect(screen.getByRole("link", { name: "حساب کاربری" })).toHaveAttribute("href", "/account");
  });
});
