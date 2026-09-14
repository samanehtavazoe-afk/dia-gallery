import Image from "next/image";

const slides = [
  { src: "/hero-homewear-duo.webp", alt: "استایل راحتی زنانه و مردانه دیا گالری" },
  { src: "/hero-homewear-women.webp", alt: "استایل راحتی زنانه دیا گالری" },
  { src: "/hero-homewear-men.webp", alt: "استایل راحتی مردانه دیا گالری" },
];

export function Hero() {
  return (
    <section className="mx-auto max-w-7xl px-4 pt-5 sm:px-6 lg:px-8" aria-label="بنر متحرک دیا گالری">
      <div className="grid min-h-[30rem] overflow-hidden rounded-[2rem] border border-[var(--line)] bg-[var(--dark)] text-white shadow-[0_24px_70px_rgba(23,22,21,0.12)] lg:min-h-[34rem] lg:grid-cols-[0.9fr_1.1fr]">
        <div className="relative z-10 flex flex-col justify-center gap-7 p-7 sm:p-10 lg:p-14">
          <div className="space-y-4">
            <p className="text-sm tracking-[0.22em] text-white/55">DIA GALLERY</p>
            <h1 className="max-w-xl text-3xl font-semibold leading-[1.5] sm:text-4xl lg:text-5xl">
              انتخاب خوب، خرید آسان
            </h1>
            <p className="max-w-xl text-sm leading-8 text-white/70 sm:text-base">
              پوشاک راحت و کاربردی برای خانه و روزمره؛ با یک تجربه خرید ساده و روشن.
            </p>
          </div>
          <a
            href="/shop"
            className="inline-flex min-h-11 w-fit items-center justify-center rounded-full bg-white px-6 text-sm font-medium text-[#171615] transition hover:bg-[#f1e8e1]"
          >
            مشاهده محصولات
          </a>
        </div>
        <div className="relative min-h-72 overflow-hidden border-t border-white/10 bg-[#eee6dc] lg:min-h-0 lg:border-r lg:border-t-0">
          {slides.map((slide, index) => (
            <div key={slide.src} className="hero-slide" style={{ animationDelay: `${index * 5}s` }}>
              <Image
                src={slide.src}
                alt={slide.alt}
                fill
                sizes="(max-width: 1024px) 100vw, 55vw"
                preload={index === 0}
                className="object-cover object-center"
              />
            </div>
          ))}
          <div className="absolute bottom-5 left-1/2 z-10 flex -translate-x-1/2 gap-2" aria-hidden="true">
            {slides.map((slide) => <span key={slide.src} className="size-1.5 rounded-full bg-black/35" />)}
          </div>
        </div>
      </div>
    </section>
  );
}
