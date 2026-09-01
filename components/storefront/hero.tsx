export function Hero() {
  return (
    <section className="mx-auto max-w-7xl px-4 pt-6 sm:px-6 lg:px-8">
      <div className="overflow-hidden rounded-[2rem] border border-[var(--line)] bg-[var(--dark)] text-white">
        <div className="flex flex-col justify-center gap-6 p-7 sm:p-10 lg:p-14">

          <div className="space-y-4">
            <p className="text-sm tracking-[0.18em] text-white/60">DIAA GALLERY</p>
            <h1 className="max-w-xl text-3xl font-semibold leading-[1.5] sm:text-4xl lg:text-5xl">
              انتخاب خوب، خرید آسان
            </h1>
            <p className="max-w-xl text-sm leading-8 text-white/70 sm:text-base">
              مجموعه‌ای ساده و متنوع برای خرید روزمره؛ بدون شلوغی و با انتخاب‌های روشن‌تر.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <a
              href="/shop"
              className="inline-flex min-h-11 items-center justify-center rounded-full bg-white px-5 text-sm font-medium text-[var(--dark)]"
            >
              مشاهده محصولات
            </a>
          </div>
        </div>

      </div>
    </section>
  );
}
