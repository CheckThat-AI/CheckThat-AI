import { createRoot } from "react-dom/client";
import { 
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query';
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/toaster";
import { AppProvider } from "@/contexts/AppContext";
import App from "./App";
import "./index.css";
import './components/scrollbar-hide.css';

// Create a client
const queryClient = new QueryClient();

createRoot(document.getElementById("root")!).render(
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <AppProvider>
        <App />
        <Toaster />
      </AppProvider>
    </TooltipProvider>
  </QueryClientProvider>
);
