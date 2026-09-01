import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Header } from "../header";

describe("Header", () => {
  it("shows the store identity and primary shopping actions", () => {
    render(<Header />);

    expect(screen.getByRole("img", { name: "لوگوی دیا گالری" })).toBeInTheDocument();
      expect(screen.getByRole("img", { name: "لوگوی دیا گالری" })).toHaveAttribute("width", "1024");
      expect(screen.getByRole("img", { name: "لوگوی دیا گالری" })).toHaveAttribute("height", "1024");
    expect(screen.getByRole("link", { name: "فروشگاه" })).toHaveAttribute("href", "/shop");
    expect(screen.getByRole("link", { name: "علاقه‌مندی‌ها" })).toHaveAttribute("href", "/wishlist");
    expect(screen.getByRole("link", { name: "سبد خرید" })).toHaveAttribute("href", "/cart");
    expect(screen.getByRole("link", { name: "حساب کاربری" })).toHaveAttribute("href", "/account");
  });
});
