import type { Express, Request, Response } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import multer from "multer";
import path from "path";
import fs from "fs";

// Configure multer for file uploads
const upload = multer({
  storage: multer.diskStorage({
    destination: function (req, file, cb) {
      if (!fs.existsSync('./uploads')){
        fs.mkdirSync('./uploads');
      }
      cb(null, './uploads');
    },
    filename: function (req, file, cb) {
      cb(null, Date.now() + '-' + file.originalname);
    }
  }),
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    // Allow CSV, JSON, JSONL, and TXT files
    const allowedTypes = [
      'text/csv',
      'application/vnd.ms-excel',
      'application/json',
      'application/x-jsonlines',
      'text/plain'
    ];
    
    if (allowedTypes.includes(file.mimetype) || 
        file.originalname.endsWith('.csv') ||
        file.originalname.endsWith('.json') ||
        file.originalname.endsWith('.jsonl') ||
        file.originalname.endsWith('.txt')) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only CSV, JSON, JSONL, and TXT files are allowed.'));
    }
  }
});

export async function registerRoutes(app: Express): Promise<Server> {
  const server = createServer(app);
  
  // API routes for claim normalization
  
  // Normalize claim endpoint
  app.post('/api/normalize-claims', upload.single('file'), async (req, res) => {
    try {
      const file = req.file;
      
      // Validate input
      if (!file) {
        return res.status(400).json({ 
          detail: 'Please provide a valid file (CSV, JSON, JSONL, or TXT)' 
        });
      }
      
      // The actual processing will be handled by the FastAPI backend through the proxy
      // This endpoint is just for file upload handling
      return res.status(200).json({
        message: 'File uploaded successfully',
        filePath: file.path
      });
      
    } catch (error) {
      console.error('Error processing file:', error);
      return res.status(500).json({ 
        detail: 'Error processing your request' 
      });
    }
  });
  
  return server;
}
