"""STALWART Dashboard application."""

from typing import Optional
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

from ..utils.logger import get_logger

logger = get_logger(__name__)


def create_dashboard():
    """Create the Streamlit dashboard."""
    st.set_page_config(
        page_title="STALWART Bridge Monitor",
        page_icon="🌉",
        layout="wide"
    )
    
    st.title("🌉 STALWART Bridge Health Monitoring System")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("Bridge Selection")
        bridge_id = st.selectbox(
            "Select Bridge",
            ["TEST-001", "BR-001 (Tacoma Narrows)", "BR-002 (Sunshine Skyway)", "BR-003 (Verrazano-Narrows)"]
        )
        
        st.header("Time Range")
        time_range = st.selectbox(
            "Select Period",
            ["Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days"]
        )
        
        st.header("Parameters")
        show_all = st.checkbox("Show All Parameters", value=True)
        
        if not show_all:
            selected_params = st.multiselect(
                "Select Parameters",
                ["AFC", "ALSA", "CPII", "FFD", "LTS", "CCF", "TVR", "BD", "SED"],
                default=["AFC", "FFD"]
            )
    
    # Main content
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Overall Health", "94.7%", "+2.3%")
    
    with col2:
        st.metric("Risk Level", "SAFE", "Stable")
    
    with col3:
        st.metric("Active Alerts", "0", "None")
    
    with col4:
        st.metric("Bridges Monitored", "47", "+2")
    
    st.markdown("---")
    
    # Parameters section
    st.header("📊 Nine Key Parameters")
    
    params = {
        "AFC (Aeroelastic Flutter)": {"value": 0.42, "threshold": 0.80, "status": "safe"},
        "ALSA (Strain Accumulation)": {"value": 0.58, "threshold": 0.75, "status": "warning"},
        "CPII (Cable Integrity)": {"value": 0.91, "threshold": 0.85, "status": "safe"},
        "FFD (Frequency Drift)": {"value": 2.3, "threshold": 5.0, "status": "safe", "unit": "%"},
        "LTS (Thermal Stress)": {"value": 18.5, "threshold": 30.0, "status": "safe", "unit": "%"},
        "CCF (Corrosion)": {"value": 34.2, "threshold": 70.0, "status": "safe", "unit": "%"},
        "TVR (Vibration)": {"value": 0.88, "threshold": 0.70, "status": "safe"},
        "BD (Displacement)": {"value": 8.4, "threshold": 15.0, "status": "safe", "unit": "mm"},
        "SED (Strain Energy)": {"value": 42.3, "threshold": 70.0, "status": "safe", "unit": "%"}
    }
    
    cols = st.columns(3)
    for i, (param_name, param_data) in enumerate(params.items()):
        with cols[i % 3]:
            value = param_data["value"]
            threshold = param_data["threshold"]
            unit = param_data.get("unit", "")
            
            # Determine color based on status
            if param_data["status"] == "critical":
                delta_color = "inverse"
            elif param_data["status"] == "warning":
                delta_color = "off"
            else:
                delta_color = "normal"
            
            st.metric(
                label=param_name,
                value=f"{value}{unit}",
                delta=f"Threshold: {threshold}{unit}",
                delta_color=delta_color
            )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Historical Trends")
        
        # Generate sample data
        dates = [datetime.now() - timedelta(hours=x) for x in range(24, 0, -1)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=[random.uniform(0.3, 0.5) for _ in range(24)],
            mode='lines+markers',
            name='AFC'
        ))
        fig.add_trace(go.Scatter(
            x=dates,
            y=[random.uniform(0.5, 0.7) for _ in range(24)],
            mode='lines+markers',
            name='ALSA'
        ))
        
        fig.update_layout(
            title="Parameter Trends (Last 24 Hours)",
            xaxis_title="Time",
            yaxis_title="Value",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⚠️ Recent Alerts")
        
        alerts_data = {
            "Time": ["14:23", "09:15", "Yesterday", "2 days ago"],
            "Parameter": ["AFC", "FFD", "ALSA", "CCF"],
            "Value": ["0.76", "3.2%", "0.71", "38.5%"],
            "Status": ["WARNING", "CAUTION", "INFO", "INFO"]
        }
        
        df_alerts = pd.DataFrame(alerts_data)
        st.dataframe(df_alerts, use_container_width=True)
        
        st.subheader("📋 Active Bridges")
        bridges_data = {
            "Bridge ID": ["BR-001", "BR-002", "BR-003", "BR-004"],
            "Location": ["Tacoma, WA", "Tampa, FL", "NYC, NY", "San Francisco, CA"],
            "Health": ["94%", "87%", "91%", "78%"],
            "Status": ["SAFE", "WARNING", "SAFE", "CAUTION"]
        }
        df_bridges = pd.DataFrame(bridges_data)
        st.dataframe(df_bridges, use_container_width=True)
    
    st.markdown("---")
    
    # Footer with research info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("📚 **Research**\n\n47 bridges • 36 months • 94.7% accuracy")
    
    with col2:
        st.success("💰 **Economic Impact**\n\n$3.4M avg savings • 2.1 year payback")
    
    with col3:
        st.warning("🔬 **Early Warning**\n\n6-18 months before visual detection")
    
    st.markdown("---")
    st.caption("STALWART v1.0.0 - Research published in Journal of Bridge Engineering (Feb 2026)")
    st.caption("DOI: 10.5281/zenodo.18655299 | Authors: Baladi, S. et al.")


def start_dashboard(host: str = "0.0.0.0", port: int = 8501, debug: bool = False):
    """Start the dashboard server."""
    logger.info(f"Starting dashboard on {host}:{port}")
    
    # This would normally run streamlit
    # For now, just a placeholder
    print("=" * 60)
    print("STALWART Dashboard")
    print("=" * 60)
    print(f"To start the dashboard, run:")
    print(f"streamlit run src/stalwart/dashboard/app.py --server.port {port}")
    print()
    print("Or install streamlit first:")
    print("pip install streamlit")
    print("=" * 60)
    
    if debug:
        print("\nPreview mode - showing dashboard structure:")
        print("-" * 40)
        create_dashboard()


if __name__ == "__main__":
    # For testing
    create_dashboard()
