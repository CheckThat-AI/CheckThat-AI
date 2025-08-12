import { UserAvatar } from '@/components/ui/UserAvatar';

export function AvatarDemo() {
  const users = [
    {
      firstName: 'Nathan',
      lastName: 'Kant',
      email: 'nathan.kant@example.com',
      isGuest: false
    },
    {
      firstName: 'John',
      lastName: 'Doe',
      email: 'john.doe@example.com',
      isGuest: false
    },
    {
      firstName: 'Alice',
      lastName: 'Smith',
      email: 'alice.smith@example.com',
      isGuest: false
    },
    {
      firstName: 'Guest',
      lastName: 'User',
      email: 'guest@example.com',
      isGuest: true
    }
  ];

  return (
    <div className="p-8 space-y-4">
      <h2 className="text-2xl font-bold mb-6">Avatar Demo</h2>
      
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Authenticated Users (Initials)</h3>
        <div className="flex gap-4 items-center">
          {users.filter(u => !u.isGuest).map((user, idx) => (
            <div key={idx} className="flex flex-col items-center gap-2">
              <UserAvatar 
                user={user} 
                className="w-12 h-12 rounded-full"
              />
              <span className="text-sm">{user.firstName} {user.lastName}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Guest User (Icon)</h3>
        <div className="flex gap-4 items-center">
          {users.filter(u => u.isGuest).map((user, idx) => (
            <div key={idx} className="flex flex-col items-center gap-2">
              <UserAvatar 
                user={user} 
                className="w-12 h-12 rounded-full"
              />
              <span className="text-sm">{user.firstName} {user.lastName}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Different Sizes</h3>
        <div className="flex gap-4 items-center">
          <UserAvatar 
            user={users[0]} 
            className="w-8 h-8 rounded-full"
          />
          <UserAvatar 
            user={users[0]} 
            className="w-10 h-10 rounded-full"
          />
          <UserAvatar 
            user={users[0]} 
            className="w-12 h-12 rounded-full"
          />
          <UserAvatar 
            user={users[0]} 
            className="w-16 h-16 rounded-full"
          />
        </div>
      </div>
    </div>
  );
}
