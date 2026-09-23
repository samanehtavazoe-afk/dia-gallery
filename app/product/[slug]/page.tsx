import { notFound } from "next/navigation";
import { ProductDetailView } from "@/components/storefront/product-detail-view";
import { StorefrontShell } from "@/components/storefront/storefront-shell";
import { loadProductCatalog } from "@/lib/catalog/runtime";

export const dynamic = "force-dynamic";

export default async function ProductPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const product = await loadProductCatalog(slug);

  if (!product) {
    notFound();
  }

  return (
    <StorefrontShell>
      <ProductDetailView product={product} />
    </StorefrontShell>
  );
}
