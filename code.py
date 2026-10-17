
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ==================================================
# 1. FILE PATHS
# ==================================================

INPUT_FILE = Path(__file__).parent / "SEVN_all_metallicities_combined.csv"

OUTPUT_EXCEL = Path(__file__).parent / "SEVN_Remnant_Comparison.xlsx"
OUTPUT_PLOT = Path(__file__).parent / "SEVN_Remnant_Comparison.png"

# ==================================================
# 2. LOAD CSV DATA
# ==================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nCSV file not found:\n{INPUT_FILE}\n\n"
        "Put SEVN_all_metallicities_combined.csv "
        "in the same folder as code.py."
    )

df = pd.read_csv(INPUT_FILE)

# Remove accidental spaces from column names
df.columns = df.columns.str.strip()

required_columns = [
    "M_ZAMS_Msun",
    "M_final_Msun",
    "M_CO_final_Msun",
    "M_rem_no_PSN_Msun",
    "M_rem_with_PSN_Msun",
    "Metallicity_Z",
]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    raise ValueError(
        f"Missing columns: {missing}\n"
        f"Columns in your CSV: {df.columns.tolist()}"
    )

print("\nCSV loaded successfully!")
print("Number of progenitor rows:", len(df))
print("Metallicities:", sorted(df["Metallicity_Z"].unique()))

# ==================================================
# 3. CALCULATE SUMMARY STATISTICS
# ==================================================

summary_rows = []

for metallicity, group in df.groupby("Metallicity_Z", sort=True):

    for model_name, mass_column in [
        ("Without PSN", "M_rem_no_PSN_Msun"),
        ("With PSN", "M_rem_with_PSN_Msun"),
    ]:

        masses = group[mass_column].dropna()

        # Count remnants in the selected mass intervals
        count_2_to_5 = (
            (masses >= 2.0) & (masses <= 5.0)
        ).sum()

        count_2p5_to_5 = (
            (masses >= 2.5) & (masses <= 5.0)
        ).sum()

        summary_rows.append({
            "Metallicity_Z": metallicity,
            "Model": model_name,
            "Number_of_remnants": len(masses),
            "Remnants_2_to_5_Msun": int(count_2_to_5),
            "Fraction_2_to_5_percent": (
                100 * count_2_to_5 / len(masses)
                if len(masses) else 0
            ),
            "Remnants_2p5_to_5_Msun": int(count_2p5_to_5),
            "Fraction_2p5_to_5_percent": (
                100 * count_2p5_to_5 / len(masses)
                if len(masses) else 0
            ),
            "Minimum_remnant_mass_Msun": masses.min(),
            "Maximum_remnant_mass_Msun": masses.max(),
        })

summary = pd.DataFrame(summary_rows)

print("\n========== SUMMARY TABLE ==========\n")
print(summary.round(3).to_string(index=False))

# ==================================================
# 4. SAVE RESULTS TO EXCEL
# ==================================================

with pd.ExcelWriter(OUTPUT_EXCEL, engine="openpyxl") as writer:

    summary.to_excel(
        writer,
        sheet_name="Summary",
        index=False
    )

    df.to_excel(
        writer,
        sheet_name="Original_Data",
        index=False
    )

    # Save a separate sheet for each metallicity
    for metallicity, group in df.groupby("Metallicity_Z", sort=True):

        sheet_name = f"Z_{metallicity}".replace(".", "_")

        group.to_excel(
            writer,
            sheet_name=sheet_name[:31],
            index=False
        )

print("\nExcel results saved to:")
print(OUTPUT_EXCEL.resolve())

# ==================================================
# 5. PLOT REMNANT MASS AGAINST INITIAL STELLAR MASS
# ==================================================

metallicities = sorted(df["Metallicity_Z"].unique())

fig, axes = plt.subplots(
    nrows=1,
    ncols=len(metallicities),
    figsize=(6 * len(metallicities), 5),
    sharey=True
)

# Handle a dataset with only one metallicity
if len(metallicities) == 1:
    axes = [axes]

for ax, metallicity in zip(axes, metallicities):

    group = df[df["Metallicity_Z"] == metallicity]

    ax.scatter(
        group["M_ZAMS_Msun"],
        group["M_rem_no_PSN_Msun"],
        label="Without PSN",
        marker="o",
        alpha=0.8
    )

    ax.scatter(
        group["M_ZAMS_Msun"],
        group["M_rem_with_PSN_Msun"],
        label="With PSN",
        marker="x",
        alpha=0.8
    )

    # Mark the lower-mass-gap reference interval
    ax.axhline(
        2.0,
        linestyle="--",
        linewidth=1,
        label="2 solar masses"
    )

    ax.axhline(
        2.5,
        linestyle=":",
        linewidth=1,
        label="2.5 solar masses"
    )

    ax.axhline(
        5.0,
        linestyle="--",
        linewidth=1,
        label="5 solar masses"
    )

    ax.set_title(f"Metallicity Z = {metallicity}")
    ax.set_xlabel("Initial stellar mass (solar masses)")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)

axes[0].set_ylabel("Remnant mass (solar masses)")

fig.suptitle(
    "SEVN Remnant Mass Comparison: With vs Without PSN",
    fontsize=14
)

fig.tight_layout()

fig.savefig(
    OUTPUT_PLOT,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("\nPlot saved to:")
print(OUTPUT_PLOT.resolve())

print("\n========== COMPLETE ==========")
print("Both output files have been generated.")
