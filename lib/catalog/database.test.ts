import { existsSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import type { CatalogDatabase } from "./database";
import {
  migrateCatalogDatabase,
  openCatalogDatabase,
  resolveCatalogDatabasePath,
} from "./database";

let database: CatalogDatabase | undefined;
let directory: string | undefined;

afterEach(() => {
  database?.close();
  database = undefined;

  if (directory) {
    rmSync(directory, { recursive: true, force: true });
    directory = undefined;
  }
});

describe("catalog database", () => {
  it("uses the deployment database path by default in production", () => {
    expect(
      resolveCatalogDatabasePath({ NODE_ENV: "production" }, "C:/app"),
    ).toBe("/var/lib/dia-gallery/data/dia-gallery.sqlite");
  });

  it("creates the catalog tables and enables foreign keys", () => {
    database = openCatalogDatabase(":memory:");

    migrateCatalogDatabase(database);

    const tables = database
      .prepare(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name",
      )
      .all()
      .map((row) => (row as { name: string }).name);

    expect(tables).toEqual([
      "categories",
      "product_colors",
      "product_images",
      "product_variants",
      "products",
    ]);

    expect(database.pragma("foreign_keys", { simple: true })).toBe(1);
  });

  it("rejects invalid catalog relationships and inventory constraints", () => {
    database = openCatalogDatabase(":memory:");
    migrateCatalogDatabase(database);

    expect(() =>
      database!.prepare(
        "INSERT INTO products (slug, name, brand, description, price, category_id) VALUES (?, ?, ?, ?, ?, ?)",
      ).run("orphan-product", "محصول", "Dia", "شرح", 100000, 999),
    ).toThrow();

    const category = database
      .prepare(
        "INSERT INTO categories (slug, title, image_path, image_alt) VALUES (?, ?, ?, ?)",
      )
      .run("women", "زنانه", "/women.webp", "زنانه");

    expect(() =>
      database!.prepare(
        "INSERT INTO products (slug, name, brand, description, price, category_id) VALUES (?, ?, ?, ?, ?, ?)",
      ).run(
        "bad-price",
        "نامعتبر",
        "Dia",
        "شرح",
        -1,
        category.lastInsertRowid,
      ),
    ).toThrow();

    const product = database
      .prepare(
        "INSERT INTO products (slug, name, brand, description, price, category_id) VALUES (?, ?, ?, ?, ?, ?)",
      )
      .run(
        "valid-product",
        "محصول",
        "Dia",
        "شرح",
        100000,
        category.lastInsertRowid,
      );
    const color = database
      .prepare("INSERT INTO product_colors (product_id, name) VALUES (?, ?)")
      .run(product.lastInsertRowid, "مشکی");

    expect(() =>
      database!.prepare(
        "INSERT INTO product_variants (product_id, color_id, size, sku, stock) VALUES (?, ?, ?, ?, ?)",
      ).run(product.lastInsertRowid, 999, "M", "SKU-ORPHAN", 1),
    ).toThrow();

    database
      .prepare(
        "INSERT INTO product_variants (product_id, color_id, size, sku, stock) VALUES (?, ?, ?, ?, ?)",
      )
      .run(product.lastInsertRowid, color.lastInsertRowid, "M", "SKU-1", 2);

    expect(() =>
      database!.prepare(
        "INSERT INTO product_variants (product_id, color_id, size, sku, stock) VALUES (?, ?, ?, ?, ?)",
      ).run(product.lastInsertRowid, color.lastInsertRowid, "L", "SKU-1", 1),
    ).toThrow();
    expect(() =>
      database!.prepare(
        "INSERT INTO product_variants (product_id, color_id, size, sku, stock) VALUES (?, ?, ?, ?, ?)",
      ).run(product.lastInsertRowid, color.lastInsertRowid, "L", "SKU-2", -1),
    ).toThrow();
    expect(() =>
      database!.prepare(
        "INSERT INTO product_variants (product_id, color_id, size, sku, stock) VALUES (?, ?, ?, ?, ?)",
      ).run(product.lastInsertRowid, color.lastInsertRowid, "M", "SKU-3", 1),
    ).toThrow();
  });

  it("creates parent directories and reopens a persistent WAL database", () => {
    directory = mkdtempSync(join(tmpdir(), "dia-catalog-"));
    const filename = join(directory, "data", "catalog.sqlite");

    database = openCatalogDatabase(filename);
    migrateCatalogDatabase(database);
    database
      .prepare(
        "INSERT INTO categories (slug, title) VALUES (?, ?)",
      )
      .run("persisted", "ماندگار");

    expect(existsSync(filename)).toBe(true);
    expect(database.pragma("journal_mode", { simple: true })).toBe("wal");
    expect(database.pragma("foreign_keys", { simple: true })).toBe(1);

    database.close();
    database = openCatalogDatabase(filename);
    migrateCatalogDatabase(database);

    expect(
      database
        .prepare("SELECT title FROM categories WHERE slug = ?")
        .get("persisted"),
    ).toEqual({ title: "ماندگار" });
    expect(database.pragma("journal_mode", { simple: true })).toBe("wal");
    expect(database.pragma("foreign_keys", { simple: true })).toBe(1);
  });
});
