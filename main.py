# main.py
import os
import glob
import xarray as xr
import numpy as np
import streamlit as st
import plotly.express as px

# =====================================================
# CONFIG
# =====================================================

BASE_DIR = "."   # contient 'absolue/' et 'relative/'
SEASONS = ["DJF", "MAM", "JJA", "SON"]

UNITS_ABS = {
    "TMm": "°C",
    "TMx": "°C",
    "PRCPTOT": "mm/an",
    "Rx1D": "mm/j",
}

COLORMAP = "turbo"

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
# UNITS
# ==========================

if mode == "relative":
    unit = "%"
else:
    unit = UNITS_ABS.get(indicator, "")

# ==========================
# DATA PREPARATION
# ==========================

data = {}
vmax = 0.0

for season in SEASONS:
    da = load_field(mode_dir, indicator, season, comp)

    if da is not None:
        if "period" in da.dims:
            da = da.mean("period")

        da = np.sqrt(da)  # variance → écart‑type

        if mode == "relative":
            da = da * 100.0

        data[season] = da
        vmax = max(vmax, float(np.nanmax(da.values)))
    else:
        data[season] = None

# ==========================
# PLOT (PLOTLY – INTERACTIF)
# ==========================

st.subheader(f"{indicator} – {comp} ({mode})")
st.caption(f"Écart‑type moyen sur 80 ans [{unit}]")

cols = st.columns(2)

for i, season in enumerate(SEASONS):
    da = data[season]

    if da is None:
        cols[i % 2].warning(f"{season} : donnée manquante")
        continue

    fig = px.imshow(
        da.values,
        origin="lower",
        color_continuous_scale=COLORMAP,
        zmin=0,
        zmax=vmax,
        labels={"color": f"{unit}"},
        title=season,
    )

    fig.update_layout(
        height=380,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    cols[i % 2].plotly_chart(fig, use_container_width=True)
