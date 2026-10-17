
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# 1. FILE PATHS
# ============================================================

FOLDER = Path(__file__).parent

INPUT_FILE = FOLDER / "SEVN_all_metallicities_combined.csv"
OUTPUT_FILE = FOLDER / "Fryer_Rapid_Delayed_Results.xlsx"
PLOT_FILE = FOLDER / "Fryer_Rapid_Delayed_Plots.png"

# ============================================================
# 2. LOAD PROGENITOR DATA
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Cannot find input CSV:\n{INPUT_FILE}"
    )

df = pd.read_csv(INPUT_FILE)
df.columns = df.columns.str.strip()

required = [
    "M_ZAMS_Msun",
    "M_final_Msun",
    "M_CO_final_Msun",
    "Metallicity_Z",
]

missing = [col for col in required if col not in df.columns]

if missing:
    raise ValueError(
        f"Missing columns: {missing}\n"
        f"Available columns: {df.columns.tolist()}"
    )

# Convert required columns to numeric values
for col in required:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=required).copy()

if (df["M_final_Msun"] <= 0).any():
    raise ValueError("Final stellar masses must be positive.")

print("CSV loaded successfully.")
print("Progenitors:", len(df))
print("Metallicities:", sorted(df["Metallicity_Z"].unique()))

# ============================================================
# 3. RAPID SUPERNOVA PRESCRIPTION
# Fryer et al. (2012)
# ============================================================

def rapid_model(m_co, m_final):

    # Proto-remnant mass, in solar masses
    m_proto = 1.0

    remaining_mass = m_final - m_proto

    if remaining_mass <= 0:
        raise ValueError("Invalid mass for rapid prescription.")

    # Calculate fallback mass
    if m_co < 2.5:
        m_fb = 0.2

    elif m_co < 6.0:
        m_fb = 0.286 * m_co - 0.514

    elif m_co < 7.0:
        # Complete fallback
        m_fb = remaining_mass

    elif m_co < 11.0:
        alpha = 0.25 - 1.275 / remaining_mass
        beta = 1.0 - 11.0 * alpha

        fallback_fraction = alpha * m_co + beta
        m_fb = fallback_fraction * remaining_mass

    else:
        # Complete fallback
        m_fb = remaining_mass

    # Total baryonic remnant mass
    m_baryonic = m_proto + m_fb

    return m_proto, m_fb, m_baryonic


# ============================================================
# 4. DELAYED SUPERNOVA PRESCRIPTION
# Fryer et al. (2012)
# ============================================================

def delayed_model(m_co, m_final):

    # Proto-remnant mass
    if m_co < 3.5:
        m_proto = 1.2

    elif m_co < 6.0:
        m_proto = 1.3

    elif m_co < 11.0:
        m_proto = 1.4

    else:
        m_proto = 1.6

    remaining_mass = m_final - m_proto

    if remaining_mass <= 0:
        raise ValueError("Invalid mass for delayed prescription.")

    # Calculate fallback mass
    if m_co < 2.5:
        m_fb = 0.2

    elif m_co < 3.5:
        m_fb = 0.5 * m_co - 1.05

    elif m_co < 11.0:
        alpha = 0.133 - 0.093 / remaining_mass
        beta = 1.0 - 11.0 * alpha

        fallback_fraction = alpha * m_co + beta
        m_fb = fallback_fraction * remaining_mass

    else:
        # Complete fallback
        m_fb = remaining_mass

    # Total baryonic remnant mass
    m_baryonic = m_proto + m_fb

    return m_proto, m_fb, m_baryonic


# ============================================================
# 5. CONVERT BARYONIC MASS TO GRAVITATIONAL MASS
# ============================================================

def gravitational_mass(m_baryonic):
    """
    Working classification convention:
      baryonic mass < 2.5 Msun -> NS conversion
      baryonic mass >= 2.5 Msun -> BH conversion

    Verify the NS/BH boundary against the specific
    implementation you intend to reproduce before
    interpreting BH population counts.
    """

    if m_baryonic < 2.5:
        m_grav = (
            np.sqrt(1.0 + 0.3 * m_baryonic) - 1.0
        ) / 0.15

        remnant_type = "NS"

    else:
        m_grav = 0.9 * m_baryonic
        remnant_type = "BH"

    return m_grav, remnant_type


# ============================================================
# 6. APPLY BOTH MODELS TO EVERY PROGENITOR
# ============================================================

rapid_proto = []
rapid_fallback = []
rapid_baryonic = []
rapid_grav = []
rapid_type = []

delayed_proto = []
delayed_fallback = []
delayed_baryonic = []
delayed_grav = []
delayed_type = []

