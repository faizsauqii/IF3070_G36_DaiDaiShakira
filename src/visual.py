
"""Visualisasi hasil pencarian HC, SA, dan GA."""

from pathlib import Path

import matplotlib.pyplot as plt


def plot_objective_history(result, save_path):
    """Simpan grafik objective berdasarkan hasil algoritma."""

    algorithm = result["algorithm"]
    history = result["history"]
    extra = result.get("extra") or {}

    if not history:
        raise ValueError("History objective tidak boleh kosong")

    fig, ax = plt.subplots(figsize=(9, 5))

    x = range(len(history))

    if algorithm == "ga":
        # GA: nilai maksimum dan rata-rata populasi.
        ax.plot(x, history, label="Fitness maksimum")

        history_avg = result.get(
            "history_avg",
            extra.get("history_avg"),
        )

        if history_avg is not None:
            if len(history_avg) != len(history):
                raise ValueError("Panjang history GA tidak sesuai")

            ax.plot(
                x,
                history_avg,
                label="Fitness rata-rata",
            )

    elif algorithm == "sa":
        # SA: current objective dapat naik maupun turun.
        ax.plot(x, history, label="Current objective")

        best_history = result.get(
            "best_history",
            extra.get("best_history"),
        )

        if best_history is not None:
            if len(best_history) != len(history):
                raise ValueError("Panjang best_history tidak sesuai")

            ax.plot(
                x,
                best_history,
                label="Best objective",
            )

    else:
        # HC dan variasinya.
        ax.plot(x, history, label="Objective")

    ax.set_title(
        f"Perkembangan Objective - {algorithm.upper()}"
    )
    ax.set_xlabel("Iterasi")
    ax.set_ylabel("Nilai Objective")
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Awal pencarian berada pada iterasi 0.
    ax.set_xlim(left=0)

    output_path = Path(save_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close(fig)

    return str(output_path)
