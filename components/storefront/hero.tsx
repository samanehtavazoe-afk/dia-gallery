export function Hero() {
  return (
    <section className="mx-auto max-w-7xl px-4 pt-6 sm:px-6 lg:px-8">
      <div className="grid overflow-hidden rounded-[2rem] border border-[var(--line)] bg-[var(--dark)] text-white lg:grid-cols-[1.05fr_0.95fr]">
        <div className="flex flex-col justify-center gap-6 p-7 sm:p-10 lg:p-14">
          <div className="flex flex-wrap gap-2 text-sm">
            <span className="rounded-full border border-white/20 px-3 py-1.5">زنانه</span>
            <span className="rounded-full border border-white/20 px-3 py-1.5">مردانه</span>
          </div>

          <div className="space-y-4">
            <p className="text-sm tracking-[0.18em] text-white/60">DIAA GALLERY</p>
            <h1 className="max-w-xl text-3xl font-semibold leading-[1.5] sm:text-4xl lg:text-5xl">
              انتخاب برای خانم‌ها و آقایان
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
            <a
              href="#categories"
              className="inline-flex min-h-11 items-center justify-center rounded-full border border-white/25 px-5 text-sm text-white"
            >
              دسته‌بندی‌ها
            </a>
          </div>
        </div>

        <div className="grid min-h-72 grid-cols-2 border-t border-white/10 lg:min-h-[32rem] lg:border-t-0 lg:border-r">
          <a
            href="/category/women"
            className="group relative flex items-end overflow-hidden bg-[linear-gradient(160deg,#eaded4_0%,#c9a991_100%)] p-5 text-[var(--dark)]"
          >
            <span className="absolute inset-5 rounded-[1.75rem] border border-black/10" aria-hidden="true" />
            <span className="relative rounded-full bg-white/75 px-4 py-2 text-sm font-medium backdrop-blur">زنانه</span>
          </a>

          <a
            href="/category/men"
            className="group relative flex items-end overflow-hidden bg-[linear-gradient(160deg,#cbc6c0_0%,#756f69_100%)] p-5"
          >
            <span className="absolute inset-5 rounded-[1.75rem] border border-white/20" aria-hidden="true" />
            <span className="relative rounded-full bg-black/40 px-4 py-2 text-sm font-medium text-white backdrop-blur">مردانه</span>
          </a>
        </div>
      </div>
    </section>
  );
}
