import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RootLayout, { metadata } from "../layout";

describe("RootLayout", () => {
  it("uses the Diaa Gallery Persian identity", () => {
    expect(metadata.title).toBe("دیا گالری | فروشگاه آنلاین");
    expect(metadata.description).toContain("دیا گالری");

    const { container } = render(
      <RootLayout>
        <main>محتوا</main>
      </RootLayout>,
    );

    const html = container.querySelector("html");
    expect(html).toHaveAttribute("lang", "fa");
    expect(html).toHaveAttribute("dir", "rtl");
  });
});
