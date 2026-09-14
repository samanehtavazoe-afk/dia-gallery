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

export type CatalogColor = {
  id: number;
  name: string;
  hexCode?: string;
  sortOrder: number;
};

export type CatalogVariant = {
  colorId: number;
  size: string;
  sku: string;
  stock: number;
  available: boolean;
};

export type CatalogImage = {
  id: number;
  colorId?: number;
  path: string;
  alt: string;
  sortOrder: number;
};

export type CatalogProductDetails = CatalogProduct & {
  colors: CatalogColor[];
  variants: CatalogVariant[];
  images: CatalogImage[];
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

type ColorRow = {
  id: number;
  name: string;
  hex_code: string | null;
  sort_order: number;
};

type VariantRow = {
  color_id: number;
  size: string;
  sku: string;
  stock: number;
};

type ImageRow = {
  id: number;
  color_id: number | null;
  path: string;
  alt: string;
  sort_order: number;
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

export function getProductDetailsBySlug(
  db: CatalogDatabase,
  slug: string,
): CatalogProductDetails | null {
  const product = getProductBySlug(db, slug);

  if (!product) {
    return null;
  }

  const colorRows = db
    .prepare(`
      SELECT id, name, hex_code, sort_order
      FROM product_colors
      WHERE product_id = ?
      ORDER BY sort_order, id
    `)
    .all(product.id) as ColorRow[];

  const variantRows = db
    .prepare(`
      SELECT color_id, size, sku, stock
      FROM product_variants
      WHERE product_id = ?
        AND is_active = 1
      ORDER BY id
    `)
    .all(product.id) as VariantRow[];

  const imageRows = db
    .prepare(`
      SELECT id, color_id, path, alt, sort_order
      FROM product_images
      WHERE product_id = ?
      ORDER BY sort_order, id
    `)
    .all(product.id) as ImageRow[];

  return {
    ...product,
    colors: colorRows.map((row) => ({
      id: row.id,
      name: row.name,
      hexCode: row.hex_code ?? undefined,
      sortOrder: row.sort_order,
    })),
    variants: variantRows.map((row) => ({
      colorId: row.color_id,
      size: row.size,
      sku: row.sku,
      stock: row.stock,
      available: row.stock > 0,
    })),
    images: imageRows.map((row) => ({
      id: row.id,
      colorId: row.color_id ?? undefined,
      path: row.path,
      alt: row.alt,
      sortOrder: row.sort_order,
    })),
  };
}

export function selectImagesForColor(
  images: CatalogImage[],
  colorId: number,
): CatalogImage[] {
  const colorImages = images.filter((image) => image.colorId === colorId);
  const generalImages = images.filter((image) => image.colorId === undefined);

  return [...colorImages, ...generalImages];
}
