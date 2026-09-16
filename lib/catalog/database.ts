import Database from "better-sqlite3";
import { mkdirSync } from "node:fs";
import { dirname, join } from "node:path";

export type CatalogDatabase = InstanceType<typeof Database>;

const defaultDatabasePath = join(process.cwd(), ".data", "dia-gallery.sqlite");

export function openCatalogDatabase(
  path = process.env.DIA_DB_PATH ?? defaultDatabasePath,
) {
  if (path !== ":memory:") {
    mkdirSync(dirname(path), { recursive: true });
  }

  const db = new Database(path);

  db.pragma("foreign_keys = ON");

  if (path !== ":memory:") {
    db.pragma("journal_mode = WAL");
  }

  return db;
}

export function migrateCatalogDatabase(db: CatalogDatabase) {
  db.exec(`
    CREATE TABLE IF NOT EXISTS categories (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      slug TEXT NOT NULL UNIQUE,
      title TEXT NOT NULL,
      image_path TEXT,
      image_alt TEXT,
      sort_order INTEGER NOT NULL DEFAULT 0,
      is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
    );

    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      slug TEXT NOT NULL UNIQUE,
      name TEXT NOT NULL,
      brand TEXT NOT NULL,
      description TEXT NOT NULL DEFAULT '',
      price INTEGER NOT NULL CHECK (price >= 0),
      compare_at_price INTEGER CHECK (
        compare_at_price IS NULL OR compare_at_price > price
      ),
      category_id INTEGER NOT NULL,
      is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (category_id) REFERENCES categories(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
    );

    CREATE TABLE IF NOT EXISTS product_colors (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_id INTEGER NOT NULL,
      name TEXT NOT NULL,
      hex_code TEXT,
      sort_order INTEGER NOT NULL DEFAULT 0,
      UNIQUE (product_id, name),
      FOREIGN KEY (product_id) REFERENCES products(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS product_variants (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_id INTEGER NOT NULL,
      color_id INTEGER NOT NULL,
      size TEXT NOT NULL,
      sku TEXT NOT NULL UNIQUE,
      stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
      is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
      UNIQUE (product_id, color_id, size),
      FOREIGN KEY (product_id) REFERENCES products(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
      FOREIGN KEY (color_id) REFERENCES product_colors(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS product_images (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_id INTEGER NOT NULL,
      color_id INTEGER,
      path TEXT NOT NULL,
      alt TEXT NOT NULL,
      sort_order INTEGER NOT NULL DEFAULT 0,
      FOREIGN KEY (product_id) REFERENCES products(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
      FOREIGN KEY (color_id) REFERENCES product_colors(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_products_category
      ON products(category_id);

    CREATE INDEX IF NOT EXISTS idx_product_colors_product
      ON product_colors(product_id);

    CREATE INDEX IF NOT EXISTS idx_product_variants_product
      ON product_variants(product_id);

    CREATE INDEX IF NOT EXISTS idx_product_images_product
      ON product_images(product_id);
  `);
}
