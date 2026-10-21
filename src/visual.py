
"""Visualisasi hasil pencarian HC, SA, dan GA."""
import math
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

def plot_sa_acceptance_probability(result, save_path):
    """Simpan grafik probabilitas penerimaan kandidat pada SA."""

    if result.get("algorithm") != "sa":
        raise ValueError("Fungsi ini hanya untuk hasil Simulated Annealing")

    probabilities = result.get("acceptance_probability_history")
    temperatures = result.get("temperature_history")
    deltas = result.get("delta_history")

    if probabilities is None or temperatures is None or deltas is None:
        raise ValueError("Data SA tidak lengkap untuk membuat grafik probabilitas")

    if not (
        len(probabilities) == len(temperatures) == len(deltas)
    ):
        raise ValueError("Panjang data probabilitas SA tidak konsisten")

    fig, ax = plt.subplots(figsize=(9, 5))

    x = list(range(len(probabilities)))
    y = [
        p if p is not None else float("nan")
        for p in probabilities
    ]

    ax.plot(x, y, label="Probabilitas penerimaan")

    ax.set_title("Probabilitas Penerimaan Kandidat - SA")
    ax.set_xlabel("Iterasi")
    ax.set_ylabel("Probabilitas")
    ax.set_ylim(0, 1.05)
    ax.set_xlim(left=0)
    ax.grid(True, alpha=0.3)
    ax.legend()

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


def plot_sa_exponential(result, save_path):
    """Plot nilai e^(delta E / T) untuk setiap neighbor valid."""

    if result.get("algorithm") != "sa":
        raise ValueError("Grafik ini hanya untuk SA")

    extra = result.get("extra") or {}

    deltas = result.get(
        "delta_history",
        extra.get("delta_history"),
    )
    temperatures = result.get(
        "temperature_history",
        extra.get("temperature_history"),
    )

    if deltas is None or temperatures is None:
        raise ValueError("Histori delta dan temperatur tidak tersedia")

    if len(deltas) != len(temperatures):
        raise ValueError("Panjang histori tidak konsisten")

    x_values = []
    y_values = []
    clipped_count = 0

    for t, (delta, temperature) in enumerate(
        zip(deltas, temperatures)
    ):
        # Neighbor invalid tidak memiliki delta E.
        if delta is None:
            continue

        if temperature <= 0:
            raise ValueError("Temperatur harus positif")

        exponent = delta / temperature

        # Hindari overflow/underflow saat menghitung exp().
        safe_exponent = max(-700, min(700, exponent))

        if safe_exponent != exponent:
            clipped_count += 1

        x_values.append(t)
        y_values.append(math.exp(safe_exponent))

    if not x_values:
        raise ValueError("Tidak ada neighbor valid untuk diplot")

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.scatter(
        x_values,
        y_values,
        s=16,
        alpha=0.75,
        label="e^(ΔE/T)",
    )

    ax.axhline(
        1.0,
        linestyle="--",
        color="gray",
        alpha=0.7,
        label="Nilai 1",
    )

    ax.set_yscale("log")
    ax.set_title("Nilai Eksponensial SA per Iterasi")
    ax.set_xlabel("Iterasi")
    ax.set_ylabel("e^(ΔE/T) - skala logaritmik")
    ax.grid(True, alpha=0.3)
    ax.legend()

    if clipped_count:
        ax.text(
            0.02,
            0.02,
            f"{clipped_count} nilai dibatasi untuk stabilitas numerik",
            transform=ax.transAxes,
            fontsize=8,
        )

    output_path = Path(save_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight",
    )
    plt.close(fig)

    return str(output_path)