for _, row in df.iterrows():

    m_co = row["M_CO_final_Msun"]
    m_final = row["M_final_Msun"]

    # Rapid model
    rp, rf, rb = rapid_model(m_co, m_final)
    rg, rt = gravitational_mass(rb)

    rapid_proto.append(rp)
    rapid_fallback.append(rf)
    rapid_baryonic.append(rb)
    rapid_grav.append(rg)
    rapid_type.append(rt)

    # Delayed model, using exactly the same progenitor
    dp, dfb, db = delayed_model(m_co, m_final)
    dg, dt = gravitational_mass(db)

    delayed_proto.append(dp)
    delayed_fallback.append(dfb)
    delayed_baryonic.append(db)
    delayed_grav.append(dg)
    delayed_type.append(dt)

df["Rapid_Mproto_Msun"] = rapid_proto
df["Rapid_Mfallback_Msun"] = rapid_fallback
df["Rapid_Mbaryonic_Msun"] = rapid_baryonic
df["Rapid_remnant_Msun"] = rapid_grav
df["Rapid_type"] = rapid_type

df["Delayed_Mproto_Msun"] = delayed_proto
df["Delayed_Mfallback_Msun"] = delayed_fallback
df["Delayed_Mbaryonic_Msun"] = delayed_baryonic
df["Delayed_remnant_Msun"] = delayed_grav
df["Delayed_type"] = delayed_type

df["Mass_difference_Delayed_minus_Rapid_Msun"] = (
    df["Delayed_remnant_Msun"] - df["Rapid_remnant_Msun"]
)

# ============================================================
# 7. SUMMARISE BLACK HOLES BY METALLICITY
# ============================================================

summary_rows = []

for metallicity, group in df.groupby("Metallicity_Z", sort=True):

    for model in ["Rapid", "Delayed"]:

        mass_col = f"{model}_remnant_Msun"
        type_col = f"{model}_type"

        is_bh = group[type_col].eq("BH")
        bh_masses = group.loc[is_bh, mass_col].dropna()

        n_bh = len(bh_masses)

        count_2_5 = (
            (bh_masses >= 2.0) & (bh_masses <= 5.0)
        ).sum()

        count_2p5_5 = (
            (bh_masses >= 2.5) & (bh_masses <= 5.0)
        ).sum()

        summary_rows.append({
            "Metallicity_Z": metallicity,
            "Model": model,
            "Progenitors": len(group),
            "Black_holes": n_bh,
            "Neutron_stars": int((~is_bh).sum()),
            "BHs_2_to_5_Msun": int(count_2_5),
            "BH_fraction_2_to_5_percent": (
                100 * count_2_5 / n_bh if n_bh else np.nan
            ),
            "BHs_2p5_to_5_Msun": int(count_2p5_5),
            "BH_fraction_2p5_to_5_percent": (
                100 * count_2p5_5 / n_bh if n_bh else np.nan
            ),
            "Minimum_BH_mass_Msun": (
                bh_masses.min() if n_bh else np.nan
            ),
        })

summary = pd.DataFrame(summary_rows)

print("\n========== RAPID VS DELAYED SUMMARY ==========")
print(summary.round(4).to_string(index=False))

# ============================================================
# 8. EXPORT EXCEL RESULTS
# ============================================================

with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:

    summary.to_excel(
        writer, sheet_name="Summary", index=False
    )

    df.to_excel(
        writer, sheet_name="All_Progenitors", index=False
    )

    for metallicity, group in df.groupby("Metallicity_Z", sort=True):

        sheet_name = f"Z_{metallicity}".replace(".", "_")[:31]

        group.to_excel(
            writer, sheet_name=sheet_name, index=False
        )

print("\nExcel results saved to:")
print(OUTPUT_FILE.resolve())

# ============================================================
# 9. PLOT RAPID VS DELAYED
# ============================================================

metallicities = sorted(df["Metallicity_Z"].unique())

fig, axes = plt.subplots(
    1,
    len(metallicities),
    figsize=(6 * len(metallicities), 5),
    sharey=True,
    squeeze=False,
)

for ax, metallicity in zip(axes[0], metallicities):

    group = df[df["Metallicity_Z"] == metallicity]

    ax.scatter(
        group["M_ZAMS_Msun"],
        group["Rapid_remnant_Msun"],
        marker="o",
        label="Rapid",
        alpha=0.8,
    )

    ax.scatter(
        group["M_ZAMS_Msun"],
        group["Delayed_remnant_Msun"],
        marker="x",
        label="Delayed",
        alpha=0.8,
    )

    ax.axhline(2.0, linestyle="--", linewidth=1)
    ax.axhline(2.5, linestyle=":", linewidth=1)
    ax.axhline(5.0, linestyle="--", linewidth=1)

    ax.set_title(f"Metallicity Z = {metallicity}")
    ax.set_xlabel("Initial stellar mass (solar masses)")
    ax.grid(True, alpha=0.25)
    ax.legend()

axes[0, 0].set_ylabel("Gravitational remnant mass (solar masses)")

fig.suptitle(
    "Fryer Rapid vs Delayed Supernova Prescriptions",
    fontsize=14,
)

fig.tight_layout()
fig.savefig(PLOT_FILE, dpi=300, bbox_inches="tight")
plt.show()

print("\nPlot saved to:")
print(PLOT_FILE.resolve())

print("\nCalculation complete.")
