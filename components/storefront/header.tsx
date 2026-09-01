import Image from "next/image";
import Link from "next/link";

const actions = [
  { href: "/wishlist", label: "علاقه‌مندی‌ها", symbol: "♡" },
  { href: "/account", label: "حساب کاربری", symbol: "○" },
  { href: "/cart", label: "سبد خرید", symbol: "◌" },
];

export function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-[var(--line)] bg-[color:var(--background)]/95 backdrop-blur">
      <div className="mx-auto flex min-h-16 max-w-7xl items-center gap-4 px-4 sm:px-6 lg:px-8">
        <Link href="/" className="shrink-0" aria-label="دیا گالری - صفحه اصلی">
          <Image src="/diaa-gallery.png.PNG" alt="لوگوی دیا گالری" width={1024} height={1024} priority className="h-auto w-20 sm:w-24" />
        </Link>

        <nav className="hidden items-center gap-6 text-sm lg:flex" aria-label="منوی اصلی">
          <a href="/shop">فروشگاه</a>
          <a href="/category/women">زنانه</a>
          <a href="/category/men">مردانه</a>
          <a href="/category/shoe-care">قالب و هولدر کفش</a>
        </nav>

        <form className="me-auto hidden max-w-sm flex-1 md:block" role="search">
          <label htmlFor="site-search" className="sr-only">
            جستجوی محصولات
          </label>
          <input
            id="site-search"
            type="search"
            placeholder="جستجوی محصول..."
            className="w-full rounded-full border border-[var(--line)] bg-white px-4 py-2 text-sm outline-none"
          />
        </form>

        <div className="flex items-center gap-3">
          {actions.map((action) => (
            <a
              key={action.href}
              href={action.href}
              aria-label={action.label}
              className="grid size-9 place-items-center rounded-full border border-[var(--line)] bg-white"
            >
              <span aria-hidden="true">{action.symbol}</span>
            </a>
          ))}
        </div>
      </div>
    </header>
  );
}
