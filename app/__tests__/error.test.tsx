import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import ErrorPage from "../error";

describe("ErrorPage", () => {
  it("shows a safe Persian message and retries without exposing details", () => {
    const retry = vi.fn();
    vi.spyOn(console, "error").mockImplementation(() => undefined);

    render(
      <ErrorPage
        error={new Error("private database path")}
        retry={retry}
      />,
    );

    expect(
      screen.getByRole("heading", { name: "مشکلی پیش آمد" }),
    ).toBeInTheDocument();
    expect(screen.queryByText("private database path")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "تلاش دوباره" }));
    expect(retry).toHaveBeenCalledOnce();
  });
});
