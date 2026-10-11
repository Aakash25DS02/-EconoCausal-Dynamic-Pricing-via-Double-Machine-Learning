import DataUpload from "./pages/DataUpload.jsx";


import { useState } from "react";
import "./index.css";

export default function App() {
  const [activePage, setActivePage] = useState("Dashboard");

  const menuItems = [
    "Dashboard",
    "Data Upload",
    "Budget Settings",
    "Treatment Effects",
  ];

  return (
    <div className="app">
      <aside className="sidebar">
        <h2>EconoCausal</h2>
        <p className="subtitle">Pricing Intelligence</p>

        {menuItems.map((item) => (
          <button
            key={item}
            className={`nav-item ${
              activePage === item ? "active" : ""
            }`}
            onClick={() => setActivePage(item)}
          >
            {item}
          </button>
        ))}
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h1>{activePage}</h1>
            <p>Dynamic Pricing via Double Machine Learning</p>
          </div>
          <span className="status">Frontend Preview</span>
        </header>

        {activePage === "Dashboard" && (
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
                <h2>Not Uploaded</h2>
              </div>
              <div className="stat-card">
                <p>Estimated Price Effect</p>
                <h2>—</h2>
              </div>
              <div className="stat-card">
                <p>Budget</p>
                <h2>Not Set</h2>
              </div>
            </div>

            <section className="panel">
              <h2>Getting Started</h2>
              <p>1. Upload your pricing dataset.</p>
              <p>2. Configure your pricing budget.</p>
              <p>3. View treatment effects after model results are available.</p>
            </section>
          </>
        )}

        {activePage === "Data Upload" && <DataUpload />}

        {activePage === "Budget Settings" && (
          <section className="panel">
            <h2>Budget Settings</h2>
            <label htmlFor="budget">Campaign budget (₹)</label>
            <input
              id="budget"
              type="number"
              min="0"
              placeholder="Enter your budget"
            />
            <p className="note">
              Preview only: budget is not saved to a backend.
            </p>
          </section>
        )}

        {activePage === "Treatment Effects" && (
          <section className="panel">
            <h2>Treatment Effect Analysis</h2>
            <p>
              Estimated effects and charts will appear here
              when model results are available.
            </p>
            <div className="chart-placeholder">
              Treatment effect visualization
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
