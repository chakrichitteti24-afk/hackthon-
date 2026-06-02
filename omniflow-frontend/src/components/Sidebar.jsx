import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  MessageSquare, 
  Database, 
  BarChart3, 
  AlertCircle, 
  Cpu, 
  Settings as SettingsIcon 
} from 'lucide-react';

const navItems = [
  { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { label: 'Workspace', path: '/', icon: MessageSquare },
  { label: 'Customer Memory', path: '/customer-memory', icon: Database },
];

export default function Sidebar() {
  return (
    <aside className="hidden w-64 shrink-0 border-r border-border bg-white flex flex-col justify-between h-screen sticky top-0 md:flex">
      <div className="p-6">
        <div className="mb-8 flex items-center gap-3">
          <div className="w-9 h-9 bg-primary rounded-lg flex items-center justify-center shadow-soft">
            <span className="text-white text-lg font-bold">O</span>
          </div>
          <div>
            <h2 className="text-sm font-semibold text-text tracking-tight uppercase">OmniFlow AI</h2>
            <p className="text-[10px] font-medium text-muted uppercase tracking-wider">Enterprise SaaS</p>
          </div>
        </div>
        
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.label}
                to={item.path}
                className={({ isActive }) =>
                  [
                    'flex items-center gap-3 rounded-lg px-3.5 py-2.5 text-sm font-medium transition-all duration-150',
                    isActive
                      ? 'bg-primary/5 text-primary'
                      : 'text-muted hover:bg-bg hover:text-text',
                  ].join(' ')
                }
              >
                <Icon className="w-4 h-4" />
                {item.label}
              </NavLink>
            );
          })}
        </nav>
      </div>
      
      <div className="p-6 border-t border-border bg-bg/30">
        <div className="rounded-lg bg-white p-3.5 border border-border shadow-soft">
          <div className="flex items-center justify-between mb-1.5">
            <p className="text-[10px] font-semibold text-muted uppercase tracking-wider">System Health</p>
            <span className="text-[10px] font-bold text-success">98%</span>
          </div>
          <div className="h-1.5 w-full bg-border rounded-full overflow-hidden">
            <div className="h-full bg-success w-[98%] rounded-full" />
          </div>
        </div>
      </div>
    </aside>
  );
}
