from pathlib import Path


def create_synthetic_causal_graph():
    """Create a DAG representing the synthetic data-generation process."""

    graph = r"""
digraph SyntheticEconoCausal {
    rankdir=LR;
    node [shape=box, style="rounded,filled", fontname="Arial"];

    Price [label="Price", fillcolor="lightblue"];
    CompetitorPrice [label="Competitor Price", fillcolor="lightblue"];
    Promotion [label="Promotion", fillcolor="lightblue"];
    Season [label="Season", fillcolor="lightblue"];
    Discount [label="Discount (Treatment)", fillcolor="gold"];
    Purchase [label="Purchase (Outcome)", fillcolor="lightgreen"];

    Price -> CompetitorPrice;
    Price -> Purchase;
    CompetitorPrice -> Purchase;
    Promotion -> Purchase;
    Season -> Purchase;
    Discount -> Purchase;
}
"""

    output_path = Path("synthetic_causal_graph.dot")
    output_path.write_text(graph.strip() + "\n", encoding="utf-8")

    print("Synthetic causal graph definition created successfully.")
    print(f"Saved to: {output_path.resolve()}")
    print("Treatment: Discount")
    print("Outcome: Purchase")
    print("Discount is sampled independently in the generator.")
    print("This graph describes the synthetic mechanism, not real-world causality.")


if __name__ == "__main__":
    create_synthetic_causal_graph()