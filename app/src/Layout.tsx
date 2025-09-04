import { useEffect} from "react";
// import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";

interface LayoutProps {
  title: string;
  children: React.ReactNode;
}

export const Layout = ({ title, children }: LayoutProps) => {
  
  useEffect(() => {
    document.title = title;
  }, [title]);
  
  return (
    <div className="min-h-screen w-full flex flex-col">
      <Navbar />

      <main className="w-full flex-grow">
        {children}
      </main> 

      {/* <Footer /> */}
    </div>
  );
};