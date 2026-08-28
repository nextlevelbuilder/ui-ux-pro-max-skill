import { Card } from "@/components/Card";
import { blogPosts } from "../data/blogPosts";

export default function BlogList() {
  return (
    <section className="max-w-7xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Blog</h1>
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {blogPosts.map((post) => (
          <Card
            key={post.slug}
            href={`/blog/${post.slug}`}
            title={post.title}
            excerpt={post.excerpt}
            category={post.category}
            slug={post.slug}
            type="blog"
          />
        ))}
      </div>
    </section>
  );
}
