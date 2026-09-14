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
  },
  {
    slug: "men-essential-01",
    name: "محصول مردانه منتخب",
    brand: "Bodyguard",
    description: "محصول نمونه برای راه‌اندازی کاتالوگ دیا گالری.",
    price: 285000,
    compareAtPrice: 320000,
    categorySlug: "men-underwear",
  },
  {
    slug: "nobonian-holder-01",
    name: "قالب و هولدر کفش",
    brand: "NOBONIAN",
    description: "هولدر کفش نمونه برای راه‌اندازی کاتالوگ دیا گالری.",
    price: 100000,
    compareAtPrice: null,
    categorySlug: "shoe-holder",
  },
] as const;

export function seedCatalogDatabase(db: CatalogDatabase) {
  const upsertCategory = db.prepare(`
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
    ON CONFLICT(slug) DO UPDATE SET
      title = excluded.title,
      image_path = excluded.image_path,
      image_alt = excluded.image_alt,
      sort_order = excluded.sort_order
  `);

  const getCategoryId = db.prepare(
    "SELECT id FROM categories WHERE slug = ?",
  );

  const upsertProduct = db.prepare(`
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
    ON CONFLICT(slug) DO UPDATE SET
      name = excluded.name,
      brand = excluded.brand,
      description = excluded.description,
      price = excluded.price,
      compare_at_price = excluded.compare_at_price,
      category_id = excluded.category_id,
      updated_at = CURRENT_TIMESTAMP
  `);

  const seed = db.transaction(() => {
    for (const category of seedCategories) {
      upsertCategory.run(category);
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

      upsertProduct.run({
        slug: product.slug,
        name: product.name,
        brand: product.brand,
        description: product.description,
        price: product.price,
        compareAtPrice: product.compareAtPrice,
        categoryId: category.id,
      });
    }
  });

  seed();
}
