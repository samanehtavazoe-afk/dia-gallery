import { CategoryGrid } from "@/components/storefront/category-grid";
import { Footer } from "@/components/storefront/footer";
import { Header } from "@/components/storefront/header";
import { Hero } from "@/components/storefront/hero";
import { MobileNav } from "@/components/storefront/mobile-nav";
import { ProductGrid } from "@/components/storefront/product-grid";
import { TrustStrip } from "@/components/storefront/trust-strip";
import { buildHomepageCollections, categories, products } from "@/lib/storefront-data";

export default function Home() {
  const { today, latest, discounted } = buildHomepageCollections(products);
  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <Hero />
        <CategoryGrid categories={categories} />
        <ProductGrid products={today} title="منتخب امروز" />
        <ProductGrid products={latest} title="جدیدترین‌ها" />
        {discounted.length > 0 && <ProductGrid products={discounted} title="تخفیف‌دارها" />}
        <TrustStrip />
      </main>
      <Footer />
      <MobileNav />
    </div>
  );
}
