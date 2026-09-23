import Image from "next/image";
import type { CatalogCategory } from "@/lib/catalog/repository";

export function CategoryGrid({ categories }: { categories: CatalogCategory[] }) {
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

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5 lg:gap-4">
        {categories.map((category) => (
          <a
            key={category.slug}
            href={`/category/${category.slug}`}
            aria-label={category.title}
            className="group overflow-hidden rounded-[var(--radius-card)] border border-[var(--line)] bg-[var(--surface)] p-2.5 text-center shadow-[0_12px_40px_rgba(33,31,29,0.04)] transition duration-300 hover:-translate-y-1 hover:shadow-[0_16px_46px_rgba(33,31,29,0.09)] sm:p-3"
          >
            <div className="relative aspect-[4/5] overflow-hidden rounded-[calc(var(--radius-card)-0.45rem)] bg-[var(--accent-soft)]">
              {category.imagePath ? (
                <Image
                  src={category.imagePath}
                  alt={category.imageAlt ?? category.title}
                  fill
                  sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 20vw"
                  className="object-contain p-2 transition duration-500 group-hover:scale-[1.035] sm:p-3"
                />
              ) : (
                <span className="grid h-full place-items-center text-sm text-[var(--muted)]">
                  تصویر به‌زودی
                </span>
              )}
            </div>
            <h3 className="px-1 pb-1 pt-3 text-sm font-semibold sm:text-base">{category.title}</h3>
          </a>
        ))}
      </div>
    </section>
  );
}

