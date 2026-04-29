export default function Carbon() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-white">Carbon Footprint</h1>
        <p className="text-xs text-[#8b9ab0] mt-0.5">CO₂e tracking per shipment — coming in v3.3</p>
      </div>
      <div className="card p-8 text-center">
        <div className="text-4xl mb-3">🌱</div>
        <div className="text-sm text-gray-300 mb-1">Emissions accounting per leg & mode</div>
        <div className="text-xs text-[#8b9ab0]">
          GLEC-aligned CO₂e calculations for road, air, ocean, and rail with tenant-level reporting.
        </div>
      </div>
    </div>
  )
}
