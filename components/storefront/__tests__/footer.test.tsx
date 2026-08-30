import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Footer } from "../footer";

describe("Footer", () => {
  it("provides store, support, and legal navigation", () => {
    render(<Footer />);

    expect(screen.getByText("DIAA GALLERY")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "فروشگاه" })).toHaveAttribute("href", "/shop");
    expect(screen.getByRole("link", { name: "تماس با ما" })).toHaveAttribute("href", "/contact");
    expect(screen.getByRole("link", { name: "حریم خصوصی" })).toHaveAttribute("href", "/privacy");
  });
});
