export default function Navbar() {
  return (
    <header className="h-14 bg-[#0f1923] border-b border-[#1e2a3a] flex items-center justify-between px-6 flex-shrink-0">
      <div className="text-xs text-[#8b9ab0]">
        Supply Chain Visibility — Demo Tenant
      </div>
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-xs text-[#8b9ab0]">
          <span className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse" />
          Live
        </div>
        {/* Phase 2: Supabase auth button goes here */}
        <div className="w-7 h-7 rounded-full bg-[#10b981]/20 border border-[#10b981]/30 flex items-center justify-center text-xs text-[#10b981] font-semibold">
          D
        </div>
      </div>
    </header>
  )
}
