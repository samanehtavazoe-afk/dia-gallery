export type StoreCategory = {
  slug: string;
  title: string;
  subtitle?: string;
};

export type StoreProduct = {
  slug: string;
  title: string;
  brand: string;
  price: number;
  compareAtPrice?: number;
  category: string;
  available: boolean;
};

export const categories: StoreCategory[] = [
  { slug: "women", title: "زنانه" },
  { slug: "men", title: "مردانه" },
  { slug: "shoe-care", title: "هولدر کفش" },
];

export const products: StoreProduct[] = [
  {
    slug: "women-essential-01",
    title: "محصول زنانه منتخب",
    brand: "Diaa Selection",
    price: 285000,
    category: "women",
    available: true,
  },
  {
    slug: "men-essential-01",
    title: "محصول مردانه منتخب",
    brand: "Bodyguard",
    price: 285000,
    compareAtPrice: 320000,
    category: "men",
    available: true,
  },
  {
    slug: "nobonian-holder-01",
    title: "قالب و هولدر کفش",
    brand: "NOBONIAN",
    price: 100000,
    category: "shoe-care",
    available: true,
  },
];

export function buildHomepageCollections(
  allProducts: StoreProduct[],
  dayIndex = Math.floor(Date.now() / 86_400_000),
) {
  const available = allProducts.filter((product) => product.available);
  const selectedIndex = available.length
    ? ((dayIndex % available.length) + available.length) % available.length
    : 0;
  const today = available.length ? [available[selectedIndex]] : [];
  const remaining = available.filter(
    (product) => product.slug !== today[0]?.slug,
  );
  const discounted = remaining.filter(
    (product) =>
      product.compareAtPrice !== undefined &&
      product.compareAtPrice > product.price,
  );
  const discountedSlugs = new Set(
    discounted.map((product) => product.slug),
  );
  const latest = remaining
    .filter((product) => !discountedSlugs.has(product.slug))
    .slice(0, 4);

  return { today, latest, discounted };
}
