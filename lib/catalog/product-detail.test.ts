import { describe, expect, it } from "vitest";
import { migrateCatalogDatabase, openCatalogDatabase } from "./database";
import {
  getProductDetailsBySlug,
  selectImagesForColor,
} from "./repository";
import { seedCatalogDatabase } from "./seed";

function createDetailedProductDatabase() {
  const db = openCatalogDatabase(":memory:");
  migrateCatalogDatabase(db);
  seedCatalogDatabase(db);

  const product = db
    .prepare("SELECT id FROM products WHERE slug = ?")
    .get("women-essential-01") as { id: number };

  const black = db
    .prepare(
      "INSERT INTO product_colors (product_id, name, hex_code, sort_order) VALUES (?, ?, ?, ?) RETURNING id",
    )
    .get(product.id, "مشکی", "#111111", 1) as { id: number };

  const cream = db
    .prepare(
      "INSERT INTO product_colors (product_id, name, hex_code, sort_order) VALUES (?, ?, ?, ?) RETURNING id",
    )
    .get(product.id, "کرم", "#E8DDCF", 2) as { id: number };

  const insertVariant = db.prepare(
    "INSERT INTO product_variants (product_id, color_id, size, sku, stock, is_active) VALUES (?, ?, ?, ?, ?, ?)",
  );

  insertVariant.run(product.id, black.id, "XL", "WOM-BLK-XL", 3, 1);
  insertVariant.run(product.id, black.id, "2XL", "WOM-BLK-2XL", 0, 1);
  insertVariant.run(product.id, cream.id, "XL", "WOM-CRM-XL", 7, 1);
  insertVariant.run(product.id, cream.id, "3XL", "WOM-CRM-3XL", 9, 0);

  const insertImage = db.prepare(
    "INSERT INTO product_images (product_id, color_id, path, alt, sort_order) VALUES (?, ?, ?, ?, ?)",
  );

  insertImage.run(product.id, null, "/products/women/general.webp", "نمای عمومی محصول", 1);
  insertImage.run(product.id, black.id, "/products/women/black.webp", "محصول مشکی", 1);
  insertImage.run(product.id, cream.id, "/products/women/cream.webp", "محصول کرم", 1);

  return { db, blackId: black.id, creamId: cream.id };
}

describe("product details", () => {
  it("returns colors and independent active variant stock", () => {
    const { db, blackId, creamId } = createDetailedProductDatabase();

    const product = getProductDetailsBySlug(db, "women-essential-01");

    expect(product).not.toBeNull();
    expect(product?.colors.map((color) => color.name)).toEqual(["مشکی", "کرم"]);
    expect(product?.variants).toEqual([
      {
        colorId: blackId,
        size: "XL",
        sku: "WOM-BLK-XL",
        stock: 3,
        available: true,
      },
      {
        colorId: blackId,
        size: "2XL",
        sku: "WOM-BLK-2XL",
        stock: 0,
        available: false,
      },
      {
        colorId: creamId,
        size: "XL",
        sku: "WOM-CRM-XL",
        stock: 7,
        available: true,
      },
    ]);

    db.close();
  });

  it("prioritizes selected-color images and keeps general images available", () => {
    const { db, blackId } = createDetailedProductDatabase();
    const product = getProductDetailsBySlug(db, "women-essential-01");

    expect(product).not.toBeNull();

    const images = selectImagesForColor(product!.images, blackId);

    expect(images.map((image) => image.path)).toEqual([
      "/products/women/black.webp",
      "/products/women/general.webp",
    ]);

    db.close();
  });

  it("returns null for an unknown product slug", () => {
    const { db } = createDetailedProductDatabase();

    expect(getProductDetailsBySlug(db, "missing-product")).toBeNull();

    db.close();
  });
});
