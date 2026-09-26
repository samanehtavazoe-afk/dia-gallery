import { CategoryGrid } from "@/components/storefront/category-grid";
import { Hero } from "@/components/storefront/hero";
import { ProductGrid } from "@/components/storefront/product-grid";
import { StorefrontShell } from "@/components/storefront/storefront-shell";
import { TrustStrip } from "@/components/storefront/trust-strip";
import { loadHomepageCatalog } from "@/lib/catalog/runtime";

export const dynamic = "force-dynamic";

export default async function Home() {
  const { categories, collections } = await loadHomepageCatalog();
  const { today, latest, discounted } = collections;

  return (
    <StorefrontShell>
      <Hero />
      <CategoryGrid categories={categories} />
      {today.length > 0 ? (
        <ProductGrid products={today} title="منتخب امروز" />
      ) : null}
      {latest.length > 0 ? (
        <ProductGrid products={latest} title="جدیدترین‌ها" />
      ) : null}
      {discounted.length > 0 ? (
        <ProductGrid products={discounted} title="تخفیف‌دارها" />
      ) : null}
      <TrustStrip />
    </StorefrontShell>
  );
}
