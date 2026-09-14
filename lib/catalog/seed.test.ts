import { describe, expect, it } from "vitest";
import { migrateCatalogDatabase, openCatalogDatabase } from "./database";
import { seedCatalogDatabase } from "./seed";

describe("catalog seed", () => {
  it("seeds the approved categories and sample products without duplicates", () => {
    const db = openCatalogDatabase(":memory:");
    migrateCatalogDatabase(db);

    seedCatalogDatabase(db);
    seedCatalogDatabase(db);

    const categories = db
      .prepare("SELECT slug, title FROM categories ORDER BY sort_order, id")
      .all();

    expect(categories).toEqual([
      { slug: "women-underwear", title: "لباس زیر زنانه" },
      { slug: "men-underwear", title: "لباس زیر مردانه" },
      { slug: "men-undershirt", title: "زیرپوش مردانه" },
      { slug: "hoodie", title: "هودی" },
      { slug: "shoe-holder", title: "هولدر کفش" },
    ]);

    const products = db
      .prepare(`
        SELECT p.slug, c.slug AS category_slug
        FROM products p
        JOIN categories c ON c.id = p.category_id
        ORDER BY p.id
      `)
      .all();

    expect(products).toEqual([
      { slug: "women-essential-01", category_slug: "women-underwear" },
      { slug: "men-essential-01", category_slug: "men-underwear" },
      { slug: "nobonian-holder-01", category_slug: "shoe-holder" },
    ]);

    expect(
      db.prepare("SELECT COUNT(*) AS count FROM categories").get(),
    ).toEqual({ count: 5 });

    expect(
      db.prepare("SELECT COUNT(*) AS count FROM products").get(),
    ).toEqual({ count: 3 });

    db.close();
  });
});
