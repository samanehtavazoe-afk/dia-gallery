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
sudo install -d -m 700 /var/lib/dia-gallery/data
export DIA_DB_PATH=/var/lib/dia-gallery/data/dia-gallery.sqlite
npm ci --ignore-scripts
npm rebuild better-sqlite3
npm run db:seed
npm run build
```

سرویس اصلی نیز باید متغیر `DIA_DB_PATH` را با همین مسیر دریافت کند و کاربر اجرای سرویس اجازهٔ خواندن و نوشتن در پوشهٔ دیتابیس را داشته باشد. دادهٔ نمونه فقط در اجرای نخست ثبت می‌شود و اجرای دوبارهٔ دستور، تغییرات بعدی محصولات را بازنویسی نمی‌کند.

برای اجرای نسخهٔ ساخته‌شده:

```bash
export DIA_DB_PATH=/var/lib/dia-gallery/data/dia-gallery.sqlite
npm start -- -H 0.0.0.0 -p 3100
```
