"use client";

import { useEffect } from "react";

export default function ErrorPage({
  error,
  retry,
}: {
  error: unknown;
  retry: () => void;
}) {
  useEffect(() => {
    console.error("[storefront] render failed", error);
  }, [error]);

  return (
    <main className="grid min-h-screen place-items-center px-4 text-center">
      <div>
        <h1 className="text-2xl font-semibold">مشکلی پیش آمد</h1>
        <p className="mt-3 text-[var(--muted)]">
          نمایش فروشگاه موقتاً ممکن نیست. لطفاً دوباره تلاش کنید.
        </p>
        <button
          type="button"
          onClick={retry}
          className="mt-6 rounded-full bg-[var(--dark)] px-5 py-3 text-white"
        >
          تلاش دوباره
        </button>
      </div>
    </main>
  );
}
