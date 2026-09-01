import { describe, expect, it } from "vitest";
import { buildHomepageCollections, products } from "./storefront-data";

describe("buildHomepageCollections", () => {
  it("keeps homepage product sections compact and free of duplicates", () => {
    const result = buildHomepageCollections(products, 0);
    const slugs = [
      ...result.today,
      ...result.latest,
      ...result.discounted,
    ].map((product) => product.slug);

    expect(result.today).toHaveLength(1);
    expect(result.latest.length).toBeLessThanOrEqual(4);
    expect(new Set(slugs).size).toBe(slugs.length);
  });

  it("only exposes products with a real discount", () => {
    const result = buildHomepageCollections(products, 0);

    expect(
      result.discounted.every(
        (product) =>
          product.compareAtPrice !== undefined &&
          product.compareAtPrice > product.price,
      ),
    ).toBe(true);
  });
});
