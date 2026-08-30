import { CategoryGrid } from "@/components/storefront/category-grid";
import { Footer } from "@/components/storefront/footer";
import { Header } from "@/components/storefront/header";
import { Hero } from "@/components/storefront/hero";
import { MobileNav } from "@/components/storefront/mobile-nav";
import { ProductGrid } from "@/components/storefront/product-grid";
import { TrustStrip } from "@/components/storefront/trust-strip";
import { categories, products } from "@/lib/storefront-data";

export default function Home() {
  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <Hero />
        <CategoryGrid categories={categories} />
        <ProductGrid products={products} />
        <TrustStrip />
      </main>
      <Footer />
      <MobileNav />
    </div>
  );
}
