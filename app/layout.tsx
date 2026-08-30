import type { Metadata } from "next";
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
      <body>{children}</body>
    </html>
  );
}
