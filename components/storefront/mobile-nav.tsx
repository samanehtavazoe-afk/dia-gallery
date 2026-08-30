const items = [
  { href: "/", label: "خانه", symbol: "⌂" },
  { href: "/shop", label: "فروشگاه", symbol: "▦" },
  { href: "/wishlist", label: "علاقه‌مندی‌ها", symbol: "♡" },
  { href: "/cart", label: "سبد خرید", symbol: "◌" },
];

export function MobileNav() {
  return (
    <nav
      aria-label="دسترسی سریع موبایل"
      className="fixed inset-x-0 bottom-0 z-50 border-t border-[var(--line)] bg-white/95 px-3 py-2 backdrop-blur md:hidden"
    >
      <div className="mx-auto grid max-w-md grid-cols-4">
        {items.map((item) => (
          <a
            key={item.href}
            href={item.href}
            className="flex min-h-12 flex-col items-center justify-center gap-1 text-[0.7rem] text-[var(--muted)]"
          >
            <span aria-hidden="true" className="text-lg leading-none">{item.symbol}</span>
            <span>{item.label}</span>
          </a>
        ))}
      </div>
    </nav>
  );
}
