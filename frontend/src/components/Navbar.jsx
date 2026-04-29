import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Navbar() {
  const { user, signOut, supabaseConfigured } = useAuth()
  const navigate = useNavigate()

  async function handleSignOut() {
    await signOut()
    navigate('/login', { replace: true })
  }

  const initial = user?.email?.[0]?.toUpperCase() ?? 'D'
  const label = user?.email ?? (supabaseConfigured ? 'Anonymous' : 'Demo Tenant')

  return (
    <header className="h-14 bg-[#0f1923] border-b border-[#1e2a3a] flex items-center justify-between px-6 flex-shrink-0">
      <div className="text-xs text-[#8b9ab0]">
        Supply Chain Visibility — {label}
      </div>
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-xs text-[#8b9ab0]">
          <span className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse" />
          Live
        </div>
        <Link
          to="/billing"
          className="text-[10px] text-[#8b9ab0] hover:text-[#10b981] uppercase tracking-wide"
        >
          Billing
        </Link>
        <div className="w-7 h-7 rounded-full bg-[#10b981]/20 border border-[#10b981]/30 flex items-center justify-center text-xs text-[#10b981] font-semibold">
          {initial}
        </div>
        {supabaseConfigured && user && (
          <button
            onClick={handleSignOut}
            className="text-[10px] text-[#8b9ab0] hover:text-red-400 uppercase tracking-wide"
          >
            Sign out
          </button>
        )}
      </div>
    </header>
  )
}
