import fs from "fs";
import path from "path";
import { parseStylesCSV } from "@/lib/parseStyles";
import { GalleryGrid } from "@/components/GalleryGrid";

export default function Home() {
  const csvPath = path.join(process.cwd(), "data", "styles.csv");
  const csvContent = fs.readFileSync(csvPath, "utf-8");
  const styles = parseStylesCSV(csvContent);

  return (
    <main>
      <GalleryGrid styles={styles} />
    </main>
  );
}
