import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "دیا گالری | فروشگاه پوشاک و ملزومات روزمره",
  description:
    "دیا گالری، فروشگاه چندبرندی محصولات زنانه، مردانه و قالب نگهدارنده کفش. مجموعه‌ای از انتخاب‌های کاربردی برای خرید روزمره.",
  robots: { index: false, follow: false },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fa" dir="rtl">
      <body>{children}</body>
    </html>
  );
}
