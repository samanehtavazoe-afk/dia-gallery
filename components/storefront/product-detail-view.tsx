"use client";

import Image from "next/image";
import { useState } from "react";
import { selectImagesForColor } from "@/lib/catalog/color-images";
import type { CatalogProductDetails } from "@/lib/catalog/repository";

const priceFormatter = new Intl.NumberFormat("fa-IR");

function formatPrice(value: number) {
  return `${priceFormatter.format(value)} تومان`;
}

export function ProductDetailView({
  product,
}: {
  product: CatalogProductDetails;
}) {
  const initialColorId =
    product.colors.find((color) =>
      product.variants.some(
        (variant) => variant.colorId === color.id && variant.available,
      ),
    )?.id ??
    product.colors[0]?.id ??
    null;
  const [colorId, setColorId] = useState<number | null>(initialColorId);
  const [size, setSize] = useState<string | null>(null);
  const variants = product.variants.filter(
    (variant) => variant.colorId === colorId,
  );
  const images =
    colorId === null
      ? product.images.filter((image) => image.colorId === undefined)
      : selectImagesForColor(product.images, colorId);
  const selectedVariant =
    variants.find((variant) => variant.size === size) ?? null;
  const stockLabel = selectedVariant
    ? selectedVariant.available
      ? `${priceFormatter.format(selectedVariant.stock)} عدد موجود`
      : "ناموجود"
    : variants.some((variant) => variant.available)
      ? "سایز را انتخاب کنید"
      : "ناموجود";

  return (
    <section className="mx-auto grid max-w-7xl gap-8 px-4 py-10 sm:px-6 lg:grid-cols-[1.15fr_0.85fr] lg:px-8">
      <div className="grid gap-4 sm:grid-cols-2">
        {images.length > 0 ? (
          images.map((image) => (
            <div
              key={image.id}
              className="relative aspect-[4/5] overflow-hidden rounded-[var(--radius-card)] bg-[var(--accent-soft)]"
            >
              <Image
                src={image.path}
                alt={image.alt}
                fill
                sizes="(max-width: 1024px) 100vw, 50vw"
                className="object-contain p-4"
              />
            </div>
          ))
        ) : (
          <div className="grid aspect-[4/5] place-items-center rounded-[var(--radius-card)] bg-[var(--accent-soft)] text-sm text-[var(--muted)]">
            تصویر به‌زودی
          </div>
        )}
      </div>

      <div className="space-y-6 lg:sticky lg:top-24 lg:self-start">
        <div>
          <p className="text-sm text-[var(--muted)]">{product.brand}</p>
          <h1 className="mt-2 text-3xl font-semibold">{product.name}</h1>
        </div>
        <p className="leading-8 text-[var(--muted)]">{product.description}</p>
        <div className="flex flex-wrap items-center gap-3">
          <span className="text-xl font-semibold">
            {formatPrice(product.price)}
          </span>
          {product.compareAtPrice !== undefined &&
          product.compareAtPrice > product.price ? (
            <span className="text-sm text-[var(--muted)] line-through">
              {formatPrice(product.compareAtPrice)}
            </span>
          ) : null}
        </div>

        {product.colors.length > 0 ? (
          <fieldset>
            <legend className="mb-3 font-medium">رنگ</legend>
            <div className="flex flex-wrap gap-2">
              {product.colors.map((color) => (
                <button
                  key={color.id}
                  type="button"
                  aria-label={`رنگ ${color.name}`}
                  aria-pressed={color.id === colorId}
                  onClick={() => {
                    setColorId(color.id);
                    setSize(null);
                  }}
                  className="inline-flex items-center gap-2 rounded-full border border-[var(--line)] px-4 py-2 text-sm aria-pressed:border-[var(--dark)]"
                >
                  {color.hexCode ? (
                    <span
                      aria-hidden="true"
                      className="size-4 rounded-full border border-black/10"
                      style={{ backgroundColor: color.hexCode }}
                    />
                  ) : null}
                  {color.name}
                </button>
              ))}
            </div>
          </fieldset>
        ) : null}

        {variants.length > 0 ? (
          <fieldset>
            <legend className="mb-3 font-medium">سایز</legend>
            <div className="flex flex-wrap gap-2">
              {variants.map((variant) => (
                <button
                  key={variant.sku}
                  type="button"
                  aria-label={`سایز ${variant.size}`}
                  aria-pressed={variant.size === size}
                  disabled={!variant.available}
                  onClick={() => setSize(variant.size)}
                  className="min-w-12 rounded-full border border-[var(--line)] px-4 py-2 aria-pressed:border-[var(--dark)] disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {variant.size}
                </button>
              ))}
            </div>
          </fieldset>
        ) : null}

        <p aria-live="polite" className="text-sm text-[var(--muted)]">
          {stockLabel}
        </p>
        <button
          type="button"
          disabled
          aria-label="افزودن به سبد خرید"
          className="w-full cursor-not-allowed rounded-full bg-[var(--dark)] px-5 py-3 text-white opacity-50"
        >
          افزودن به سبد خرید
        </button>
        <p className="text-xs text-[var(--muted)]">
          سبد خرید در مرحله بعد فعال می‌شود.
        </p>
      </div>
    </section>
  );
}
