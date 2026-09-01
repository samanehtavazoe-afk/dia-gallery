import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Home from "../page";

describe("Home", () => {
  it("composes the complete phase-one storefront homepage", () => {
    render(<Home />);

    expect(screen.getByRole("banner")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "انتخاب خوب، خرید آسان" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "راحت‌تر انتخاب کن" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "منتخب امروز" })).toBeInTheDocument();
      expect(screen.getByRole("heading", { name: "جدیدترین‌ها" })).toBeInTheDocument();
    expect(screen.getByLabelText("مزایای خرید از دیا گالری")).toBeInTheDocument();
    expect(screen.getByRole("contentinfo")).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "دسترسی سریع موبایل" })).toBeInTheDocument();
  });
});
