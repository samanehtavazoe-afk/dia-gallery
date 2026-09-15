import type { StoreProduct } from "@/lib/storefront-data";

const priceFormatter = new Intl.NumberFormat("fa-IR");

function formatPrice(value: number) {
  return `${priceFormatter.format(value)} تومان`;
}

export function ProductCard({ product }: { product: StoreProduct }) {
  return (
    <article className="group overflow-hidden rounded-[var(--radius-card)] border border-[var(--line)] bg-[var(--surface)]">
      <div className="relative aspect-[4/5] bg-[var(--accent-soft)]">
        <button
          type="button"
          aria-label={`افزودن ${product.title} به علاقه‌مندی‌ها`}
          className="absolute left-3 top-3 grid size-9 place-items-center rounded-full bg-white/90 text-lg shadow-sm"
        >
          ♡
        </button>

        {!product.available ? (
          <span className="absolute bottom-3 right-3 rounded-full bg-white/90 px-3 py-1 text-xs font-medium text-[var(--foreground)]">
            ناموجود
          </span>
        ) : null}
      </div>

      <div className="space-y-3 p-4">
        <div>
          <p className="mb-1 text-xs text-[var(--muted)]">{product.brand}</p>
          <h3 className="text-sm font-medium leading-6">{product.title}</h3>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span className="font-semibold">{formatPrice(product.price)}</span>
          {product.compareAtPrice ? (
            <span className="text-sm text-[var(--muted)] line-through">
              {formatPrice(product.compareAtPrice)}
            </span>
          ) : null}
        </div>

        <a
          href={`/product/${product.slug}`}
          className="inline-flex min-h-10 items-center justify-center rounded-full border border-[var(--line)] px-4 text-sm transition hover:border-[var(--accent)]"
          aria-label={`مشاهده محصول ${product.title}`}
        >
          مشاهده محصول
        </a>
      </div>
    </article>
  );
}
