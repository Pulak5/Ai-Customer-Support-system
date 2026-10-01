"use client";

import type { ButtonHTMLAttributes } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  loading?: boolean;
};

export function Button({ children, className = "", loading = false, disabled, ...props }: ButtonProps) {
  return (
    <button className={`button primary ${className}`} disabled={disabled || loading} {...props}>
      {loading ? "Working…" : children}
    </button>
  );
}
