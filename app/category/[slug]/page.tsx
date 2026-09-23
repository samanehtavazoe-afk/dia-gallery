import Image from "next/image";
import { notFound } from "next/navigation";
import { ProductGrid } from "@/components/storefront/product-grid";
import { StorefrontShell } from "@/components/storefront/storefront-shell";
import { loadCategoryCatalog } from "@/lib/catalog/runtime";

export const dynamic = "force-dynamic";

export default async function CategoryPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const catalog = await loadCategoryCatalog(slug);

  if (!catalog) {
    notFound();
  }

  const { category, products } = catalog;

  return (
    <StorefrontShell>
      <section className="mx-auto grid max-w-7xl gap-6 px-4 py-10 sm:px-6 md:grid-cols-[1fr_16rem] lg:px-8">
        <div>
          <p className="text-sm text-[var(--accent)]">دسته‌بندی</p>
          <h1 className="mt-2 text-3xl font-semibold">{category.title}</h1>
        </div>
        <div className="relative aspect-[4/3] overflow-hidden rounded-[var(--radius-card)] bg-[var(--accent-soft)]">
          {category.imagePath ? (
            <Image
              src={category.imagePath}
              alt={category.imageAlt ?? category.title}
              fill
              sizes="256px"
              className="object-contain p-4"
            />
          ) : (
            <span className="grid h-full place-items-center text-sm text-[var(--muted)]">
              تصویر به‌زودی
            </span>
          )}
        </div>
      </section>
      {products.length > 0 ? (
        <ProductGrid products={products} title={`محصولات ${category.title}`} />
      ) : (
        <p className="mx-auto max-w-7xl px-4 py-16 text-center text-[var(--muted)]">
          در این دسته هنوز محصولی ثبت نشده است.
        </p>
      )}
    </StorefrontShell>
  );
}
