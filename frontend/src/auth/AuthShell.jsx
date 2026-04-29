export default function AuthShell({ title, subtitle, children, footer }) {
  return (
    <div className="min-h-screen bg-[#0a0f1a] text-white flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center justify-center gap-2 mb-6">
          <div className="w-9 h-9 bg-[#10b981]/10 border border-[#10b981]/30 rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-[#10b981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
          <div>
            <div className="text-base font-semibold tracking-wide">ShipLogix</div>
            <div className="text-[10px] text-[#10b981] tracking-widest uppercase">Supply Chain Visibility</div>
          </div>
        </div>

        <div className="bg-[#0f1923] border border-[#1e2a3a] rounded-xl p-6">
          <div className="mb-5">
            <h1 className="text-lg font-semibold">{title}</h1>
            {subtitle && <p className="text-xs text-[#8b9ab0] mt-1">{subtitle}</p>}
          </div>
          {children}
        </div>

        {footer && <div className="text-center text-xs text-[#8b9ab0] mt-4">{footer}</div>}
      </div>
    </div>
  )
}
