
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from "recharts";

const allocationPercentages = [
  { name: "Customer Group A", percentage: 40, color: "#2563eb" },
  { name: "Customer Group B", percentage: 35, color: "#7c3aed" },
  { name: "Customer Group C", percentage: 25, color: "#0d9488" }
];


function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2
  }).format(value);
}


export default function BudgetAllocation({ budget }) {
  const hasBudget =
    Number.isFinite(Number(budget)) && Number(budget) > 0;

  if (!hasBudget) {
    return (
      <section className="panel">
        <h2>Budget Allocation</h2>
        <p>
          Please save a campaign budget in Budget Settings
          before viewing the allocation plan.
        </p>
      </section>
    );
  }

  // Illustrative plan: allocate 75% of the saved budget.
  const allocatedBudget = Number(budget) * 0.75;
  const remainingBudget = Number(budget) - allocatedBudget;

  const allocationData = allocationPercentages.map((group) => ({
    ...group,
    amount: allocatedBudget * (group.percentage / 100)
  }));

  const chartData = [
    ...allocationData.map((group) => ({
      name: group.name,
      amount: Number(group.amount.toFixed(2)),
      color: group.color
    })),
    {
      name: "Remaining Budget",
      amount: Number(remainingBudget.toFixed(2)),
      color: "#94a3b8"
    }
  ];

  return (
    <div className="page">
      <h1>Budget Allocation</h1>
      <p>
        View an illustrative discount budget distribution
        while keeping track of the remaining campaign budget.
      </p>

      <p role="note">
        <strong>Demo mode:</strong> These allocations are
        sample values, not recommendations from the causal
        machine learning model.
      </p>

      <div className="stats-grid">
        <section className="panel">
          <h3>Total Budget</h3>
          <h2>{formatCurrency(Number(budget))}</h2>
        </section>

        <section className="panel">
          <h3>Allocated Budget</h3>
          <h2>{formatCurrency(allocatedBudget)}</h2>
        </section>

        <section className="panel">
          <h3>Remaining Budget</h3>
          <h2>{formatCurrency(remainingBudget)}</h2>
        </section>
      </div>

      <section className="panel">
        <h2>Budget Distribution</h2>
        <p>
          Compare the illustrative allocations with the
          amount of budget left unallocated.
        </p>

        <div style={{ width: "100%", height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                dataKey="amount"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ name, percent }) =>
                  `${name}: ${(percent * 100).toFixed(0)}%`
                }
              >
                {chartData.map((item) => (
                  <Cell
                    key={item.name}
                    fill={item.color}
                  />
                ))}
              </Pie>
              <Tooltip
                formatter={(value) => formatCurrency(Number(value))}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="panel">
        <h2>Allocation by Customer Group</h2>

        <div style={{ width: "100%", height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={allocationData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip
                formatter={(value) => formatCurrency(Number(value))}
              />
              <Bar dataKey="amount" name="Allocated Amount">
                {allocationData.map((group) => (
                  <Cell
                    key={group.name}
                    fill={group.color}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="panel">
        <h2>Allocation Details</h2>

        <div style={{ overflowX: "auto" }}>
          <table>
            <thead>
              <tr>
                <th>Customer Group</th>
                <th>Allocation Share</th>
                <th>Budget Amount</th>
              </tr>
            </thead>

            <tbody>
              {allocationData.map((group) => (
                <tr key={group.name}>
                  <td>{group.name}</td>
                  <td>{group.percentage}%</td>
                  <td>{formatCurrency(group.amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p>
          <strong>Budget check:</strong>{" "}
          {allocatedBudget + remainingBudget <= Number(budget)
            ? "The allocation stays within the saved budget."
            : "The allocation exceeds the saved budget."}
        </p>
      </section>
    </div>
  );
}
