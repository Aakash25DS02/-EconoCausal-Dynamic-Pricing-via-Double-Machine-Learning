
import { useState } from "react";

export default function BudgetSettings({ budget, onSave }) {
  const [amount, setAmount] = useState(budget ?? "");
  const [message, setMessage] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    const value = Number(amount);

    if (amount === "" || !Number.isFinite(value) || value <= 0) {
      setMessage("Please enter a budget greater than zero.");
      return;
    }

    onSave(value);
    setMessage("Budget saved successfully!");
  }

  return (
    <section className="panel">
      <h2>Budget Settings</h2>
      <p>Set the budget for your pricing or marketing campaign.</p>

      <form onSubmit={handleSubmit}>
        <label htmlFor="budget">Campaign Budget (₹)</label>

        <input
          id="budget"
          type="number"
          min="0.01"
          step="0.01"
          value={amount}
          onChange={(event) => {
            setAmount(event.target.value);
            setMessage("");
          }}
          placeholder="Enter budget amount"
          required
        />

        <button className="save-button" type="submit">
          Save Budget
        </button>
      </form>

      {message && (
        <p role="status" style={{ color: "#244c91" }}>
          {message}
        </p>
      )}

      {budget !== null && budget !== undefined && (
        <p>
          <strong>Current saved budget:</strong>{" "}
          ₹{budget.toLocaleString("en-IN")}
        </p>
      )}
    </section>
  );
}
