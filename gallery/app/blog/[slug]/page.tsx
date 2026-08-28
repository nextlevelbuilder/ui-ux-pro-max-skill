import { blogPosts } from "../../data/blogPosts";
import { notFound } from "next/navigation";
import { Hero } from "@/components/Hero";

export default function BlogPost({ params }: { params: { slug: string } }) {
  const post = blogPosts.find((p) => p.slug === params.slug);
  if (!post) {
    notFound();
  }
  return (
    <article className="prose dark:prose-invert max-w-4xl mx-auto p-4">
      <Hero
        title={post.title}
        subtitle={post.excerpt}
        imageSrc="https://images.unsplash.com/photo-1498050108023-c5249f4df085"
      />
      <p>{post.excerpt}</p>
      <p>
        {/* Placeholder content – in a real project replace with markdown rendering */}
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus
        suscipit, ultricies mi sit amet, ullamcorper augue.
      </p>
    </article>
  );
}
