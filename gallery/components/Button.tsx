"use client";

import Link from "next/link";
import type { ReactNode } from "react";

type ButtonProps = {
  children: ReactNode;
  href?: string;
  variant?: "primary" | "outline";
  onClick?: () => void;
  className?: string;
};

export function Button({ children, href, variant = "primary", onClick, className = "" }: ButtonProps) {
  const base = "px-4 py-2 rounded-xl font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-primary";
  const styles = {
    primary: "bg-primary text-white hover:bg-primary-hover dark:bg-primary-dark dark:hover:bg-primary-dark",
    outline: "border border-primary text-primary bg-transparent hover:bg-primary/10 dark:border-primary-dark dark:text-primary-dark",
  };

  const combined = `${base} ${styles[variant]} ${className}`;

  if (href) {
    return (
      <Link href={href} className={combined} onClick={onClick}>
        {children}
      </Link>
    );
  }

  return (
    <button type="button" className={combined} onClick={onClick}>
      {children}
    </button>
  );
}
