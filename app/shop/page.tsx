import { Footer } from "@/components/storefront/footer";
import { Header } from "@/components/storefront/header";
import { MobileNav } from "@/components/storefront/mobile-nav";
import { ProductGrid } from "@/components/storefront/product-grid";
import { loadShopProducts } from "@/lib/catalog/runtime";
import type { StoreProduct } from "@/lib/storefront-data";

export const dynamic = "force-dynamic";

export default async function ShopPage() {
  const catalogProducts = await loadShopProducts();

  const products: StoreProduct[] = catalogProducts.map((product) => ({
    slug: product.slug,
    title: product.name,
    brand: product.brand,
    price: product.price,
    compareAtPrice: product.compareAtPrice,
    category: product.categorySlug,
    available: product.available,
  }));

  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <section className="mx-auto max-w-7xl px-4 pt-10 sm:px-6 lg:px-8">
          <p className="mb-2 text-sm text-[var(--muted)]">فروشگاه دیا گالری</p>
          <h1 className="text-3xl font-semibold">همه محصولات</h1>
        </section>
        <ProductGrid products={products} title="همه محصولات" />
      </main>
      <Footer />
      <MobileNav />
    </div>
  );
}
