import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export interface ExternalLink {
  url: string;
  target?: "_blank" | "_self";
  rel?: "noopener" | "noreferrer";
}

export interface HyperLink {
  link: ExternalLink;
  description: string;
}