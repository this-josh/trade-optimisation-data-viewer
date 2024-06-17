import streamlit as st
import streamlit.components.v1 as components
from collections import namedtuple
import numpy as np
import dill as pickle

st.set_page_config(layout="wide")

from pathlib import Path
results_path = Path('./results/')

def run():
    models = [f.name for f in results_path.glob('*/') if f.is_dir()]
    models =['Disrupted', 'Undisrupted']
    option = st.selectbox("Select model", models)
    option = option.lower()

    st.write(f"Loading {option}")

    with open(results_path/option/'static.pkl', 'rb') as f:
        r = pickle.load(f)

    Result = namedtuple('Result', r.keys())
    result = Result(**r)


    A = np.load("A.npy")
    periods = result.periods

    with st.form("Optional"):
        period = st.select_slider("Period",periods, value=periods[10])
        _ = st.form_submit_button("Submit")

    st.title(period)

    st.markdown(f"""
    Links closer to 100% utilisations are more transparent.
    Blue shows more trade going from west to east
    Orange shows trade going from east to west
    Circle colours are defined by the summed link utilisation 
    """)


    col1, col2,col3,col4 = st.columns(4)
    col1.metric("Total deficit", f"{np.sum(result.gamma):.0f}m³")
    col2.metric("Total trade", f"{np.sum(result.Q):.2e}m³")
    col3.metric("AQ", f"{np.sum(np.abs(A) @ np.abs(result.Q)) :.2e}m³")
    col4.metric("Solve time", f"{result.solve_time:.2f}s")
    period_s3 =str(period).split(' ')[0]
    map_path =fr'https://trade-optimisation-data-viewer.s3.eu-west-2.amazonaws.com/results/{option.lower()}/html/{period_s3}+00%3A00%3A00.html'

    st.components.v1.iframe(map_path, scrolling=False, height=1000)
    st.plotly_chart(result.supply_fig, use_container_width=True)

    st.plotly_chart(result.S_fig, use_container_width=True)

    st.plotly_chart(result.gamma_fig, use_container_width=True)

run()