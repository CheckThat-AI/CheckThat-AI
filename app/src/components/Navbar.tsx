import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogTrigger } from '@/components/ui/dialog';
import { Login } from './Login';
import { ModeToggle } from './mode-toggle';
// import {
//   NavigationMenu,
//   NavigationMenuItem,
//   NavigationMenuLink,
//   NavigationMenuList,
//   navigationMenuTriggerStyle,
// } from '@/components/ui/navigation-menu';
// import { cn } from '@/lib/utils';
import { supabase } from '@/lib/supabase';
import checkThatLogo from '../assets/Checkthat-logo.svg';

// interface NavigationItem {
//   label: string;
//   href: string;
//   external?: boolean;
//   description?: string;
// }

// const navigationItems: NavigationItem[] = [
//   { 
//     label: 'Features', 
//     href: '#features',
//     description: 'Explore our comprehensive platform capabilities'
//   },
//   { 
//     label: 'Documentation', 
//     href: '#docs',
//     description: 'Learn how to use CheckThat.AI effectively'
//   },
//   { 
//     label: 'Blog', 
//     href: '/blog', 
//     external: true,
//     description: 'View source code and contribute'
//   },
//   { 
//     label: 'Contact', 
//     href: '#contact',
//     description: 'Get in touch with our team'
//   },
// ];

