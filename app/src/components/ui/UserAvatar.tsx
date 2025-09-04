import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { User } from 'lucide-react';
import { generateInitials, getInitialsBackgroundColor } from '@/utils/avatarUtils';

interface UserAvatarProps {
  user: {
    firstName?: string;
    lastName?: string;
    picture?: string;
    isGuest?: boolean;
  };
  className?: string;
  fallbackClassName?: string;
  showGuestIcon?: boolean;
}

export function UserAvatar({ 
  user, 
  className = "h-8 w-8", 
  fallbackClassName = "",
  showGuestIcon = true 
}: UserAvatarProps) {
  const initials = generateInitials(user.firstName, user.lastName);
  const bgColorClass = getInitialsBackgroundColor(initials);

  return (
    <Avatar className={className}>
      {/* For authenticated users, don't show the picture anymore, just use initials */}
      {!user.isGuest ? (
        <AvatarFallback 
          className={`${bgColorClass} text-white font-semibold text-sm flex items-center justify-center ${fallbackClassName || 'rounded-full'}`}
        >
          {initials}
        </AvatarFallback>
      ) : (
        <>
          {/* Guest users can still have picture fallback */}
          <AvatarImage src={user.picture} alt={user.firstName || 'User'} />
          <AvatarFallback className={`${fallbackClassName} bg-muted text-muted-foreground`}>
            {showGuestIcon ? <User className="h-4 w-4" /> : initials}
          </AvatarFallback>
        </>
      )}
    </Avatar>
  );
}
