# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: comm
#     language: python
#     name: comm
# ---

# %% [markdown]
# # Browse and analyse traced ignitions
# **Notebook Purpose:**
#
# -
# -
#
# **Created by:** Krystian Safjan
#
#
# **Changes:**
#
# - 2022-04-16: KS: Initial implementation

# %%
# %load_ext autoreload

# %%
# add parent dir to python path
import sys

sys.path.insert(0, "..")

# %%
# %autoreload
# Add parent directory to path
from pathlib import Path
import plotly.graph_objects as go
import os
from binance_pump.traces import Traces

# %%
traces_dir = Path("../traces")

# %%
# !ls -lh $traces_dir

# %%
ret = [r for r in os.listdir(traces_dir) if "retired_trace" in r]
ret

# %%
FILE = ret[0]

# %%
# convert traces to models

# %%
trc = Traces(traces_dir=traces_dir)
trc.get_events(FILE)
print(len(trc.traces))
trc.remove_short_events(min_length=3)
print(len(trc.traces))
# %% [markdown]
# # Investigate traces shorter than N ticks

# %%
n_ticks = [len(t.price_history) for t in trc.traces]
fig = go.Figure(data=[go.Histogram(x=n_ticks)])
fig.show()

# %%
short_traces = [t for t in trc.traces if len(t.price_history) < 5]
long_traces = [t for t in trc.traces if len(t.price_history) >= 5]

# %%
len(short_traces)

# %%
import plotly.graph_objects as go
import numpy as np

max_price_short = np.log([t.max_total_price_change_prc for t in short_traces])
max_price_long = np.log([t.max_total_price_change_prc for t in long_traces])

fig = go.Figure()
fig.add_trace(go.Histogram(x=max_price_short, name="shorts"))
fig.add_trace(go.Histogram(x=max_price_long, name="longs"))

# Overlay both histograms
fig.update_layout(barmode="overlay")
# Reduce opacity to see both histograms
fig.update_traces(opacity=0.75)
fig.show()

# %%
trc.sort_events_by_length()

# %%
trc.traces[0].length


# %%
# Create traces
def display_func(line_id):
    fig = go.Figure()
    p = trc.traces[line_id].price_history
    ts=trc.traces[line_id].timestamps

    fig.add_trace(go.Scatter(x=ts[1:], y=p[1:], mode="lines+markers", name="lines"))
    fig.show()


from ipywidgets import interact
import ipywidgets as widgets

# or interact_manual - do not compute for states during the slider move
interact(
    display_func,
    line_id=widgets.IntSlider(min=0, max=len(trc.traces) - 1, step=1, value=0),
)

# %%

# %%

# %%
trc.traces[11].price_history

# %%
