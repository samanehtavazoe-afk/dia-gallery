import type { ReactNode } from "react";
import { Footer } from "./footer";
import { Header } from "./header";
import { MobileNav } from "./mobile-nav";

export function StorefrontShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <Header />
      <main>{children}</main>
      <Footer />
      <MobileNav />
    </div>
  );
}
