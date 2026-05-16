import { NavLink } from 'react-router-dom';

const navItems = [
  { label: 'Chat', path: '/' },
  { label: 'Dashboard', path: '/dashboard' },
];

export default function Sidebar() {
  return (
    <aside className="hidden w-56 shrink-0 border-r border-primary/20 bg-black/40 p-4 md:block">
      <div className="mb-8">
        <p className="text-lg font-semibold text-primary">OmniFlow</p>
        <p className="text-xs text-secondary/80">Multi-agent console</p>
      </div>
      <nav className="space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              [
                'block rounded-md px-3 py-2 text-sm transition',
                isActive
                  ? 'bg-primary text-bg shadow-neon'
                  : 'text-primary/80 hover:bg-primary/10 hover:text-primary',
              ].join(' ')
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
