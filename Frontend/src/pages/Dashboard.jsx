
export default function Dashboard({ budget, dataset }) {
  return (
    <>
      <div className="welcome">
        <h2>Welcome to EconoCausal</h2>
        <p>
          Analyze pricing decisions and estimate their
          impact on customer demand.
        </p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <p>Dataset Status</p>
          <h2>{dataset ? "Uploaded" : "Not Uploaded"}</h2>
        </div>

        <div className="stat-card">
          <p>Estimated Price Effect</p>
          <h2>—</h2>
        </div>

        <div className="stat-card">
          <p>Budget</p>
          <h2>
            {budget !== null
              ? `₹${budget.toLocaleString("en-IN")}`
              : "Not Set"}
          </h2>
        </div>
      </div>

      <section className="panel">
        <h2>Getting Started</h2>
        <p>1. Upload your pricing dataset.</p>
        <p>2. Configure your pricing budget.</p>
        <p>3. View treatment effects when model results are available.</p>
      </section>
    </>
  );
}
