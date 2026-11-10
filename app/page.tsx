const collections = [
  {
    number: "01",
    label: "WOMEN",
    title: "زنانه",
    description: "انتخاب‌های ساده و کاربردی برای راحتی هر روز",
    style: "women",
  },
  {
    number: "02",
    label: "MEN",
    title: "مردانه",
    description: "مدل‌های متنوع برای استفاده روزمره",
    style: "men",
  },
  {
    number: "03",
    label: "SHOE CARE",
    title: "قالب و هولدر کفش",
    description: "برای نگهداری بهتر از فرم و ظاهر کفش",
    style: "shoe",
  },
];

export default function Home() {
  return (
    <div className="site-shell">
      <div className="announcement">
        <span>فروشگاه چندبرندی دیا گالری</span>
        <span className="announcement-separator" aria-hidden="true">✦</span>
        <span>انتخاب‌های کاربردی برای هر روز</span>
      </div>

      <header className="site-header">
        <div className="header-inner content-width">
          <a className="wordmark" href="#top" aria-label="دیا گالری، صفحه اصلی">
            <span>DIA</span>
            <small>GALLERY</small>
          </a>
          <nav className="primary-nav" aria-label="ناوبری اصلی">
            <a href="#collections">دسته‌بندی‌ها</a>
            <a href="#philosophy">درباره دیا</a>
            <a href="#contact">ارتباط با ما</a>
          </nav>
          <a className="header-link" href="#collections">
            مشاهده محصولات <span aria-hidden="true">↙</span>
          </a>
        </div>
      </header>

      <main id="top">
        <section className="hero content-width" aria-labelledby="hero-title">
          <div className="hero-copy">
            <div className="eyebrow"><span className="line" /> YOUR EVERYDAY EDIT</div>
            <h1 id="hero-title">
              برای هر روز،
              <br />
              <em>یک انتخاب بهتر.</em>
            </h1>
            <p>
              از لباس زیر زنانه و مردانه تا قالب نگهدارنده کفش؛
              مجموعه‌ای از انتخاب‌های راحت و کاربردی، در یک جا.
            </p>
            <div className="hero-actions">
              <a className="button button-dark" href="#collections">کشف دسته‌بندی‌ها <span aria-hidden="true">←</span></a>
              <a className="text-link" href="#philosophy">آشنایی با دیا گالری</a>
            </div>
            <div className="hero-footnote">
              <span className="footnote-line" aria-hidden="true" />
              <span>فروشگاهی برای سلیقه‌های متفاوت</span>
            </div>
          </div>
          <div className="hero-art" aria-label="تصویر مفهومی برای ظاهر اولیه فروشگاه">
            <div className="hero-art-inner">
              <div className="art-orbit art-orbit-one" />
              <div className="art-orbit art-orbit-two" />
              <div className="art-object art-object-back" />
              <div className="art-object art-object-front" />
              <span className="art-stamp">D / G</span>
              <span className="art-vertical">ESSENTIALS · CURATED FOR YOU</span>
              <div className="art-caption">
                <span>THE DIA EDIT</span>
                <span>01 / 03</span>
              </div>
            </div>
            <div className="hero-art-note">تصاویر اصلی محصولات در مرحله تکمیل فروشگاه جایگزین می‌شوند.</div>
          </div>
        </section>

        <section className="collections-section" id="collections" aria-labelledby="collections-title">
          <div className="content-width">
            <div className="section-heading">
              <div>
                <div className="eyebrow muted">EXPLORE THE COLLECTIONS</div>
                <h2 id="collections-title">دسته‌بندی‌ها را کشف کن</h2>
              </div>
              <p>از نیازهای روزمره شروع کن؛ به‌سادگی چیزی را پیدا کن که دنبالش هستی.</p>
            </div>
            <div className="collections-grid">
              {collections.map((item) => (
                <article className={`collection-card ${item.style}`} key={item.number}>
                  <div className="collection-art" aria-hidden="true">
                    <div className="collection-blob blob-a" />
                    <div className="collection-blob blob-b" />
                    <span className="collection-label">{item.label}</span>
                    <span className="collection-number">{item.number}</span>
                  </div>
                  <div className="collection-meta">
                    <div>
                      <h3>{item.title}</h3>
                      <p>{item.description}</p>
                    </div>
                    <span className="collection-arrow" aria-hidden="true">↙</span>
                  </div>
                </article>
              ))}
            </div>
            <p className="prototype-note">این صفحه نسخه اولیه طراحی است؛ لینک محصولات، قیمت‌ها و سبد خرید پس از اتصال به فروشگاه فعال می‌شوند.</p>
          </div>
        </section>

        <section className="manifesto content-width" id="philosophy" aria-labelledby="manifesto-title">
          <div className="manifesto-mark" aria-hidden="true">DIA <span>GALLERY</span></div>
          <div className="manifesto-content">
            <div className="eyebrow">A LITTLE MORE ABOUT US</div>
            <h2 id="manifesto-title">خرید خوب، از <em>انتخاب ساده</em> شروع می‌شود.</h2>
            <p>
              دیا گالری یک فروشگاه چندبرندی است. دسته‌بندی‌ها بر اساس نوع محصول چیده می‌شوند
              تا میان مدل‌های زنانه، مردانه و سایر نیازهای روزمره، راحت‌تر انتخاب کنی.
            </p>
            <a className="text-link" href="#contact">در ارتباط باشیم <span aria-hidden="true">←</span></a>
          </div>
        </section>

        <section className="principles">
          <div className="content-width principles-inner">
            <div><span>01</span><strong>دسته‌بندی روشن</strong><p>پیدا کردن محصول بر اساس نوع آن</p></div>
            <div><span>02</span><strong>چندبرندی</strong><p>انتخاب میان برندها و مدل‌های مختلف</p></div>
            <div><span>03</span><strong>طراحی ساده</strong><p>تجربه‌ای مرتب و مناسب موبایل</p></div>
          </div>
        </section>

        <section className="contact-section content-width" id="contact" aria-labelledby="contact-title">
          <div>
            <span className="eyebrow">STAY CONNECTED</span>
            <h2 id="contact-title">با دیا گالری همراه باش.</h2>
            <p>برای دیدن مدل‌ها و خبرهای فروشگاه، صفحه اینستاگرام دیا گالری را دنبال کن.</p>
          </div>
          <a className="button button-outline" href="https://www.instagram.com/diagallery._/" target="_blank" rel="noopener noreferrer">
            اینستاگرام دیا گالری <span aria-hidden="true">↗</span>
          </a>
        </section>
      </main>

      <footer className="site-footer">
        <div className="content-width footer-inner">
          <div className="footer-brand"><strong>DIA</strong><span>GALLERY</span></div>
          <p>دیا گالری · انتخاب‌های روزمره برای همه</p>
          <a href="#top">بازگشت به بالا ↑</a>
        </div>
      </footer>
    </div>
  );
}
