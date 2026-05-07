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

BASE_DIR = "."   # contient absolue/ et relative/
SEASONS = ["DJF", "MAM", "JJA", "SON"]
CMAP = "turbo"

# =====================================================
# UTILS
# =====================================================

def list_indicators(mode_dir):
    return sorted({d.split("_")[0] for d in os.listdir(mode_dir) if "_" in d})

def load_field(mode_dir, indicator, season, comp):
    indir = os.path.join(mode_dir, f"{indicator}_{season}")
    files = sorted(glob.glob(os.path.join(indir, f"*_{comp}_MEAN_80ANS.nc")))
    return xr.open_dataarray(files[0]) if files else None

# =====================================================
# STREAMLIT APP
# =====================================================

st.set_page_config(layout="wide")
st.title("Variabilité climatique – écart‑type moyen (80 ans)")

# ==========================
# SIDEBAR
# ==========================

mode = st.sidebar.selectbox(
    "Type de données",
    ["— Sélectionner —", "absolue", "relative"]
)

if mode == "— Sélectionner —":
    st.info("Sélectionnez un type de données pour commencer.")
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

fig, axes = plt.subplots(2, 2, figsize=(8, 8))
axes = axes.flatten()

data = {}
vmax = 0.0
pcm_last = None

# --- chargement ---
for season in SEASONS:
    da = load_field(mode_dir, indicator, season, comp)
    if da is not None:
        da = np.sqrt(da)  # ✅ passage VAR → ET
        data[season] = da
        vmax = max(vmax, float(np.nanmax(da.values)))
    else:
        data[season] = None

# --- affichage ---
for i, season in enumerate(SEASONS):
    ax = axes[i]
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(season, fontsize=18, fontweight="bold")

    da = data[season]
    if da is None:
        ax.text(0.5, 0.5, "Donnée manquante",
                ha="center", va="center",
                transform=ax.transAxes)
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
cax = fig.add_axes([0.3, 0.05, 0.4, 0.025])
fig.colorbar(pcm_last, cax=cax, orientation="horizontal")

fig.suptitle(
    f"{indicator} – {comp} ({mode})\nÉcart‑type moyen sur 80 ans",
    fontsize=20,
    fontweight="bold"
)

plt.tight_layout(rect=[0, 0.09, 1, 0.92])
st.pyplot(fig)
