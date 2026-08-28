import fs from "fs";
import path from "path";
import { parseStylesCSV } from "@/lib/parseStyles";
import { GalleryGrid } from "@/components/GalleryGrid";
import { Hero } from "@/components/Hero";

export default function Home() {
  const csvPath = path.join(process.cwd(), "data", "styles.csv");
  const csvContent = fs.readFileSync(csvPath, "utf-8");
  const styles = parseStylesCSV(csvContent);

  return (
    <main>
      <Hero
        title="Explore 67 UI Styles"
        subtitle="Find the perfect visual language for your product"
        ctaHref="/gallery"
        ctaLabel="Browse Gallery"
      />
      <GalleryGrid styles={styles} />
    </main>
  );
}
