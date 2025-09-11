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
      {/* Show profile image if available for both guest and authenticated users */}
      {user.picture ? (
        <AvatarImage 
          src={user.picture} 
          alt={user.firstName || 'User'} 
          className="object-cover"
        />
      ) : null}
      <AvatarFallback 
        className={`${user.isGuest ? 'bg-muted text-muted-foreground' : bgColorClass} text-white font-semibold text-sm flex items-center justify-center ${fallbackClassName || 'rounded-full'}`}
      >
        {user.isGuest && showGuestIcon ? <User className="h-4 w-4" /> : initials}
      </AvatarFallback>
    </Avatar>
  );
}
