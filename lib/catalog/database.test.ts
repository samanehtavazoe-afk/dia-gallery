import { describe, expect, it } from "vitest";
import { migrateCatalogDatabase, openCatalogDatabase } from "./database";

describe("catalog database", () => {
  it("creates the catalog tables and enables foreign keys", () => {
    const db = openCatalogDatabase(":memory:");

    migrateCatalogDatabase(db);

    const tables = db
      .prepare(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name",
      )
      .all()
      .map((row: any) => row.name);

    expect(tables).toEqual([
      "categories",
      "product_colors",
      "product_images",
      "product_variants",
      "products",
    ]);

    expect(db.pragma("foreign_keys", { simple: true })).toBe(1);

    db.close();
  });
});
