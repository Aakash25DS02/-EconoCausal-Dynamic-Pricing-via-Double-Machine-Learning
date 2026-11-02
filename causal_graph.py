
from pathlib import Path


def create_causal_graph():
    """Create a conceptual causal DAG for the EconoCausal project."""

    graph = r"""
digraph EconoCausal {
    rankdir=LR;
    node [shape=box, style="rounded,filled", fontname="Arial"];

    Price [fillcolor="lightblue"];
    CompetitorPrice [label="Competitor Price", fillcolor="lightblue"];
    Promotion [fillcolor="lightblue"];
    Season [fillcolor="lightblue"];
    Discount [fillcolor="gold"];
    Purchase [fillcolor="lightgreen"];

    Price -> Discount;
    Price -> Purchase;
    CompetitorPrice -> Discount;
    CompetitorPrice -> Purchase;
    Promotion -> Discount;
    Promotion -> Purchase;
    Season -> Discount;
    Season -> Purchase;
    Discount -> Purchase;
}
"""
    output_path = Path("causal_graph.dot")
    output_path.write_text(graph.strip() + "\n", encoding="utf-8")

    print("Causal graph definition created successfully.")
    print(f"Saved to: {output_path.resolve()}")
    print("Treatment: Discount")
    print("Outcome: Purchase")
    print("Potential confounders: Price, Competitor Price, Promotion, Season")


if __name__ == "__main__":
    create_causal_graph()
