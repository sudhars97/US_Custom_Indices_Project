import os
import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==============================================================================
# 1. DATA INGESTION
# ==============================================================================
# Dynamically locate the data file based on where app.py is run
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "outputs", "indices_data", "Master_Custom_Indices.parquet")

try:
    df = pd.read_parquet(DATA_PATH)
    # Ensure Date is in datetime format
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
except FileNotFoundError:
    raise FileNotFoundError(f"Could not find data at {DATA_PATH}. Ensure the Jupyter notebook exported the data correctly.")

# Get list of all custom indices
available_indices = df.columns.tolist()

# Define default selected indices on startup
default_selection = [
    '1. Total Market (MCW)', 
    '5. The Goliath Index (Top 50 EW)', 
    '8. Ex-Tech Economy (MCW)',
    '14. Global Minimum Variance (Top 100)'
]
# Fallback just in case names changed
default_selection = [col for col in default_selection if col in available_indices]

# ==============================================================================
# 2. APP INITIALIZATION & STYLING
# ==============================================================================
app = dash.Dash(__name__, title="Quantitative Index Dashboard")

app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px', 'backgroundColor': '#f4f4f9'}, children=[
    
    # Header
    html.Div([
        html.H1("US Broad Market Custom Index Dashboard", style={'color': '#2c3e50', 'textAlign': 'center'}),
        html.P("Interactive performance comparison of Traditional, Thematic, and Smart Beta indices (Base 100).", 
               style={'textAlign': 'center', 'color': '#7f8c8d'})
    ]),
    
    # Control Panel (Dropdown)
    html.Div([
        html.Label("Select Indices to Compare:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
        dcc.Dropdown(
            id='index-selector',
            options=[{'label': col, 'value': col} for col in available_indices],
            value=default_selection,
            multi=True,
            clearable=False,
            style={'marginBottom': '20px'}
        )
    ], style={'width': '80%', 'margin': '0 auto', 'padding': '10px', 'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    
    # Chart Section
    html.Div([
        dcc.Graph(id='performance-chart', style={'height': '600px'})
    ], style={'width': '95%', 'margin': '20px auto', 'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '5px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    
    # Metrics Table Section
    html.Div([
        html.H3("Performance Metrics", style={'color': '#2c3e50'}),
        html.Div(id='metrics-table-container')
    ], style={'width': '80%', 'margin': '0 auto', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '5px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
])

# ==============================================================================
# 3. CALLBACKS (Dynamic Interaction)
# ==============================================================================
@app.callback(
    [Output('performance-chart', 'figure'),
     Output('metrics-table-container', 'children')],
    [Input('index-selector', 'value')]
)
def update_dashboard(selected_indices):
    if not selected_indices:
        return go.Figure(), html.Div("Please select at least one index.")

    # --- UPDATE CHART ---
    fig = go.Figure()
    
    for idx, col in enumerate(selected_indices):
        # Give the Total Market a distinct dashed line to act as a baseline
        line_style = dict(width=2)
        if 'Total Market' in col:
            line_style = dict(width=3, dash='dash', color='#2c3e50')
            
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=df[col], 
            mode='lines', 
            name=col,
            line=line_style,
            hovertemplate='<b>%{name}</b><br>Date: %{x}<br>Level: %{y:.2f}<extra></extra>'
        ))

    fig.update_layout(
        title={'text': "Cumulative Returns (2015-2026)", 'x': 0.5, 'xanchor': 'center'},
        yaxis_title="Index Level (Base 100)",
        xaxis_title="Date",
        hovermode="x unified", # Shows all values in a single hover box
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0', tickformat=",.0f")

    # --- UPDATE METRICS TABLE ---
    TRADING_DAYS = 252
    RISK_FREE_RATE = 0.02
    
    metrics = []
    for col in selected_indices:
        series = df[col].dropna()
        if len(series) < 2:
            continue
            
        # Calculate Returns
        ret = series.pct_change().dropna()
        years = len(ret) / TRADING_DAYS
        
        cagr = ((series.iloc[-1] / 100) ** (1 / years)) - 1
        vol = ret.std() * np.sqrt(TRADING_DAYS)
        sharpe = (cagr - RISK_FREE_RATE) / vol if vol > 0 else 0
        
        rolling_max = series.cummax()
        max_dd = ((series / rolling_max) - 1).min()
        
        metrics.append({
            'Index Strategy': col,
            'CAGR': f"{cagr:.2%}",
            'Volatility': f"{vol:.2%}",
            'Sharpe Ratio': f"{sharpe:.2f}",
            'Max Drawdown': f"{max_dd:.2%}"
        })
        
    metrics_df = pd.DataFrame(metrics)
    
    # Create an interactive Dash DataTable
    table = dash_table.DataTable(
        data=metrics_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in metrics_df.columns],
        style_header={
            'backgroundColor': '#2c3e50',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        style_cell={
            'padding': '10px',
            'fontFamily': 'Arial, sans-serif',
            'textAlign': 'center',
            'border': '1px solid #ecf0f1'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f9f9f9'
            }
        ]
    )

    return fig, table

# ==============================================================================
# 4. RUN SERVER
# ==============================================================================
if __name__ == '__main__':
    # Run the app locally on port 8050
    app.run(debug=True, port=8050)