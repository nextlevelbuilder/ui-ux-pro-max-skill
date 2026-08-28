"use client";

import Image from "next/image";

type HeroProps = {
  title: string;
  subtitle?: string;
  ctaHref?: string;
  ctaLabel?: string;
  imageSrc?: string; // optional background image
};

export function Hero({ title, subtitle, ctaHref, ctaLabel, imageSrc }: HeroProps) {
  return (
    <section className="relative bg-gradient-to-r from-primary to-accent text-white py-20" aria-label="hero">
      {imageSrc && (
        <Image src={imageSrc} alt="" fill className="object-cover opacity-30" priority />
      )}
      <div className="relative max-w-4xl mx-auto text-center px-4">
        <h1 className="text-4xl md:text-5xl font-bold mb-4">{title}</h1>
        {subtitle && <p className="text-xl mb-6">{subtitle}</p>}
        {ctaHref && ctaLabel && (
          <a href={ctaHref} className="inline-block bg-white text-primary font-medium px-6 py-3 rounded-xl hover:bg-gray-100 transition-colors">
            {ctaLabel}
          </a>
        )}
      </div>
    </section>
  );
}
