export default function RouteOptimizer() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-white">Route Optimizer</h1>
        <p className="text-xs text-[#8b9ab0] mt-0.5">OR-Tools VRP solver — coming in v3.1</p>
      </div>
      <div className="card p-8 text-center">
        <div className="text-4xl mb-3">🗺️</div>
        <div className="text-sm text-gray-300 mb-1">Multi-stop route optimization</div>
        <div className="text-xs text-[#8b9ab0]">
          Plan optimal delivery sequences across vehicles using vehicle-routing-problem solvers.
        </div>
      </div>
    </div>
  )
}
