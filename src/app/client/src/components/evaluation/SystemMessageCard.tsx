import React from 'react';
import { motion } from 'framer-motion';

export default function SystemMessageCard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="px-2 py-4 rounded-md mx-auto max-w-6xl w-full 
      border-b border-slate-800 shadow-xl"
    >
      <p className="text-slate-100 text-center">
        This is the batch mode interface for processing large datasets. If you wish to extract claims from a single source, please switch back to Chat mode.
      </p>
    </motion.div>
  );
} 