import { Footer } from "@/components/storefront/footer";
import { Header } from "@/components/storefront/header";
import { MobileNav } from "@/components/storefront/mobile-nav";
import { ProductGrid } from "@/components/storefront/product-grid";
import { loadShopProducts } from "@/lib/catalog/runtime";

export const dynamic = "force-dynamic";

export default async function ShopPage() {
  const catalogProducts = await loadShopProducts();

  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <section className="mx-auto max-w-7xl px-4 pt-10 sm:px-6 lg:px-8">
          <p className="mb-2 text-sm text-[var(--muted)]">فروشگاه دیا گالری</p>
          <h1 className="text-3xl font-semibold">همه محصولات</h1>
        </section>
        <ProductGrid products={catalogProducts} title="محصولات" />
      </main>
      <Footer />
      <MobileNav />
    </div>
  );
}
