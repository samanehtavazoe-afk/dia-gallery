const assurances = [
  { title: "ارسال مطمئن", description: "بسته‌بندی دقیق و پیگیری سفارش" },
  { title: "تضمین اصالت", description: "انتخاب از محصولات معتبر" },
  { title: "پشتیبانی خرید", description: "همراه شما پیش و پس از سفارش" },
];

export function TrustStrip() {
  return (
    <section className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8" aria-label="مزایای خرید از دیا گالری">
      <div className="grid overflow-hidden rounded-[var(--radius-card)] border border-[var(--line)] bg-white sm:grid-cols-3">
        {assurances.map((item, index) => (
          <div
            key={item.title}
            className={`p-5 text-center sm:p-6 ${index ? "border-t border-[var(--line)] sm:border-r sm:border-t-0" : ""}`}
          >
            <h2 className="text-base font-semibold">{item.title}</h2>
            <p className="mt-2 text-sm leading-6 text-[var(--muted)]">{item.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
