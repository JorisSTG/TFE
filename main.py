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

BASE_DIR = "."   # structure : absolue/INDI_SAISON/*.nc
SEASONS = ["DJF", "MAM", "JJA", "SON"]
CMAP = "turbo"

# =====================================================
# UTILS
# =====================================================

def get_coord(da, names):
    for n in names:
        if n in da.coords:
            return da.coords[n]
        if n in da.dims:
            return da[n]
    raise KeyError("Coordonnée spatiale introuvable")

def list_indicators(mode_dir):
    # dossiers du type INDI_SAISON
    return sorted({d.split("_")[0] for d in os.listdir(mode_dir) if "_" in d})

def load_field(mode_dir, indicator, season, comp):
    """
    Charge un fichier :
    MOYENNE/{absolue|relative}/INDI_SAISON/*_TYPE_MEAN_80ANS.nc
    """
    indir = os.path.join(mode_dir, f"{indicator}_{season}")
    files = sorted(glob.glob(os.path.join(indir, f"*_{comp}_MEAN_80ANS.nc")))
    return xr.open_dataarray(files[0]) if files else None

# =====================================================
# STREAMLIT APP
# =====================================================

st.set_page_config(layout="wide")
st.title("Variabilité climatique – moyenne sur 80 ans")

# ==========================
# SIDEBAR
# ==========================

mode = st.sidebar.selectbox(
    "Type de données",
    ["absolue", "relative"]
)

mode_dir = os.path.join(BASE_DIR, mode)

indicators = list_indicators(mode_dir)
indicator = st.sidebar.selectbox("Indicateur", indicators)

if mode == "absolue":
    types = ["interne", "scenario", "modele", "total"]
else:
    types = ["interne", "scenario", "modele"]

comp = st.sidebar.selectbox("Type de variabilité", types)

# ==========================
# PLOT
# ==========================

fig, axes = plt.subplots(2, 2, figsize=(14, 14))
axes = axes.flatten()

data = {}
vmax = 0.0
pcm_last = None

# --- chargement ---
for season in SEASONS:
    da = load_field(mode_dir, indicator, season, comp)
    data[season] = da
    if da is not None:
        vmax = max(vmax, float(np.nanmax(da.values)))

# --- affichage ---
for i, season in enumerate(SEASONS):
    ax = axes[i]
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(season, fontsize=16, fontweight="bold")

    da = data[season]
    if da is None:
        ax.text(0.5, 0.5, "Donnée manquante",
                ha="center", va="center", transform=ax.transAxes)
        continue

    lon = get_coord(da, ["lon", "x"])
    lat = get_coord(da, ["lat", "y"])

    pcm = ax.pcolormesh(
        lon, lat, da,
        cmap=CMAP,
        vmin=0,
        vmax=vmax,
        shading="auto"
    )
    pcm_last = pcm

# --- colorbar sous la grille ---
cax = fig.add_axes([0.25, 0.06, 0.5, 0.025])
fig.colorbar(pcm_last, cax=cax, orientation="horizontal")

fig.suptitle(
    f"{indicator} – {comp} ({mode})\nMoyenne sur 80 ans",
    fontsize=18,
    fontweight="bold"
)

plt.tight_layout(rect=[0, 0.1, 1, 0.93])
st.pyplot(fig)
