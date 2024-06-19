import streamlit as st
import streamlit.components.v1 as components
from collections import namedtuple
import numpy as np
import dill as pickle
from datetime import datetime

st.set_page_config(layout="wide")

from pathlib import Path
results_path = Path('./results/')

def load_map(map_path):
    custom_html = """
    <style>
    #spinner {{
        z-index: 99999;
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.8);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}
    </style>

    <div id="spinner">
        <h2>Loading Interactive Map...</h2>
        <img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExYjA0NGFrZ2h4MWQwaHk0c2I5MXdwajBybWV0aG5qb2ppbmtxenc0OSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/VI2UC13hwWin1MIfmi/giphy.webp" alt="Loading Interactive Map..." />
    </div>

    <iframe id="documentIFrame" onload="closeIndicator()" src="{map_path}" style="width: 100%; height: 1000px; border: none;">
    </iframe>

    <script type="text/javascript">
    function closeIndicator() {{
        var s = document.getElementById('spinner');
        console.log(s);
        s.style.display = "none";
    }}
    </script>
    """.format(map_path=map_path)  # Replace with your actual map_path
    return custom_html

@st.cache_resource
def load_static(option):
    with open(results_path/option/'static.pkl', 'rb') as f:
        r = pickle.load(f)

    Result = namedtuple('Result', r.keys())
    result = Result(**r)
    return result

@st.cache_resource
def load_A():
    return np.load("A.npy")

def sidebar():
    st.markdown(f"""
This work in progress app aids viewing the highly dimensional trade optimisation results

## How this figure works

- You can select a node to get a detailed view
- Links close to full utilisation are more transparent
- :blue[Blue] shows more trade going from west to east
- :orange[Orange] shows trade going from east to west
- Circle colours are defined by the summed link utilisation

## Node plot key
| Name     | Description                    |
|----------|--------------------------------|
| C        | Consumption                    |
| ExCap    | Export Capacity                |
| ImCap    | Import Capacity                |
| P        | Domestic Production            |
| S        | Stockpile                      |
| TotEx    | Total Monthly Exports          |
| TotIm    | Total Monthly Imports          |
| taun     | Amount withdraw from stockpile |
| taup     | Amount deposited to stockpile  |
| $\gamma$ | Supply deficit                 |
                """                
                )





def run():
    st.title("Trade Optimisation Data Viewer")
    st.logo("https://github.com/tsl-imperial/assets/blob/main/tsl-logo-dark.png?raw=true")
    cols = st.columns(spec=[0.2,0.8])
    cols[0].write("Select whether you'd like to include the disruption")
    option = cols[0].toggle("Disrupted", value=True)
    option = 'disrupted' if option else 'undisrupted'



    result= load_static(option)
    periods = result.periods

    period_str =  [date.strftime("%b %Y") for date in periods]
    cols[1].write("Select the month you'd like to view, this only affects the node and line colours")
    period = cols[1].select_slider("Period",period_str, value=period_str[10])
    period_idx = period_str.index(period)
    A = load_A()
    with st.sidebar:
        sidebar()
    col1, col2,col3 = st.columns(3)
    col1.metric("Total deficit", f"{np.sum(result.gamma):.0f}m³")
    col2.metric("Total trade", f"{np.sum(result.Q):.2e}m³")
    col3.metric(r"$m^3 \times$ meters travelled", f"{np.sum(np.abs(A) @ np.abs(result.Q)) :.2e}m³")
    # col4.metric("Solve time", f"{result.solve_time:.2f}s")
    period_s3 =str(periods[period_idx]).split(' ')[0]
    map_path =fr'https://trade-optimisation-data-viewer.s3.eu-west-2.amazonaws.com/results/{option.lower()}/{period_s3}+00%3A00%3A00.html'
    print(map_path)

    custom_html = load_map(map_path)
    components.html(custom_html, height=1000)
    # st.plotly_chart(result.supply_fig, use_container_width=True)

    st.plotly_chart(result.S_fig, use_container_width=True)

    st.plotly_chart(result.gamma_fig, use_container_width=True)



run()