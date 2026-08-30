import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TrustStrip } from "../trust-strip";

describe("TrustStrip", () => {
  it("communicates the key purchase assurances", () => {
    render(<TrustStrip />);

    expect(screen.getByText("ارسال مطمئن")).toBeInTheDocument();
    expect(screen.getByText("تضمین اصالت")).toBeInTheDocument();
    expect(screen.getByText("پشتیبانی خرید")).toBeInTheDocument();
  });
});
