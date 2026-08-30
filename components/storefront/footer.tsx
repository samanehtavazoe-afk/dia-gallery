const shopLinks = [
  { href: "/shop", label: "فروشگاه" },
  { href: "/category/women", label: "زنانه" },
  { href: "/category/men", label: "مردانه" },
];

const supportLinks = [
  { href: "/contact", label: "تماس با ما" },
  { href: "/shipping", label: "ارسال و پیگیری" },
  { href: "/faq", label: "سوالات متداول" },
];

export function Footer() {
  return (
    <footer className="mt-6 border-t border-[var(--line)] bg-[var(--dark)] pb-24 text-white md:pb-0">
      <div className="mx-auto grid max-w-7xl gap-10 px-4 py-12 sm:px-6 md:grid-cols-[1.4fr_1fr_1fr] lg:px-8">
        <div>
          <p className="text-lg font-semibold tracking-[0.16em]">DIAA GALLERY</p>
          <p className="mt-4 max-w-md text-sm leading-7 text-white/65">
            انتخاب‌های کاربردی زنانه و مردانه، در یک فروشگاه ساده و مطمئن.
          </p>
        </div>
        <nav aria-label="لینک‌های فروشگاه">
          <h2 className="mb-4 font-semibold">فروشگاه</h2>
          <div className="grid gap-3 text-sm text-white/65">
            {shopLinks.map((link) => <a key={link.href} href={link.href}>{link.label}</a>)}
          </div>
        </nav>
        <nav aria-label="راهنما و پشتیبانی">
          <h2 className="mb-4 font-semibold">راهنما</h2>
          <div className="grid gap-3 text-sm text-white/65">
            {supportLinks.map((link) => <a key={link.href} href={link.href}>{link.label}</a>)}
          </div>
        </nav>
      </div>
      <div className="border-t border-white/10">
        <div className="mx-auto flex max-w-7xl flex-wrap justify-between gap-3 px-4 py-5 text-xs text-white/50 sm:px-6 lg:px-8">
          <span>© دیا گالری</span>
          <a href="/privacy">حریم خصوصی</a>
        </div>
      </div>
    </footer>
  );
}
