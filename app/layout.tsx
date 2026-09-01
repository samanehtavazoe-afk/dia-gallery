import type { Metadata } from "next";
import "vazirmatn/Vazirmatn-font-face.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "دیا گالری | فروشگاه آنلاین",
  description: "فروشگاه آنلاین دیا گالری؛ انتخابی ساده برای خرید محصولات متنوع.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fa" dir="rtl">
      <body className="font-vazirmatn">{children}</body>
    </html>
  );
}
