import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Hero } from "../hero";

describe("Hero", () => {
  it("presents an animated product banner with the approved brand line", () => {
    render(<Hero />);

    expect(screen.getByRole("region", { name: "بنر متحرک دیا گالری" })).toBeInTheDocument();
    expect(screen.getByText("DIA GALLERY")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "انتخاب خوب، خرید آسان" })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "منتخب لباس زیر زنانه" })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "منتخب پوشاک مردانه" })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "هولدر کفش زنانه و مردانه" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "مشاهده محصولات" })).toHaveAttribute("href", "/shop");
    expect(screen.queryByRole("link", { name: "زنانه" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "مردانه" })).not.toBeInTheDocument();
  });
});

