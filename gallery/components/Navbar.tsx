"use client";

import Link from "next/link";
import { DarkModeToggle } from "./DarkModeToggle";

export function Navbar() {
  return (
    <header className="bg-surface dark:bg-surface-dark border-b border-border dark:border-border-dark">
      <nav className="max-w-7xl mx-auto flex items-center justify-between p-4">
        <Link href="/" className="text-text dark:text-text-dark font-semibold text-xl">
          UI/UX Pro Max
        </Link>
        <ul className="flex gap-4 items-center">
          <li>
            <Link href="/" aria-label="Home" className="text-muted dark:text-muted hover:underline">
              Home
            </Link>
          </li>
          <li>
            <Link href="/blog" aria-label="Blog" className="text-muted dark:text-muted hover:underline">
              Blog
            </Link>
          </li>
          <li>
            <Link href="/courses" aria-label="Courses" className="text-muted dark:text-muted hover:underline">
              Courses
            </Link>
          </li>
          <li>
            <DarkModeToggle />
          </li>
        </ul>
      </nav>
    </header>
  );
}
