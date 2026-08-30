import type { StoreCategory } from "@/lib/storefront-data";

export function CategoryGrid({ categories }: { categories: StoreCategory[] }) {
  return (
    <section className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8" aria-labelledby="categories-title">
      <div className="mb-6 flex items-end justify-between gap-4">
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

      <div className="grid gap-3 sm:grid-cols-3">
        {categories.map((category) => (
          <a
            key={category.slug}
            href={`/category/${category.slug}`}
            className="group min-h-44 rounded-[var(--radius-card)] border border-[var(--line)] bg-white p-6 transition-transform hover:-translate-y-1"
          >
            <div className="flex h-full flex-col justify-end">
              <h3 className="text-xl font-semibold">{category.title}</h3>
              <p className="mt-2 text-sm text-[var(--muted)]">{category.subtitle}</p>
            </div>
          </a>
        ))}
      </div>
    </section>
  );
}
