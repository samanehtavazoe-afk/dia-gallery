import type { CatalogDatabase } from "./database";

export type CatalogCategory = {
  id: number;
  slug: string;
  title: string;
  imagePath?: string;
  imageAlt?: string;
  sortOrder: number;
};

export type CatalogProduct = {
  id: number;
  slug: string;
  name: string;
  brand: string;
  description: string;
  price: number;
  compareAtPrice?: number;
  categoryId: number;
  categorySlug: string;
  categoryTitle: string;
  available: boolean;
};

type CategoryRow = {
  id: number;
  slug: string;
  title: string;
  image_path: string | null;
  image_alt: string | null;
  sort_order: number;
};

type ProductRow = {
  id: number;
  slug: string;
  name: string;
  brand: string;
  description: string;
  price: number;
  compare_at_price: number | null;
  category_id: number;
  category_slug: string;
  category_title: string;
  total_stock: number;
};

function mapCategory(row: CategoryRow): CatalogCategory {
  return {
    id: row.id,
    slug: row.slug,
    title: row.title,
    imagePath: row.image_path ?? undefined,
    imageAlt: row.image_alt ?? undefined,
    sortOrder: row.sort_order,
  };
}

function mapProduct(row: ProductRow): CatalogProduct {
  const compareAtPrice =
    row.compare_at_price !== null && row.compare_at_price > row.price
      ? row.compare_at_price
      : undefined;

  return {
    id: row.id,
    slug: row.slug,
    name: row.name,
    brand: row.brand,
    description: row.description,
    price: row.price,
    compareAtPrice,
    categoryId: row.category_id,
    categorySlug: row.category_slug,
    categoryTitle: row.category_title,
    available: row.total_stock > 0,
  };
}

const productSelect = `
  SELECT
    p.id,
    p.slug,
    p.name,
    p.brand,
    p.description,
    p.price,
    p.compare_at_price,
    p.category_id,
    c.slug AS category_slug,
    c.title AS category_title,
    COALESCE(SUM(
      CASE
        WHEN pv.is_active = 1 THEN pv.stock
        ELSE 0
      END
    ), 0) AS total_stock
  FROM products p
  JOIN categories c ON c.id = p.category_id
  LEFT JOIN product_variants pv ON pv.product_id = p.id
`;

const productGroupBy = `
  GROUP BY
    p.id,
    p.slug,
    p.name,
    p.brand,
    p.description,
    p.price,
    p.compare_at_price,
    p.category_id,
    c.slug,
    c.title
`;

export function getActiveCategories(db: CatalogDatabase): CatalogCategory[] {
  const rows = db
    .prepare(`
      SELECT id, slug, title, image_path, image_alt, sort_order
      FROM categories
      WHERE is_active = 1
      ORDER BY sort_order, id
    `)
    .all() as CategoryRow[];

  return rows.map(mapCategory);
}

export function getActiveProducts(db: CatalogDatabase): CatalogProduct[] {
  const rows = db
    .prepare(`
      ${productSelect}
      WHERE p.is_active = 1
        AND c.is_active = 1
      ${productGroupBy}
      ORDER BY p.created_at DESC, p.id DESC
    `)
    .all() as ProductRow[];

  return rows.map(mapProduct);
}

export function getActiveProductsByCategory(
  db: CatalogDatabase,
  categorySlug: string,
): CatalogProduct[] {
  const rows = db
    .prepare(`
      ${productSelect}
      WHERE p.is_active = 1
        AND c.is_active = 1
        AND c.slug = ?
      ${productGroupBy}
      ORDER BY p.created_at DESC, p.id DESC
    `)
    .all(categorySlug) as ProductRow[];

  return rows.map(mapProduct);
}

export function getProductBySlug(
  db: CatalogDatabase,
  slug: string,
): CatalogProduct | null {
  const row = db
    .prepare(`
      ${productSelect}
      WHERE p.is_active = 1
        AND c.is_active = 1
        AND p.slug = ?
      ${productGroupBy}
      LIMIT 1
    `)
    .get(slug) as ProductRow | undefined;

  return row ? mapProduct(row) : null;
}
