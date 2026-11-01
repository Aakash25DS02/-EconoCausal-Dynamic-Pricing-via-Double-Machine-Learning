import numpy as np


def summarize_effects(effects):
    """Summarize estimated treatment effects from a causal ML model."""
    effects = np.asarray(effects, dtype=float).ravel()
    effects = effects[np.isfinite(effects)]

    if effects.size == 0:
        raise ValueError("No valid treatment effects to summarize.")

    print("=== Treatment Effect Summary ===")
    print(f"Valid estimates: {effects.size}")
    print(f"Mean effect:     {effects.mean():.4f}")
    print(f"Median effect:   {np.median(effects):.4f}")
    print(f"Std deviation:   {effects.std():.4f}")
    print(f"Minimum effect:  {effects.min():.4f}")
    print(f"Maximum effect:  {effects.max():.4f}")

    return {
        "count": int(effects.size),
        "mean": float(effects.mean()),
        "median": float(np.median(effects)),
        "std": float(effects.std()),
        "min": float(effects.min()),
        "max": float(effects.max()),
    }


if __name__ == "__main__":
    # Example estimates only; replace with model.effect(...) output.
    example_effects = [0.02, 0.04, -0.01, 0.03, 0.05]
    summarize_effects(example_effects)
