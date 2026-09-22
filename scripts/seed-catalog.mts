import {
  migrateCatalogDatabase,
  openCatalogDatabase,
} from "../lib/catalog/database.ts";
import { seedCatalogDatabase } from "../lib/catalog/seed.ts";

const database = openCatalogDatabase();

try {
  migrateCatalogDatabase(database);
  seedCatalogDatabase(database);
  console.log("دیتابیس کاتالوگ دیا گالری آماده است.");
} finally {
  database.close();
}
