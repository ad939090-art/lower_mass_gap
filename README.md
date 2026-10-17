# Theoretical Remnant-Mass Predictions

## Project Overview

This project investigates whether stellar-collapse models predict a deficit of black holes in the proposed lower black-hole mass gap, taken here as **2.5–5 \(M_\odot\)**.

The analysis compares rapid and delayed supernova remnant-mass prescriptions and examines how the predicted remnant masses vary with progenitor properties and metallicity. It also compares these calculations with remnant-mass data from SEVN models.

The results are used to investigate model dependence, not to establish that black holes in this mass interval are physically impossible.

## Research Objectives

- Calculate compact-object remnant masses using rapid and delayed supernova prescriptions.
- Classify predicted remnants as neutron stars or black holes according to the threshold implemented in the calculation.
- Count predicted black holes within the 2.5–5 \(M_\odot\) interval.
- Compare predictions across three metallicities.
- Examine SEVN remnant masses with and without pair-instability supernova effects.
- Assess how the choice of remnant-formation prescription affects the predicted lower mass gap.

## Dataset

The analysis uses a combined SEVN progenitor dataset containing 180 stellar models across three metallicities:

| Metallicity, \(Z\) | Number of models |
|---:|---:|
| 0.02 | 60 |
| 0.002 | 60 |
| 0.0002 | 60 |
| **Total** | **180** |

The dataset contains progenitor properties and remnant-mass estimates, including initial mass, final mass, helium-core mass, carbon–oxygen core mass, and remnant masses under different pair-instability assumptions.

**Original data source:** Spera, Mapelli & Bressan (2017), *MNRAS*, 470, 4739–4753.

https://doi.org/10.1093/mnras/stx1576

The SEVN dataset and the rapid/delayed prescription calculations serve different purposes and should not be treated as interchangeable predictions.

## Methodology

### 1. Rapid and delayed prescriptions

Remnant masses are calculated using the rapid and delayed supernova prescriptions described by Fryer et al. (2012). The prescriptions use progenitor properties, including final stellar mass and carbon–oxygen core mass, to estimate proto-compact-object mass and fallback.

The implementation includes:

- Proto-compact-object mass assignments.
- Fallback prescriptions and fallback fractions.
- Baryonic remnant-mass calculation.
- Conversion from baryonic to gravitational remnant mass.
- Classification and counting of remnants in the selected mass interval.

The equations and parameter choices used in the implementation should be documented in the accompanying report and checked against the original source.

### 2. Lower mass-gap interval

For this project, the interval is defined operationally as

\[
2.5\,M_\odot \leq M_{\rm rem} \leq 5\,M_\odot.
\]

The script must apply this interval consistently to the remnant mass quantity specified in the analysis. The classification threshold used to distinguish neutron stars from black holes is a modelling convention and should not be interpreted as a universal physical boundary.

### 3. Metallicity comparison

The predictions are evaluated separately for \(Z=0.02\), \(Z=0.002\), and \(Z=0.0002\). Metallicity affects the calculations through the stellar properties supplied to the remnant-mass prescriptions; it does not appear explicitly in every fallback equation.

### 4. SEVN comparison

The SEVN remnant-mass estimates are examined separately, including cases with and without pair-instability supernova effects. Pair-instability processes primarily affect more massive stellar remnants and are not, by themselves, a direct explanation of the proposed lower mass gap.

## Repository Contents

The repository should contain the files required to reproduce the analysis. Update the filenames below to match the actual files committed to the repository.

| File or directory | Purpose |
|---|---|
| `remnant_mass_calculations.py` | Implements the rapid and delayed prescriptions and produces remnant-mass counts. |
| `SEVN_all_metallicities_combined.csv` | Combined SEVN progenitor dataset, if redistribution is permitted. |
| `figures/` | Generated figures used in the report. |
| `README.md` | Project description, data source, and reproduction instructions. |

## Reproducing the Analysis

1. Download or clone this repository.
2. Install the Python libraries required by the calculation script.
3. Ensure the input dataset is available at the path expected by the script.
4. Run the calculation script.
5. Check the printed or saved output for neutron-star counts, black-hole counts, and black holes in the 2.5–5 \(M_\odot\) interval for each prescription and metallicity.
6. Run the plotting code and compare the generated figures with Figures 3.1 and 3.2 in the report.

The exact commands and dependencies should be added once the final script and environment have been verified.

## Main Outputs

The analysis is intended to produce:

- Remnant-mass predictions for the rapid and delayed prescriptions.
- Neutron-star and black-hole counts by metallicity.
- Counts of black holes in the 2.5–5 \(M_\odot\) interval.
- Figure 3.1: remnant mass versus zero-age main-sequence mass for the two prescriptions and different metallicities.
- Figure 3.2: comparison of SEVN remnant masses with and without pair-instability supernova effects.

Numerical results should be reported only after the calculation script has been executed and its outputs checked. In particular, the reported absence of rapid-model black holes and the reported delayed-model count in the interval must be verified against the final code and input data.

## Limitations

- The 180 progenitor models do not necessarily represent a realistic population distribution of stars.
- Predictions depend on the adopted explosion, fallback, and mass-conversion prescriptions.
- The calculation does not, by itself, account for all effects of binary evolution or observational selection.
- A predicted deficit in a particular model does not establish that black holes in the interval are physically forbidden.
- Observational candidates require careful consideration of mass uncertainties and object classification.

## References

**Fryer, C. L., et al. (2012).** *Compact Remnant Mass Function: Dependence on the Explosion Mechanism and Metallicity.* The Astrophysical Journal, 749, 91.

https://doi.org/10.1088/0004-637X/749/1/91

**Spera, M., Mapelli, M., & Bressan, A. (2017).** *The mass spectrum of compact remnants from the PARSEC stellar evolution tracks.* Monthly Notices of the Royal Astronomical Society, 470, 4739–4753.

https://doi.org/10.1093/mnras/stx1576

## Code and Data Availability

This repository supports the calculations and figures associated with the project's theoretical remnant-mass analysis. The report provides the scientific discussion, equations, results, and interpretation; this repository provides the supporting computational materials.

