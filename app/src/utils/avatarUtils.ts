/**
 * Utility functions for avatar handling
 */

/**
 * Generate initials from first and last name
 * @param firstName - User's first name
 * @param lastName - User's last name
 * @returns Two character initials (e.g., "NK" for Nathan Kant)
 */
export function generateInitials(firstName?: string, lastName?: string): string {
  if (!firstName && !lastName) {
    return 'U'; // Default to 'U' for User
  }
  
  const first = firstName?.trim().charAt(0).toUpperCase() || '';
  const last = lastName?.trim().charAt(0).toUpperCase() || '';
  
  if (first && last) {
    return `${first}${last}`;
  } else if (first) {
    return first;
  } else if (last) {
    return last;
  }
  
  return 'U';
}

/**
 * Generate a consistent background color based on user initials
 * @param initials - User initials
 * @returns CSS class for background color
 */
export function getInitialsBackgroundColor(initials: string): string {
  // Generate a consistent color based on the initials
  const colors = [
    'bg-red-500',
    'bg-blue-500', 
    'bg-green-500',
    'bg-yellow-500',
    'bg-purple-500',
    'bg-pink-500',
    'bg-indigo-500',
    'bg-teal-500',
    'bg-orange-500',
    'bg-cyan-500'
  ];
  
  // Create a simple hash from initials
  let hash = 0;
  for (let i = 0; i < initials.length; i++) {
    hash = initials.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  // Use absolute value to ensure positive index
  const index = Math.abs(hash) % colors.length;
  return colors[index];
}
