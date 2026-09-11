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
    expect(screen.getByRole("link", { name: "لباس زیر زنانه" })).toHaveAttribute("href", "/category/women-underwear");
    expect(screen.getByRole("link", { name: "لباس زیر مردانه" })).toHaveAttribute("href", "/category/men-underwear");
    expect(screen.getByRole("link", { name: "زیرپوش مردانه" })).toHaveAttribute("href", "/category/men-undershirt");
    expect(screen.getByRole("link", { name: "هودی" })).toHaveAttribute("href", "/category/hoodie");
    expect(screen.getByRole("link", { name: "هولدر کفش" })).toHaveAttribute("href", "/category/shoe-holder");
    expect(screen.queryByRole("link", { name: "زنانه" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "مردانه" })).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "علاقه‌مندی‌ها" })).toHaveAttribute("href", "/wishlist");
    expect(screen.getByRole("link", { name: "سبد خرید" })).toHaveAttribute("href", "/cart");
    expect(screen.getByRole("link", { name: "حساب کاربری" })).toHaveAttribute("href", "/account");
  });
});

