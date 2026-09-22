import { describe, expect, it } from "vitest";
import { migrateCatalogDatabase, openCatalogDatabase } from "./database";
import { seedCatalogDatabase } from "./seed";
import {
  getActiveCategories,
  getActiveCategoryBySlug,
  getActiveProducts,
  getActiveProductsByCategory,
  getHomepageCollections,
  getProductBySlug,
} from "./repository";

function createSeededDatabase() {
  const db = openCatalogDatabase(":memory:");
  migrateCatalogDatabase(db);
  seedCatalogDatabase(db);
  return db;
}

describe("catalog repository", () => {
  it("returns only active categories and products", () => {
    const db = createSeededDatabase();

    db.prepare("UPDATE categories SET is_active = 0 WHERE slug = ?").run("hoodie");
    db.prepare("UPDATE products SET is_active = 0 WHERE slug = ?").run("men-essential-01");

    const categories = getActiveCategories(db);
    const products = getActiveProducts(db);

    expect(categories.some((category) => category.slug === "hoodie")).toBe(false);
    expect(products.some((product) => product.slug === "men-essential-01")).toBe(false);

    db.close();
  });

  it("filters active products by category slug", () => {
    const db = createSeededDatabase();

    const products = getActiveProductsByCategory(db, "women-underwear");

    expect(products.map((product) => product.slug)).toEqual([
      "women-essential-01",
    ]);

    db.close();
  });

  it("finds active categories by slug and hides inactive categories", () => {
    const db = createSeededDatabase();

    expect(getActiveCategoryBySlug(db, "shoe-holder")?.title).toBe("هولدر کفش");
    db.prepare("UPDATE categories SET is_active = 0 WHERE slug = ?").run(
      "shoe-holder",
    );
    expect(getActiveCategoryBySlug(db, "shoe-holder")).toBeNull();

    db.close();
  });

  it("finds an active product by slug and hides inactive products", () => {
    const db = createSeededDatabase();

    expect(getProductBySlug(db, "nobonian-holder-01")?.brand).toBe("NOBONIAN");

    db.prepare("UPDATE products SET is_active = 0 WHERE slug = ?").run(
      "nobonian-holder-01",
    );

    expect(getProductBySlug(db, "nobonian-holder-01")).toBeNull();

    db.close();
  });

  it("does not expose an invalid compare-at price", () => {
    const db = createSeededDatabase();

    db.pragma("ignore_check_constraints = ON");
    db.prepare(
      "UPDATE products SET compare_at_price = price WHERE slug = ?",
    ).run("women-essential-01");
    db.pragma("ignore_check_constraints = OFF");

    expect(getProductBySlug(db, "women-essential-01")?.compareAtPrice).toBeUndefined();

    db.close();
  });

  it("returns a primary image, creation time, and stock-backed availability", () => {
    const db = createSeededDatabase();

    const beforeStock = getProductBySlug(db, "men-essential-01");
    expect(beforeStock?.image?.path).toBe("/categories/men-underwear.webp");
    expect(beforeStock?.createdAt).toEqual(expect.any(String));
    expect(beforeStock?.available).toBe(false);

    db.prepare("UPDATE product_variants SET stock = 4 WHERE sku = ?").run(
      "DIA-MEN-01-GRY-L",
    );
    expect(getProductBySlug(db, "men-essential-01")?.available).toBe(true);

    db.close();
  });

  it("builds compact homepage sections without duplicate products", () => {
    const db = createSeededDatabase();
    const result = getHomepageCollections(db, 0);
    const slugs = [...result.today, ...result.latest, ...result.discounted].map(
      (product) => product.slug,
    );

    expect(result.today).toHaveLength(1);
    expect(result.latest.length).toBeLessThanOrEqual(4);
    expect(new Set(slugs).size).toBe(slugs.length);
    expect(
      result.discounted.every(
        (product) =>
          product.compareAtPrice !== undefined &&
          product.compareAtPrice > product.price,
      ),
    ).toBe(true);

    db.close();
  });
});
