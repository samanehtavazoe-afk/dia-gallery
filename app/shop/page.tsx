import { ProductGrid } from "@/components/storefront/product-grid";
import { StorefrontShell } from "@/components/storefront/storefront-shell";
import { loadShopProducts } from "@/lib/catalog/runtime";

export const dynamic = "force-dynamic";

export default async function ShopPage() {
  const catalogProducts = await loadShopProducts();

  return (
    <StorefrontShell>
      <section className="mx-auto max-w-7xl px-4 pt-10 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-semibold">فروشگاه</h1>
        <p className="mt-3 text-sm text-[var(--muted)]">
          همه محصولات فعال دیا گالری
        </p>
      </section>
      {catalogProducts.length > 0 ? (
        <ProductGrid products={catalogProducts} title="همه محصولات" />
      ) : (
        <p className="mx-auto max-w-7xl px-4 py-16 text-center text-[var(--muted)]">
          هنوز محصولی ثبت نشده است.
        </p>
      )}
    </StorefrontShell>
  );
}
