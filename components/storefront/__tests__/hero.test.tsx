import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Hero } from "../hero";

describe("Hero", () => {
  it("presents an animated homewear campaign without category product photos", () => {
    render(<Hero />);

    expect(screen.getByRole("region", { name: "بنر متحرک دیا گالری" })).toBeInTheDocument();
    expect(screen.getByText("DIA GALLERY")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "انتخاب خوب، خرید آسان" })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "استایل راحتی زنانه دیا گالری" })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "استایل راحتی مردانه دیا گالری" })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "استایل راحتی زنانه و مردانه دیا گالری" })).toBeInTheDocument();
    expect(screen.queryByRole("img", { name: "منتخب لباس زیر زنانه" })).not.toBeInTheDocument();
    expect(screen.queryByRole("img", { name: "هولدر کفش زنانه و مردانه" })).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "مشاهده محصولات" })).toHaveAttribute("href", "/shop");
    expect(screen.queryByRole("link", { name: "زنانه" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "مردانه" })).not.toBeInTheDocument();
  });
});
