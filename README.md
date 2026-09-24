# فروشگاه دیا گالری

فروشگاه با Next.js و دیتابیس SQLite ساخته شده است. اطلاعات دسته‌ها، محصولات، رنگ‌ها، سایزها، تصاویر و موجودی از دیتابیس خوانده می‌شود.

## راه‌اندازی توسعه

```bash
npm ci
npm run db:seed
npm run dev
```

دیتابیس توسعه به‌صورت پیش‌فرض در `.data/dia-gallery.sqlite` ساخته می‌شود و داخل Git قرار نمی‌گیرد.

## راه‌اندازی دیتابیس کاتالوگ روی سرور

Node.js نسخه ۲۲ یا جدیدتر لازم است.

```bash
export DIA_SERVICE_USER=www-data
export DIA_DB_PATH=/var/lib/dia-gallery/data/dia-gallery.sqlite
sudo install -d -o "$DIA_SERVICE_USER" -g "$DIA_SERVICE_USER" -m 750 /var/lib/dia-gallery/data
npm ci --ignore-scripts
npm rebuild better-sqlite3
sudo -u "$DIA_SERVICE_USER" env DIA_DB_PATH="$DIA_DB_PATH" npm run db:seed
npm run build
```

مقدار `DIA_SERVICE_USER` باید نام همان کاربری باشد که سرویس سایت را اجرا می‌کند؛ اگر سایت با کاربر دیگری اجرا می‌شود، `www-data` را با نام آن جایگزین کنید. سرویس اصلی نیز باید متغیر `DIA_DB_PATH` را با همین مسیر دریافت کند. دادهٔ نمونه فقط با دستور `db:seed` و در اجرای نخست ثبت می‌شود و اجرای دوبارهٔ دستور، تغییرات بعدی محصولات را بازنویسی نمی‌کند.

برای اجرای نسخهٔ ساخته‌شده:

```bash
export DIA_DB_PATH=/var/lib/dia-gallery/data/dia-gallery.sqlite
npm start -- -H 0.0.0.0 -p 3100
```
