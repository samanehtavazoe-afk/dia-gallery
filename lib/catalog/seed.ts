import type { CatalogDatabase } from "./database";

const seedCategories = [
  {
    slug: "women-underwear",
    title: "لباس زیر زنانه",
    imagePath: "/categories/women-underwear.webp",
    imageAlt: "لباس زیر زنانه مشکی",
    sortOrder: 1,
  },
  {
    slug: "men-underwear",
    title: "لباس زیر مردانه",
    imagePath: "/categories/men-underwear.webp",
    imageAlt: "لباس زیر مردانه خاکستری",
    sortOrder: 2,
  },
  {
    slug: "men-undershirt",
    title: "زیرپوش مردانه",
    imagePath: "/categories/men-undershirt.webp",
    imageAlt: "زیرپوش مردانه طوسی",
    sortOrder: 3,
  },
  {
    slug: "hoodie",
    title: "هودی",
    imagePath: "/categories/hoodie.webp",
    imageAlt: "هودی مینیمال",
    sortOrder: 4,
  },
  {
    slug: "shoe-holder",
    title: "هولدر کفش",
    imagePath: "/categories/shoe-holder-cream.webp",
    imageAlt: "هولدر داخل کفش زنانه و مردانه",
    sortOrder: 5,
  },
] as const;

const seedProducts = [
  {
    slug: "women-essential-01",
    name: "محصول زنانه منتخب",
    brand: "Diaa Selection",
    description: "محصول نمونه برای راه‌اندازی کاتالوگ دیا گالری.",
    price: 285000,
    compareAtPrice: null,
    categorySlug: "women-underwear",
    color: "مشکی",
    hexCode: "#171615",
    size: "M",
    sku: "DIA-WOMEN-01-BLK-M",
    imagePath: "/categories/women-underwear.webp",
    imageAlt: "محصول زنانه منتخب مشکی",
  },
  {
    slug: "men-essential-01",
    name: "محصول مردانه منتخب",
    brand: "Bodyguard",
    description: "محصول نمونه برای راه‌اندازی کاتالوگ دیا گالری.",
    price: 285000,
    compareAtPrice: 320000,
    categorySlug: "men-underwear",
    color: "خاکستری",
    hexCode: "#777777",
    size: "L",
    sku: "DIA-MEN-01-GRY-L",
    imagePath: "/categories/men-underwear.webp",
    imageAlt: "محصول مردانه منتخب خاکستری",
  },
  {
    slug: "nobonian-holder-01",
    name: "قالب و هولدر کفش",
    brand: "NOBONIAN",
    description: "هولدر کفش نمونه برای راه‌اندازی کاتالوگ دیا گالری.",
    price: 100000,
    compareAtPrice: null,
    categorySlug: "shoe-holder",
    color: "مشکی",
    hexCode: "#171615",
    size: "تک‌سایز",
    sku: "NOBONIAN-HOLDER-01",
    imagePath: "/categories/shoe-holder-cream.webp",
    imageAlt: "هولدر داخل کفش زنانه و مردانه",
  },
] as const;

export function seedCatalogDatabase(db: CatalogDatabase) {
  const seedKey = "catalog-foundation-v1";

  if (
    db.prepare("SELECT 1 FROM catalog_seed_runs WHERE seed_key = ?").get(seedKey)
  ) {
    return;
  }

  const insertCategory = db.prepare(`
    INSERT INTO categories (
      slug,
      title,
      image_path,
      image_alt,
      sort_order,
      is_active
    )
    VALUES (
      @slug,
      @title,
      @imagePath,
      @imageAlt,
      @sortOrder,
      1
    )
  `);

  const getCategoryId = db.prepare(
    "SELECT id FROM categories WHERE slug = ?",
  );

  const insertProduct = db.prepare(`
    INSERT INTO products (
      slug,
      name,
      brand,
      description,
      price,
      compare_at_price,
      category_id,
      is_active
    )
    VALUES (
      @slug,
      @name,
      @brand,
      @description,
      @price,
      @compareAtPrice,
      @categoryId,
      1
    )
  `);

  const insertColor = db.prepare(`
    INSERT INTO product_colors (product_id, name, hex_code, sort_order)
    VALUES (?, ?, ?, 1)
  `);
  const insertVariant = db.prepare(`
    INSERT INTO product_variants (product_id, color_id, size, sku, stock)
    VALUES (?, ?, ?, ?, 0)
  `);
  const insertImage = db.prepare(`
    INSERT INTO product_images (product_id, color_id, path, alt, sort_order)
    VALUES (?, ?, ?, ?, 1)
  `);

  const seed = db.transaction(() => {
    for (const category of seedCategories) {
      insertCategory.run(category);
    }

    for (const product of seedProducts) {
      const category = getCategoryId.get(product.categorySlug) as
        | { id: number }
        | undefined;

      if (!category) {
        throw new Error(
          `Missing seed category for product: ${product.categorySlug}`,
        );
      }

      const productResult = insertProduct.run({
        slug: product.slug,
        name: product.name,
        brand: product.brand,
        description: product.description,
        price: product.price,
        compareAtPrice: product.compareAtPrice,
        categoryId: category.id,
      });

      const productId = Number(productResult.lastInsertRowid);
      const colorResult = insertColor.run(
        productId,
        product.color,
        product.hexCode,
      );
      const colorId = Number(colorResult.lastInsertRowid);

      insertVariant.run(productId, colorId, product.size, product.sku);
      insertImage.run(
        productId,
        colorId,
        product.imagePath,
        product.imageAlt,
      );
    }

    db.prepare("INSERT INTO catalog_seed_runs (seed_key) VALUES (?)").run(
      seedKey,
    );
  });

  seed();
}
