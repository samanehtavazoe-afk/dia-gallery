import type { StoreCategory } from "@/lib/storefront-data";

export function CategoryGrid({ categories }: { categories: StoreCategory[] }) {
  return (
    <section className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8" aria-labelledby="categories-title">
      <div className="mb-5 flex items-end justify-between gap-4">
        <div>
          <p className="mb-2 text-xs font-semibold text-[var(--accent)]">دسته‌بندی‌ها</p>
          <h2 id="categories-title" className="text-2xl font-semibold sm:text-3xl">
            راحت‌تر انتخاب کن
          </h2>
        </div>
        <a href="/shop" className="text-sm text-[var(--muted)]">
          مشاهده همه
        </a>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {categories.map((category) => (
          <a
            key={category.slug}
            href={`/category/${category.slug}`}
            className="group flex min-h-24 items-center justify-center rounded-[var(--radius-card)] border border-[var(--line)] bg-white px-3 py-4 text-center transition-transform hover:-translate-y-1 sm:min-h-28"
          >
            <h3 className="text-sm font-semibold sm:text-base">{category.title}</h3>
          </a>
        ))}
      </div>
    </section>
  );
}
