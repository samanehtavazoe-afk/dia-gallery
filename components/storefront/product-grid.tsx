import type { StoreProduct } from "@/lib/storefront-data";
import { ProductCard } from "./product-card";

export function ProductGrid({ products }: { products: StoreProduct[] }) {
  return (
    <section className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-6 flex items-end justify-between gap-4">
        <div>
          <p className="mb-2 text-sm text-[var(--muted)]">انتخاب‌های پیشنهادی</p>
          <h2 className="text-2xl font-semibold">محصولات منتخب</h2>
        </div>
        <a href="/shop" className="text-sm text-[var(--muted)] transition hover:text-[var(--foreground)]">
          مشاهده همه
        </a>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
        {products.map((product) => (
          <ProductCard key={product.slug} product={product} />
        ))}
      </div>
    </section>
  );
}