export default function Navbar() {
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [hasActiveSession, setHasActiveSession] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  
  // Check if we're on the landing page
  const isLandingPage = location.pathname === '/';

  useEffect(() => {
    // Check for active session on component mount
    const checkActiveSession = async () => {
      try {
        // First check Supabase session
        const { data: { session } } = await supabase.auth.getSession();
        if (session?.user) {
          setHasActiveSession(true);
          setIsAuthenticated(true);
          return;
        }

        // Then check for guest session
        const guestSession = localStorage.getItem('guest_session');
        if (guestSession) {
          const guest = JSON.parse(guestSession);
          if (guest.isGuest) {
            setHasActiveSession(true);
            setIsAuthenticated(false); // Guest is not authenticated
            return;
          }
        }

        // Check for stored user info
        const userInfo = localStorage.getItem('user_info');
        if (userInfo) {
          const user = JSON.parse(userInfo);
          if (user.id && user.sessionId && !user.isGuest) {
            setHasActiveSession(true);
            setIsAuthenticated(true);
            return;
          }
        }

        setHasActiveSession(false);
        setIsAuthenticated(false);
      } catch (error) {
        console.error('Error checking session:', error);
        setHasActiveSession(false);
        setIsAuthenticated(false);
      }
    };

    checkActiveSession();

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        if (event === 'SIGNED_IN' && session?.user) {
          setHasActiveSession(true);
          setIsAuthenticated(true);
        } else if (event === 'SIGNED_OUT') {
          setHasActiveSession(false);
          setIsAuthenticated(false);
        }
      }
    );

    // Listen for custom guest session events
    const handleGuestSessionCreated = () => {
      setHasActiveSession(true);
      setIsAuthenticated(false);
    };

    window.addEventListener('guestSessionCreated', handleGuestSessionCreated);

    return () => {
      subscription.unsubscribe();
      window.removeEventListener('guestSessionCreated', handleGuestSessionCreated);
    };
  }, []);

  const handleGetStartedClick = () => {
    // Check for active session first
    if (hasActiveSession && isAuthenticated) {
      // If user has active session, redirect to chat/dashboard
      navigate('/chat');
    } else {
      // If no active session, open login dialog
      setIsLoginOpen(true);
    }
  };

  // const handleLinkClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
  //   if (href.startsWith('#')) {
  //     e.preventDefault();
  //     const targetElement = document.querySelector(href);
  //     if (targetElement) {
  //       const offset = -85;
  //       const elementPosition = targetElement.getBoundingClientRect().top;
  //       const offsetPosition = elementPosition + window.scrollY + offset;

  //       window.scrollTo({
  //         top: offsetPosition,
  //         behavior: "smooth",
  //       });
  //     }
  //   } else if (href.startsWith('/')) {
  //     // For internal routes like /docs, allow react-router-dom to handle it
  //     return;
  //   } 
  //   // For external links, do nothing as target="_blank" handles it
  // };


  return (
    <header className="fixed top-0 z-50 w-full border-b bg-background/80 backdrop-blur-xl">
      <div className="container mx-auto flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo */}
        <div className="flex items-center space-x-2 cursor-pointer" onClick={() => window.location.href = '/'}>
          <img 
            src={checkThatLogo}
            alt="CheckThat AI Logo"
            className="h-8 w-auto"
          />
          <div className="text-xl font-bold">
            CheckThat<span className="text-primary"> AI</span>
          </div>
        </div>

        {/* Navigation Menu - Hidden on mobile */}
        {/* <div className="hidden md:flex">
          <NavigationMenu>
            <NavigationMenuList>
              <NavigationMenuItem>
                <NavigationMenuLink 
                  className={navigationMenuTriggerStyle()}
                  asChild
                >
                  <a
                    href={navigationItems[0].href}
                    onClick={(e) => handleLinkClick(e, navigationItems[0].href)}
                  >
                    {navigationItems[0].label}
                  </a>
                </NavigationMenuLink>
              </NavigationMenuItem>
              
              <NavigationMenuItem>
                <NavigationMenuLink 
                  className={navigationMenuTriggerStyle()}
                  asChild
                >
                  <a
                    href={navigationItems[1].href}
                    onClick={(e) => handleLinkClick(e, navigationItems[1].href)}
                  >
                    {navigationItems[1].label}
                  </a>
                </NavigationMenuLink>
              </NavigationMenuItem>
              
              <NavigationMenuItem>
                <NavigationMenuLink 
                  className={navigationMenuTriggerStyle()}
                  asChild
                >
                  <a
                    href={navigationItems[2].href}
                    onClick={(e) => handleLinkClick(e, navigationItems[2].href)}
                  >
                    {navigationItems[2].label}
                  </a>
                </NavigationMenuLink>
              </NavigationMenuItem>
              
              <NavigationMenuItem>
                <NavigationMenuLink 
                  className={navigationMenuTriggerStyle()}
                  asChild
                >
                  <a
                    href={navigationItems[3].href}
                    onClick={(e) => handleLinkClick(e, navigationItems[3].href)}
                  >
                    {navigationItems[3].label}
                  </a>
                </NavigationMenuLink>
              </NavigationMenuItem>
            </NavigationMenuList>
          </NavigationMenu>
        </div> */}

        {/* Right side actions */}
        <div className="flex items-center gap-3">
          {/* Theme Toggle */}
          <ModeToggle />
          
          {/* Get Started Button with smart logic */}
          {hasActiveSession && isAuthenticated && isLandingPage? (
            <Button 
              className="bg-primary hover:bg-primary/90"
              onClick={handleGetStartedClick}
            >
              Go to Dashboard
            </Button>
          ) : (
            <Dialog open={isLoginOpen} onOpenChange={setIsLoginOpen}>
              <DialogTrigger asChild>
                <Button 
                  className="bg-primary hover:bg-primary/90"
                  onClick={handleGetStartedClick}
                >
                  Get Started
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[425px]">
                <Login onSuccess={() => {
                  setIsLoginOpen(false);
                  // Trigger a re-check of session state after login
                  setTimeout(() => {
                    // Re-check session state
                    const checkSession = async () => {
                      try {
                        const { data: { session } } = await supabase.auth.getSession();
                        if (session?.user) {
                          setHasActiveSession(true);
                          setIsAuthenticated(true);
                          return;
                        }
                        
                        const guestSession = localStorage.getItem('guest_session');
                        if (guestSession) {
                          const guest = JSON.parse(guestSession);
                          if (guest.isGuest) {
                            setHasActiveSession(true);
                            setIsAuthenticated(false);
                            return;
                          }
                        }
                        
                        setHasActiveSession(false);
                        setIsAuthenticated(false);
                      } catch (error) {
                        console.error('Error re-checking session:', error);
                      }
                    };
                    checkSession();
                  }, 100);
                }} />
              </DialogContent>
            </Dialog>
          )}
        </div>
      </div>
    </header>
  );
}

// ListItem component for NavigationMenuContent
// const ListItem = React.forwardRef<React.ComponentRef<"a">, 
//   React.ComponentPropsWithoutRef<"a"> & {
//     title: string;
//     onClick?: (e: React.MouseEvent<HTMLAnchorElement>) => void;
//   }
// >(({ className, title, children, onClick, ...props }, ref) => {
//   return (
//     <li>
//       {/* <NavigationMenuLink asChild>
//         <a
//           ref={ref}
//           className={cn(
//             "block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground",
//             className
//           )}
//           onClick={onClick}
//           {...props}
//         >
//           <div className="text-sm font-medium leading-none">{title}</div>
//           <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
//             {children}
//           </p>
//         </a>
//       </NavigationMenuLink> */}
//     </li>
//   )
// })
// ListItem.displayName = "ListItem";
