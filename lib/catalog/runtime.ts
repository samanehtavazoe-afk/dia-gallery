import { openCatalogDatabaseForRead } from "./database";
import {
  getActiveCategories,
  getActiveCategoryBySlug,
  getActiveProducts,
  getActiveProductsByCategory,
  getHomepageCollections,
  getProductDetailsBySlug,
} from "./repository";
function readCatalog<T>(
  reader: (db: ReturnType<typeof openCatalogDatabaseForRead>) => T,
) {
  const db = openCatalogDatabaseForRead();

  try {
    return reader(db);
  } finally {
    db.close();
  }
}

export async function loadShopProducts() {
  return readCatalog(getActiveProducts);
}

export async function loadCategoryCatalog(slug: string) {
  return readCatalog((db) => {
    const category = getActiveCategoryBySlug(db, slug);

    return category
      ? { category, products: getActiveProductsByCategory(db, slug) }
      : null;
  });
}

export async function loadProductCatalog(slug: string) {
  return readCatalog((db) => getProductDetailsBySlug(db, slug));
}

export async function loadHomepageCatalog(dayIndex?: number) {
  return readCatalog((db) => ({
    categories: getActiveCategories(db),
    collections: getHomepageCollections(db, dayIndex),
  }));
}
