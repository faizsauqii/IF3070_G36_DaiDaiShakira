
"""Visualisasi hasil pencarian HC, SA, dan GA."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from src.constraints import is_valid, total_weight
from src.objective import objective, total_fee

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

def plot_deck_state(state, save_path, title="Susunan Kendaraan"):
    """Gambar posisi kendaraan pada setiap geladak kapal."""

    if not is_valid(state):
        raise ValueError("State tidak valid untuk divisualisasikan")

    ships = state.problem.ships

    fig, axes = plt.subplots(
        len(ships),
        2,
        figsize=(12, max(4.5, 4.5 * len(ships))),
        squeeze=False,
        gridspec_kw={"width_ratios": [4, 1.5]},
    )

    palette = plt.get_cmap("tab20")

    outside = [
        vehicle.id
        for i, vehicle in enumerate(state.problem.vehicles)
        if state.positions[i] is None
    ]

    for ship_index, ship in enumerate(ships):
        ax, info_ax = axes[ship_index]

        # Koordinat (0, 0) berada di kiri atas.
        ax.set_xlim(0, ship.l)
        ax.set_ylim(ship.w, 0)
        ax.set_aspect("equal")

        ax.set_xticks(range(ship.l + 1))
        ax.set_yticks(range(ship.w + 1))
        ax.grid(True, alpha=0.25)

        ax.set_xlabel("x - panjang geladak")
        ax.set_ylabel("y - lebar geladak")
        ax.set_title(
            f"Kapal {ship_index + 1} ({ship.l} x {ship.w})"
        )

        for i, vehicle in enumerate(state.problem.vehicles):
            position = state.positions[i]

            if position is None or position[0] != ship_index:
                continue

            cells = state.cells(i)
            xs, ys = zip(*cells)

            x0, y0 = min(xs), min(ys)
            width = max(xs) - x0 + 1
            height = max(ys) - y0 + 1

            ax.add_patch(
                Rectangle(
                    (x0, y0),
                    width,
                    height,
                    facecolor=palette(i % 20),
                    edgecolor="black",
                    linewidth=1.2,
                    alpha=0.75,
                    zorder=2,
                )
            )

            ax.text(
                x0 + width / 2,
                y0 + height / 2,
                vehicle.id,
                ha="center",
                va="center",
                fontsize=9,
                zorder=3,
                bbox={
                    "facecolor": "white",
                    "alpha": 0.8,
                    "edgecolor": "none",
                    "pad": 1,
                },
            )

        # Panel informasi di sebelah kanan geladak.
        info_ax.axis("off")

        vehicle_count = sum(
            pos is not None and pos[0] == ship_index
            for pos in state.positions
        )

        info = (
            f"Berat: {total_weight(state, ship_index)} "
            f"/ {ship.max_capacity}\n"
            f"Kendaraan di kapal: {vehicle_count}"
        )

        if ship_index == 0:
            info += "\n\nDi luar kapal:\n"
            info += ", ".join(outside) or "Tidak ada"

        info_ax.text(
            0,
            0.95,
            info,
            va="top",
            ha="left",
            transform=info_ax.transAxes,
        )

    fig.suptitle(
        f"{title} | ShippingFee: {total_fee(state)} "
        f"| Objective: {objective(state):.3f}"
    )

    fig.tight_layout(rect=(0, 0, 1, 0.95))

    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return str(path)
