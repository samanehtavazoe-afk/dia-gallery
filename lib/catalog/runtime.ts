import { migrateCatalogDatabase, openCatalogDatabase } from "./database";
import { getActiveProducts } from "./repository";
import { seedCatalogDatabase } from "./seed";

export async function loadShopProducts() {
  const db = openCatalogDatabase();

  try {
    migrateCatalogDatabase(db);
    seedCatalogDatabase(db);
    return getActiveProducts(db);
  } finally {
    db.close();
  }
}
