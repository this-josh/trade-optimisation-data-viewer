import streamlit as st
import streamlit.components.v1 as components
from collections import namedtuple
import numpy as np
import dill as pickle

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


def run():
    models = [f.name for f in results_path.glob('*/') if f.is_dir()]
    models =['Disrupted', 'Undisrupted']
    option = st.selectbox("Select model", models)
    option = option.lower()

    st.write(f"Loading {option}")


    result= load_static(option)
    A = load_A()
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
    print(map_path)

    custom_html = load_map(map_path)
    components.html(custom_html, height=1000)
    st.plotly_chart(result.supply_fig, use_container_width=True)

    st.plotly_chart(result.S_fig, use_container_width=True)

    st.plotly_chart(result.gamma_fig, use_container_width=True)

run()