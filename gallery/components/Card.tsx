"use client";

import Image from "next/image";
import Link from "next/link";
import { getBlogImage, getCourseImage } from "@/lib/images";

type CardProps = {
  href: string;
  title: string;
  excerpt?: string;
  category?: string;
  slug?: string; // for image lookup
  type?: "blog" | "course";
};

export function Card({ href, title, excerpt, category, slug = "default", type = "blog" }: CardProps) {
  const imgSrc = type === "blog" ? getBlogImage(slug) : getCourseImage(slug);

  return (
    <Link href={href} className="group block rounded-xl overflow-hidden bg-surface dark:bg-surface-dark shadow hover:shadow-lg transition-shadow">
      <div className="relative h-48 w-full">
        <Image src={imgSrc} alt={title} fill className="object-cover group-hover:scale-105 transition-transform" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent" />
      </div>
      <div className="p-4">
        {category && (
          <p className="text-xs text-muted dark:text-muted uppercase mb-1" aria-label={`Category: ${category}`}>
            {category}
          </p>
        )}
        <h3 className="font-semibold text-text dark:text-text-dark mb-2 group-hover:underline">{title}</h3>
        {excerpt && <p className="text-sm text-muted dark:text-muted line-clamp-2">{excerpt}</p>}
      </div>
    </Link>
  );
}
