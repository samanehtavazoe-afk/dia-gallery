import Image from "next/image";
import type { CatalogProduct } from "@/lib/catalog/repository";

const priceFormatter = new Intl.NumberFormat("fa-IR");

function formatPrice(value: number) {
  return `${priceFormatter.format(value)} تومان`;
}

export function ProductCard({ product }: { product: CatalogProduct }) {
  return (
    <article className="group overflow-hidden rounded-[var(--radius-card)] border border-[var(--line)] bg-[var(--surface)]">
      <div className="relative aspect-[4/5] bg-[var(--accent-soft)]">
        {product.image ? (
          <Image
            src={product.image.path}
            alt={product.image.alt}
            fill
            sizes="(max-width: 768px) 50vw, 25vw"
            className="object-contain p-3 transition duration-500 group-hover:scale-[1.025]"
          />
        ) : (
          <span className="grid h-full place-items-center text-sm text-[var(--muted)]">
            تصویر به‌زودی
          </span>
        )}

        <button
          type="button"
          aria-label={`افزودن ${product.name} به علاقه‌مندی‌ها`}
          className="absolute left-3 top-3 z-10 grid size-9 place-items-center rounded-full bg-white/90 text-lg shadow-sm"
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
          <h3 className="text-sm font-medium leading-6">{product.name}</h3>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span className="font-semibold">{formatPrice(product.price)}</span>
          {product.compareAtPrice !== undefined &&
          product.compareAtPrice > product.price ? (
            <span className="text-sm text-[var(--muted)] line-through">
              {formatPrice(product.compareAtPrice)}
            </span>
          ) : null}
        </div>

        <a
          href={`/product/${product.slug}`}
          className="inline-flex min-h-10 items-center justify-center rounded-full border border-[var(--line)] px-4 text-sm transition hover:border-[var(--accent)]"
          aria-label={`مشاهده محصول ${product.name}`}
        >
          مشاهده محصول
        </a>
      </div>
    </article>
  );
}
