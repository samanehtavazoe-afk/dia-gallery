import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import RootLayout, { metadata } from "../layout";

describe("RootLayout", () => {
  it("uses the Diaa Gallery Persian identity", () => {
    expect(metadata.title).toBe("دیا گالری | فروشگاه آنلاین");
    expect(metadata.description).toContain("دیا گالری");

    const markup = renderToStaticMarkup(
      <RootLayout>
        <main>محتوا</main>
      </RootLayout>,
    );

    expect(markup).toContain('<html lang="fa" dir="rtl">');
  });
});
