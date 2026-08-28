// Centralised image asset helpers for blog and course cards
// ------------------------------------------------------------
// This file provides a single source of truth for image look‑ups.
// It is deliberately simple – a static map works for the current demo data
// set and can be replaced with a CMS/fetch layer later.

export const BLOG_IMAGES: Record<string, string> = {
  // slug → image URL (Unsplash placeholders for now)
  "default": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
  // Add explicit entries here to override the default per‑slug image.
};

export const COURSE_IMAGES: Record<string, string> = {
  "default": "https://images.unsplash.com/photo-1519389950476-f7831b9a6552",
};

/**
 * Return the appropriate image URL for a blog post slug.
 * Falls back to the generic placeholder if the slug is missing.
 */
export function getBlogImage(slug: string): string {
  return BLOG_IMAGES[slug] ?? BLOG_IMAGES["default"];
}

/**
 * Return the appropriate image URL for a course slug.
 */
export function getCourseImage(slug: string): string {
  return COURSE_IMAGES[slug] ?? COURSE_IMAGES["default"];
}
