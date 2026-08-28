import { Card } from "@/components/Card";

const courses = [
  {
    slug: "nextjs-foundations",
    title: "Next.js Foundations",
    excerpt: "Master the basics of Next.js including routing, data fetching, and deployment.",
    category: "Web Dev",
  },
  {
    slug: "tailwind-design",
    title: "Design Systems with Tailwind",
    excerpt: "Build scalable, theme‑aware UI kits using Tailwind CSS tokens.",
    category: "Design",
  },
];

export default function CoursesPage() {
  return (
    <section className="max-w-7xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Courses</h1>
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {courses.map((c) => (
          <Card
            key={c.slug}
            href={`/courses/${c.slug}`}
            title={c.title}
            excerpt={c.excerpt}
            category={c.category}
            slug={c.slug}
            type="course"
          />
        ))}
      </div>
    </section>
  );
}
