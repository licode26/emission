import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Emission Estimation & Monitoring Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background-color: #0e4d92;
        color: white;
        padding: 20px 0;
        text-align: center;
        margin-bottom: 20px;
    }
    .card {
        background-color: white;
        border-radius: 5px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .section-header {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .data-table {
        background-color: #f2f2f2;
        padding: 20px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header"><h1>Emission Estimation & Monitoring Platform</h1></div>', unsafe_allow_html=True)

# Initialize session state for storing data
if 'emission_data' not in st.session_state:
    st.session_state.emission_data = pd.DataFrame({
        'timestamp': [],
        'co2_emission': [],
        'methane_emission': [],
        'other_ghgs': [],
        'energy_intensity': []
    })

if 'is_monitoring' not in st.session_state:
    st.session_state.is_monitoring = False

# Function to create a gauge chart
def create_gauge(value, title):
    if value == -1:
        value = 0  # Default value when no data
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue" if value > 0 else "lightgray"},
            'steps': [
                {'range': [0, 33], 'color': "lightgreen"},
                {'range': [33, 66], 'color': "yellow"},
                {'range': [66, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=200, margin=dict(l=10, r=10, t=50, b=10))
    return fig

# Function to generate random emission data (for demo purposes)
def generate_random_data():
    return {
        'co2_emission': np.random.randint(10, 80),
        'methane_emission': np.random.randint(5, 60),
        'other_ghgs': np.random.randint(15, 90),
        'energy_intensity': np.random.randint(20, 85)
    }

# Function to update data periodically for monitoring
def update_monitoring_data():
    if st.session_state.is_monitoring:
        new_data = generate_random_data()
        new_row = pd.DataFrame({
            'timestamp': [datetime.now()],
            'co2_emission': [new_data['co2_emission']],
            'methane_emission': [new_data['methane_emission']],
            'other_ghgs': [new_data['other_ghgs']],
            'energy_intensity': [new_data['energy_intensity']]
        })
        st.session_state.emission_data = pd.concat([st.session_state.emission_data, new_row], ignore_index=True)
        st.session_state.current_values = new_data

# Main dashboard layout
# Display four gauge charts in a row
col1, col2, col3, col4 = st.columns(4)

# Get current values (either from monitoring or input)
current_values = st.session_state.get('current_values', {
    'co2_emission': -1,
    'methane_emission': -1,
    'other_ghgs': -1,
    'energy_intensity': -1
})

with col1:
    st.plotly_chart(create_gauge(current_values['co2_emission'], "CO2 Emission"))

with col2:
    st.plotly_chart(create_gauge(current_values['methane_emission'], "Methane Emission"))

with col3:
    st.plotly_chart(create_gauge(current_values['other_ghgs'], "Other GHGs"))

with col4:
    st.plotly_chart(create_gauge(current_values['energy_intensity'], "Energy Intensity"))

# Data Input Section
st.markdown('<div class="section-header">Provide Your Emission Data</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    co2_input = st.slider("CO2 Emission (%)", 0, 100, -1 if current_values['co2_emission'] == -1 else current_values['co2_emission'])
    methane_input = st.slider("Methane Emission (%)", 0, 100, -1 if current_values['methane_emission'] == -1 else current_values['methane_emission'])

with col2:
    other_ghgs_input = st.slider("Other GHGs (%)", 0, 100, -1 if current_values['other_ghgs'] == -1 else current_values['other_ghgs'])
    energy_intensity_input = st.slider("Energy Intensity (%)", 0, 100, -1 if current_values['energy_intensity'] == -1 else current_values['energy_intensity'])

# Buttons for actions
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    if st.button("Update Gauges", key="update_gauges"):
        st.session_state.current_values = {
            'co2_emission': co2_input,
            'methane_emission': methane_input,
            'other_ghgs': other_ghgs_input,
            'energy_intensity': energy_intensity_input
        }
        st.experimental_rerun()

with col2:
    if st.button("New Data", key="new_data"):
        new_data = generate_random_data()
        st.session_state.current_values = new_data
        st.experimental_rerun()

with col3:
    if st.button("Start", key="start_monitoring"):
        st.session_state.is_monitoring = True
        st.success("Monitoring started!")
        update_monitoring_data()
        st.experimental_rerun()

with col4:
    if st.button("Stop", key="stop_monitoring"):
        st.session_state.is_monitoring = False
        st.warning("Monitoring stopped!")

# Data Table Section
st.markdown('<div class="section-header">Emission Values (DEMO)</div>', unsafe_allow_html=True)

if not st.session_state.emission_data.empty:
    # Display the latest few entries
    display_df = st.session_state.emission_data.tail(5).copy()
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("No data recorded yet. Use the controls above to add data.")

# Historical Data Visualization
if not st.session_state.emission_data.empty and len(st.session_state.emission_data) > 1:
    st.markdown('<div class="section-header">Historical Trends</div>', unsafe_allow_html=True)
    
    # Line chart for historical data
    chart_data = st.session_state.emission_data.copy()
    chart_data = chart_data.set_index('timestamp')
    
    st.line_chart(chart_data)

# ML Model Integration (simplified for demo)
st.markdown('<div class="section-header">Emission Prediction (ML Model)</div>', unsafe_allow_html=True)

if st.button("Generate Prediction"):
    with st.spinner("Running ML model..."):
        # Simulate ML processing
        time.sleep(2)
        
        # Generate "predictions" (random for demo)
        prediction_horizon = 5
        last_date = datetime.now()
        
        if not st.session_state.emission_data.empty:
            # Use the trend from existing data to make slightly more realistic predictions
            df = st.session_state.emission_data
            trend_co2 = 0 if len(df) < 2 else (df['co2_emission'].iloc[-1] - df['co2_emission'].iloc[0]) / len(df)
            trend_methane = 0 if len(df) < 2 else (df['methane_emission'].iloc[-1] - df['methane_emission'].iloc[0]) / len(df)
            trend_other = 0 if len(df) < 2 else (df['other_ghgs'].iloc[-1] - df['other_ghgs'].iloc[0]) / len(df)
            trend_energy = 0 if len(df) < 2 else (df['energy_intensity'].iloc[-1] - df['energy_intensity'].iloc[0]) / len(df)
            
            last_values = {
                'co2_emission': df['co2_emission'].iloc[-1] if not df.empty else 50,
                'methane_emission': df['methane_emission'].iloc[-1] if not df.empty else 40,
                'other_ghgs': df['other_ghgs'].iloc[-1] if not df.empty else 30,
                'energy_intensity': df['energy_intensity'].iloc[-1] if not df.empty else 60
            }
        else:
            trend_co2, trend_methane, trend_other, trend_energy = 1, -0.5, 0.7, -0.3
            last_values = {
                'co2_emission': 50,
                'methane_emission': 40,
                'other_ghgs': 30,
                'energy_intensity': 60
            }
        
        # Generate predictions
        predictions = []
        for i in range(prediction_horizon):
            noise = np.random.normal(0, 3, 4)  # Add some noise for realism
            predictions.append({
                'predicted_date': (last_date.replace(day=last_date.day + i + 1)).strftime('%Y-%m-%d'),
                'co2_emission': max(0, min(100, last_values['co2_emission'] + trend_co2 * (i+1) + noise[0])),
                'methane_emission': max(0, min(100, last_values['methane_emission'] + trend_methane * (i+1) + noise[1])),
                'other_ghgs': max(0, min(100, last_values['other_ghgs'] + trend_other * (i+1) + noise[2])),
                'energy_intensity': max(0, min(100, last_values['energy_intensity'] + trend_energy * (i+1) + noise[3]))
            })
        
        pred_df = pd.DataFrame(predictions)
        st.success("Prediction complete!")
        st.dataframe(pred_df, use_container_width=True)
        
        # Display prediction chart
        pred_df_plot = pred_df.set_index('predicted_date')
        st.line_chart(pred_df_plot)

# Update data if monitoring is active
if st.session_state.is_monitoring:
    time.sleep(3)  # Slow down updates for demo
    update_monitoring_data()
    st.experimental_rerun()

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 40px; padding: 20px; background-color: #f2f2f2;">
    <p>© 2025 Emission Estimation & Monitoring Platform. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
