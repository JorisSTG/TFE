# main.py
import os
import glob
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# =====================================================
# CONFIG
# =====================================================

BASE_DIR = "."   # contient directement les dossiers 'absolue/' et 'relative/'
SEASONS = ["DJF", "MAM", "JJA", "SON"]
CMAP = "turbo"

# =====================================================
# UTILS
# =====================================================

def list_indicators(mode_dir):
    """Liste des indicateurs disponibles à partir des dossiers INDI_SAISON"""
    return sorted({d.split("_")[0] for d in os.listdir(mode_dir) if "_" in d})

def load_field(mode_dir, indicator, season, comp):
    """Charge le champ NetCDF correspondant"""
    indir = os.path.join(mode_dir, f"{indicator}_{season}")
    files = sorted(glob.glob(os.path.join(indir, f"*_{comp}_MEAN_80ANS.nc")))
    return xr.open_dataarray(files[0]) if files else None

# =====================================================
# STREAMLIT APP
# =====================================================

st.set_page_config(layout="centered")

# ==========================
# SIDEBAR
# ==========================

mode = st.sidebar.selectbox(
    "Type de données",
    ["— Sélectionner —", "absolue", "relative"]
)

if mode == "— Sélectionner —":
    st.info("Veuillez sélectionner un type de données.")
    st.stop()

mode_dir = os.path.join(BASE_DIR, mode)

indicators = ["— Sélectionner —"] + list_indicators(mode_dir)
indicator = st.sidebar.selectbox("Indicateur", indicators)

if indicator == "— Sélectionner —":
    st.stop()

if mode == "absolue":
    types = ["— Sélectionner —", "interne", "scenario", "modele", "total"]
else:
    types = ["— Sélectionner —", "interne", "scenario", "modele"]

comp = st.sidebar.selectbox("Type de variabilité", types)

if comp == "— Sélectionner —":
    st.stop()

# ==========================
# PLOT
# ==========================

fig, axes = plt.subplots(2, 2, figsize=(9, 9))
axes = axes.flatten()

data = {}
vmax = 0.0
pcm_last = None

# --- chargement et préparation des données ---
for season in SEASONS:
    da = load_field(mode_dir, indicator, season, comp)

    if da is not None:
        # Cas relatif : moyenne sur la dimension 'period'
        if "period" in da.dims:
            da = da.mean("period")

        # variance -> écart-type
        da = np.sqrt(da)

        data[season] = da
        vmax = max(vmax, float(np.nanmax(da.values)))
    else:
        data[season] = None

# --- tracé ---
for i, season in enumerate(SEASONS):
    ax = axes[i]
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(season, fontsize=14, fontweight="bold")

    da = data[season]
    if da is None:
        ax.text(
            0.5, 0.5, "Donnée manquante",
            ha="center", va="center",
            transform=ax.transAxes
        )
        continue

    pcm = ax.pcolormesh(
        da.values,
        cmap=CMAP,
        vmin=0,
        vmax=vmax,
        shading="auto"
    )
    pcm_last = pcm

# --- colorbar ---
cax = fig.add_axes([0.32, 0.06, 0.36, 0.025])
fig.colorbar(pcm_last, cax=cax, orientation="horizontal")

fig.suptitle(
    f"{indicator} – {comp} ({mode})\nÉcart‑type moyen sur 80 ans",
    fontsize=14,
    fontweight="bold"
)

plt.tight_layout(rect=[0, 0.1, 1, 0.93])
st.pyplot(fig)
