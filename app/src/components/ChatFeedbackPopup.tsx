import React from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, ExternalLink } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

interface ChatFeedbackPopupProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmitFeedback: () => void;
}

const ChatFeedbackPopup: React.FC<ChatFeedbackPopupProps> = ({
  isOpen,
  onClose,
  onSubmitFeedback,
}) => {
  const handleSubmitFeedback = () => {
    window.open('https://docs.google.com/forms/d/e/1FAIpQLScyQB7-vpfaOGtXfXSbwdpT6ytrVG-TT9k6GT8v8wEO_ivAAA/viewform?usp=header', '_blank');
    onSubmitFeedback();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md border-0 bg-gradient-to-br from-white to-gray-50 dark:from-gray-900 dark:to-gray-800">
        <motion.div
          initial={{ opacity: 0, scale: 0.8, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.8, y: 20 }}
          transition={{
            type: "spring",
            stiffness: 300,
            damping: 30,
            duration: 0.4
          }}
          className="relative overflow-hidden"
        >
          {/* Animated background gradient */}
          <motion.div
            className="absolute inset-0 rounded-lg"
            animate={{
              backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: "linear"
            }}
            style={{
              backgroundSize: "200% 200%"
            }}
          />

          <DialogHeader className="relative z-10 text-center space-y-4">
            {/* Animated icon */}
            <motion.div
              className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg"
              animate={{
                rotate: [0, 10, -10, 0],
                scale: [1, 1.1, 1]
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              <MessageSquare className="w-8 h-8 text-white" />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.3 }}
            >
              <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-amber-400">
                How's CheckThat AI treating you?
              </DialogTitle>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.3 }}
            >
              <DialogDescription className="text-gray-600 dark:text-gray-300 leading-relaxed">
                Your feedback helps us improve our claim normalization platform and make it better for everyone!
              </DialogDescription>
            </motion.div>
          </DialogHeader>

          {/* Animated features list */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.3 }}
            className="relative z-10 mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl"
          >
            <motion.div
              className="flex items-center space-x-2 text-sm text-gray-700 dark:text-gray-300"
              animate={{ x: [0, 5, 0] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            >
              <span className="text-blue-500">✨</span>
              <span>Quick 2-minute survey</span>
            </motion.div>
            <motion.div
              className="flex items-center space-x-2 text-sm text-gray-700 dark:text-gray-300 mt-2"
              animate={{ x: [0, -5, 0] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
            >
              <span className="text-purple-500">🔒</span>
              <span>Anonymous & confidential</span>
            </motion.div>
            <motion.div
              className="flex items-center space-x-2 text-sm text-gray-700 dark:text-gray-300 mt-2"
              animate={{ x: [0, 5, 0] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 1 }}
            >
              <span className="text-pink-500">🚀</span>
              <span>Shapes future updates</span>
            </motion.div>
          </motion.div>

          {/* Animated buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.3 }}
            className="relative z-10 flex flex-col sm:flex-row gap-3 mt-8"
          >
            <Button
              onClick={handleSubmitFeedback}
              className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold 
              py-3 px-6 rounded-xl transition-all duration-300 transform hover:shadow-lg flex items-center justify-center gap-2"
            >
              <motion.span
                whileHover={{ scale: 0.95 }}
                transition={{ type: "spring", stiffness: 400, damping: 10 }}
              >
                Share Feedback
              </motion.span>
              <ExternalLink className="w-4 h-4" />
            </Button>

            <Button
              onClick={onClose}
              variant="outline"
              className="flex-1 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 font-semibold 
              py-3 px-6 rounded-xl transition-all duration-300 transform border-2 border-gray-200 dark:border-gray-600"
            >
              <motion.span
                whileHover={{ scale: 0.95 }}
                transition={{ type: "spring", stiffness: 400, damping: 10 }}
              >
                Maybe Later
              </motion.span>
            </Button>
          </motion.div>
        </motion.div>
      </DialogContent>
    </Dialog>
  );
};

export default ChatFeedbackPopup;
