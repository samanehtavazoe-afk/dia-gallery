export type StoreCategory = {
  slug: string;
  title: string;
  subtitle: string;
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
  { slug: "women", title: "زنانه", subtitle: "انتخاب‌های روزمره و راحت" },
  { slug: "men", title: "مردانه", subtitle: "مدل‌های کاربردی و باکیفیت" },
  { slug: "shoe-care", title: "قالب و هولدر کفش", subtitle: "برای حفظ فرم بهتر کفش" },
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
