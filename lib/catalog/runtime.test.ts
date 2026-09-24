import { existsSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  loadCategoryCatalog,
  loadHomepageCatalog,
  loadProductCatalog,
} from "./runtime";
import { migrateCatalogDatabase, openCatalogDatabase } from "./database";
import { seedCatalogDatabase } from "./seed";

let directory: string;
let previousDatabasePath: string | undefined;

beforeEach(() => {
  directory = mkdtempSync(join(tmpdir(), "dia-runtime-"));
  previousDatabasePath = process.env.DIA_DB_PATH;
  process.env.DIA_DB_PATH = join(directory, "catalog.sqlite");
});

afterEach(() => {
  if (previousDatabasePath === undefined) {
    delete process.env.DIA_DB_PATH;
  } else {
    process.env.DIA_DB_PATH = previousDatabasePath;
  }
  rmSync(directory, { recursive: true, force: true });
});

describe("catalog runtime loaders", () => {
  it("loads homepage, category, and product data from a closed-per-read database", async () => {
    const database = openCatalogDatabase(process.env.DIA_DB_PATH);
    migrateCatalogDatabase(database);
    seedCatalogDatabase(database);
    database.close();

    const homepage = await loadHomepageCatalog(0);
    const category = await loadCategoryCatalog("shoe-holder");
    const product = await loadProductCatalog("nobonian-holder-01");

    expect(homepage.categories).toHaveLength(5);
    expect(homepage.collections.today).toHaveLength(1);
    expect(category?.category.title).toBe("هولدر کفش");
    expect(category?.products.map((item) => item.slug)).toEqual([
      "nobonian-holder-01",
    ]);
    expect(product?.brand).toBe("NOBONIAN");

    expect(await loadCategoryCatalog("missing-category")).toBeNull();
    expect(await loadProductCatalog("missing-product")).toBeNull();
  });

  it("does not create or seed a missing database during a storefront read", async () => {
    const filename = process.env.DIA_DB_PATH!;

    await expect(loadHomepageCatalog(0)).rejects.toThrow();
    expect(existsSync(filename)).toBe(false);
  });
});
