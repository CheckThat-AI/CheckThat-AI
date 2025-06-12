// server/index.ts
import express2 from "express";
import rateLimit from "express-rate-limit";

// server/routes.ts
import { createServer } from "http";
import multer from "multer";
import fs from "fs";
var upload = multer({
  storage: multer.diskStorage({
    destination: function(req, file, cb) {
      if (!fs.existsSync("./uploads")) {
        fs.mkdirSync("./uploads");
      }
      cb(null, "./uploads");
    },
    filename: function(req, file, cb) {
      cb(null, Date.now() + "-" + file.originalname);
    }
  }),
  limits: {
    fileSize: 10 * 1024 * 1024
    // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = [
      "text/csv",
      "application/vnd.ms-excel",
      "application/json",
      "application/x-jsonlines",
      "text/plain"
    ];
    if (allowedTypes.includes(file.mimetype) || file.originalname.endsWith(".csv") || file.originalname.endsWith(".json") || file.originalname.endsWith(".jsonl") || file.originalname.endsWith(".txt")) {
      cb(null, true);
    } else {
      cb(new Error("Invalid file type. Only CSV, JSON, JSONL, and TXT files are allowed."));
    }
  }
});
async function registerRoutes(app2) {
  const server = createServer(app2);
  app2.post("/api/normalize-claims", upload.single("file"), async (req, res) => {
    try {
      const file = req.file;
      if (!file) {
        return res.status(400).json({
          detail: "Please provide a valid file (CSV, JSON, JSONL, or TXT)"
        });
      }
      return res.status(200).json({
        message: "File uploaded successfully",
        filePath: file.path
      });
    } catch (error) {
      console.error("Error processing file:", error);
      return res.status(500).json({
        detail: "Error processing your request"
      });
    }
  });
  return server;
}

// server/vite.ts
import express from "express";
import fs2 from "fs";
import path2 from "path";
import { createServer as createViteServer, createLogger } from "vite";

// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import themePlugin from "@replit/vite-plugin-shadcn-theme-json";
import path from "path";
var vite_config_default = defineConfig({
  base: process.env.NODE_ENV === "production" ? "/" : "/",
  plugins: [
    react(),
    themePlugin()
  ],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "client", "src"),
      "@shared": path.resolve(import.meta.dirname, "shared"),
      "@assets": path.resolve(import.meta.dirname, "attached_assets")
    }
  },
  root: path.resolve(import.meta.dirname, "client"),
  build: {
    outDir: path.resolve(import.meta.dirname, "dist"),
    emptyOutDir: true,
    assetsDir: "assets",
    sourcemap: false,
    minify: "esbuild"
  },
  // Ensure the preview server works correctly
  preview: {
    port: 4173,
    host: true
  }
});

// server/vite.ts
import { nanoid } from "nanoid";
var viteLogger = createLogger();
function log(message, source = "express") {
  const formattedTime = (/* @__PURE__ */ new Date()).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
    hour12: true
  });
  console.log(`${formattedTime} [${source}] ${message}`);
}
async function setupVite(app2, server) {
  const serverOptions = {
    middlewareMode: true,
    hmr: { server },
    allowedHosts: true
  };
  const vite = await createViteServer({
    ...vite_config_default,
    configFile: false,
    customLogger: {
      ...viteLogger,
      error: (msg, options) => {
        viteLogger.error(msg, options);
        process.exit(1);
      }
    },
    server: serverOptions,
    appType: "custom"
  });
  app2.use(vite.middlewares);
  const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limit each IP to 100 requests per windowMs
    message: "Too many requests, please try again later.",
  });

  app2.use("*", limiter, async (req, res, next) => {
    const url = req.originalUrl;
    try {
      const clientTemplate = path2.resolve(
        import.meta.dirname,
        "..",
        "client",
        "index.html"
      );
      let template = await fs2.promises.readFile(clientTemplate, "utf-8");
      template = template.replace(
        `src="/src/main.tsx"`,
        `src="/src/main.tsx?v=${nanoid()}"`
      );
      const page = await vite.transformIndexHtml(url, template);
      res.status(200).set({ "Content-Type": "text/html" }).end(page);
    } catch (e) {
      vite.ssrFixStacktrace(e);
      next(e);
    }
  });
}
function serveStatic(app2) {
  const distPath = path2.resolve(import.meta.dirname, "public");
  if (!fs2.existsSync(distPath)) {
    throw new Error(
      `Could not find the build directory: ${distPath}, make sure to build the client first`
    );
  }
  app2.use(express.static(distPath));
  const staticFileLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // max 100 requests per windowMs
  });
  app2.use("*", staticFileLimiter, (_req, res) => {
    res.sendFile(path2.resolve(distPath, "index.html"));
  });
}

// server/index.ts
import { createProxyMiddleware } from "http-proxy-middleware";
import cors from "cors";
var app = express2();
app.use(cors({
  origin: ["http://localhost:5173", "http://127.0.0.1:5173"],
  credentials: true,
  methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  allowedHeaders: ["Content-Type", "Authorization"]
}));
app.use("/api", createProxyMiddleware({
  target: "http://localhost:8000",
  changeOrigin: true,
  pathRewrite: { "^/api": "" }
  // Remove /api prefix when forwarding to FastAPI
}));
app.use((req, res, next) => {
  const start = Date.now();
  const path3 = req.path;
  let capturedJsonResponse = void 0;
  const originalResJson = res.json;
  res.json = function(bodyJson, ...args) {
    capturedJsonResponse = bodyJson;
    return originalResJson.apply(res, [bodyJson, ...args]);
  };
  res.on("finish", () => {
    const duration = Date.now() - start;
    if (path3.startsWith("/api")) {
      let logLine = `${req.method} ${path3} ${res.statusCode} in ${duration}ms`;
      if (capturedJsonResponse) {
        logLine += ` :: ${JSON.stringify(capturedJsonResponse)}`;
      }
      if (logLine.length > 80) {
        logLine = logLine.slice(0, 79) + "\u2026";
      }
      log(logLine);
    }
  });
  next();
});
(async () => {
  const server = await registerRoutes(app);
  app.use((err, _req, res, _next) => {
    const status = err.status || err.statusCode || 500;
    const message = err.message || "Internal Server Error";
    res.status(status).json({ message });
    throw err;
  });
  if (app.get("env") === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }
  const port = 5173;
  server.listen({
    port,
    host: "0.0.0.0"
  }, () => {
    log(`Frontend server running on port ${port}`);
    log(`API requests will be proxied to http://localhost:8000`);
  });
})();
