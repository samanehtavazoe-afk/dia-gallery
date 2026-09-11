import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Footer } from "../footer";

describe("Footer", () => {
  it("provides store, support, and legal navigation", () => {
    render(<Footer />);

    expect(screen.getByText("DIA GALLERY")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "فروشگاه" })).toHaveAttribute("href", "/shop");
    expect(screen.getByRole("link", { name: "لباس زیر زنانه" })).toHaveAttribute("href", "/category/women-underwear");
    expect(screen.getByRole("link", { name: "لباس زیر مردانه" })).toHaveAttribute("href", "/category/men-underwear");
    expect(screen.queryByRole("link", { name: "زنانه" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "مردانه" })).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "تماس با ما" })).toHaveAttribute("href", "/contact");
    expect(screen.getByRole("link", { name: "حریم خصوصی" })).toHaveAttribute("href", "/privacy");
  });
});

