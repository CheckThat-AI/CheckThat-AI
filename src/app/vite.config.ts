import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import themePlugin from "@replit/vite-plugin-shadcn-theme-json";
import path from "path";
import runtimeErrorOverlay from "@replit/vite-plugin-runtime-error-modal";

export default defineConfig({
  // Set base URL for GitHub Pages deployment
  // Replace 'your-repo-name' with your actual repository name
  base: process.env.NODE_ENV === "production" ? "/clef2025-checkthat-lab-task2/" : "/",
  
  plugins: [
    react(),
    // Only include development plugins in development mode
    ...(process.env.NODE_ENV !== "production" ? [runtimeErrorOverlay()] : []),
    themePlugin(),
    ...(process.env.NODE_ENV !== "production" &&
    process.env.REPL_ID !== undefined
      ? [
          await import("@replit/vite-plugin-cartographer").then((m) =>
            m.cartographer(),
          ),
        ]
      : []),
  ],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "client", "src"),
      "@shared": path.resolve(import.meta.dirname, "shared"),
      "@assets": path.resolve(import.meta.dirname, "attached_assets"),
    },
  },
  root: path.resolve(import.meta.dirname, "client"),
  build: {
    // Output to docs folder at repository root for GitHub Pages
    outDir: path.resolve(import.meta.dirname, "../../docs"),
    emptyOutDir: true,
    // Ensure assets use relative paths
    assetsDir: "assets",
    // Generate source maps for easier debugging
    sourcemap: false,
    // Optimize for production
    minify: "esbuild",
  },
  // Ensure the preview server works correctly
  preview: {
    port: 4173,
    host: true,
  },
});
