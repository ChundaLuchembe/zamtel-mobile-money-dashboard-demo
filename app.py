import os
import pandas as pd
import numpy as np
from datetime import datetime, time
import warnings
import hashlib

# Suppress warnings
warnings.filterwarnings('ignore')

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px

# Configure pandas to avoid threading issues
pd.set_option('mode.chained_assignment', None)

# -----------------------
# Authentication Config
# -----------------------
USERNAME = "admin"
PASSWORD = "admin123"

# Simple session storage (in production, use flask-login or dash-auth)
logged_in = False

# -----------------------
# Config
# -----------------------
CSV_PATH = "zamtel_mobile_money_200.csv"

# -----------------------
# Data loading and prep
# -----------------------
def load_data():
    df = pd.read_csv(CSV_PATH)
    # Combine Date and Time to a single datetime
    df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    # Normalize types
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    # Useful derived fields
    df["Hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
    df["SuccessFlag"] = (df["Status"].str.lower() == "success").astype(int)
    return df

df = load_data()
print("\n" + "="*60)
print("✅ DATA LOADED SUCCESSFULLY")
print(f"📊 Total rows: {len(df)}")
print(f"📅 Date range: {df['Date'].min()} to {df['Date'].max()}")
print(f"💰 Total amount: ZMW {df['Amount'].sum():,.2f}")
print("="*60 + "\n")

# -----------------------
# App init
# -----------------------
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Zamtel Mobile Money Analytics"
server = app.server  # for deployment

# -----------------------
# Controls
# -----------------------
def get_login_page():
    return html.Div([
        html.Div([
            # Logo/Icon
            html.Div([
                html.I(className="fas fa-shield-alt", style={
                    "fontSize": "80px",
                    "color": "#28a745",
                    "marginBottom": "20px"
                }),
            ], style={"textAlign": "center"}),
            
            # Title
            html.H2("ZAMTEL ANALYTICS", style={
                "textAlign": "center",
                "color": "#2c3e50",
                "marginBottom": "10px",
                "fontWeight": "bold",
                "letterSpacing": "2px"
            }),
            html.P("Mobile Money Dashboard", style={
                "textAlign": "center",
                "color": "#6c757d",
                "marginBottom": "40px",
                "fontSize": "14px"
            }),
            
            # Login Form
            html.Div([
                # Username
                html.Div([
                    html.Label([
                        html.I(className="fas fa-user", style={"marginRight": "8px"}),
                        "Username"
                    ], style={
                        "fontWeight": "600",
                        "color": "#495057",
                        "marginBottom": "8px",
                        "display": "block"
                    }),
                    dcc.Input(
                        id="username-input",
                        type="text",
                        placeholder="Enter username",
                        style={
                            "width": "100%",
                            "padding": "12px 15px",
                            "border": "1px solid #ced4da",
                            "borderRadius": "6px",
                            "fontSize": "14px",
                            "marginBottom": "20px",
                            "boxSizing": "border-box"
                        }
                    ),
                ]),
                
                # Password
                html.Div([
                    html.Label([
                        html.I(className="fas fa-lock", style={"marginRight": "8px"}),
                        "Password"
                    ], style={
                        "fontWeight": "600",
                        "color": "#495057",
                        "marginBottom": "8px",
                        "display": "block"
                    }),
                    dcc.Input(
                        id="password-input",
                        type="password",
                        placeholder="Enter password",
                        style={
                            "width": "100%",
                            "padding": "12px 15px",
                            "border": "1px solid #ced4da",
                            "borderRadius": "6px",
                            "fontSize": "14px",
                            "marginBottom": "10px",
                            "boxSizing": "border-box"
                        }
                    ),
                ]),
                
                # Error message
                html.Div(id="login-error", style={
                    "color": "#dc3545",
                    "fontSize": "13px",
                    "marginBottom": "20px",
                    "minHeight": "20px",
                    "textAlign": "center"
                }),
                
                # Login button
                html.Button([
                    html.I(className="fas fa-sign-in-alt", style={"marginRight": "10px"}),
                    "Login"
                ], id="login-button", n_clicks=0, style={
                    "width": "100%",
                    "padding": "12px",
                    "background": "linear-gradient(135deg, #28a745 0%, #20c997 100%)",
                    "color": "white",
                    "border": "none",
                    "borderRadius": "6px",
                    "fontSize": "16px",
                    "fontWeight": "600",
                    "cursor": "pointer",
                    "transition": "all 0.3s ease",
                    "boxShadow": "0 4px 6px rgba(40, 167, 69, 0.3)"
                }),
                
            ], style={"padding": "0 30px"}),
            
        ], style={
            "background": "white",
            "padding": "40px 20px",
            "borderRadius": "12px",
            "boxShadow": "0 10px 40px rgba(0,0,0,0.1)",
            "maxWidth": "400px",
            "width": "100%"
        })
    ], style={
        "display": "flex",
        "justifyContent": "center",
        "alignItems": "center",
        "minHeight": "100vh",
        "background": "linear-gradient(135deg, #28a745 0%, #20c997 100%)",
        "padding": "20px"
    })

def get_controls(df):
    provinces = sorted(df["Province"].dropna().unique())
    districts = sorted(df["District"].dropna().unique())
    types = sorted(df["TransactionType"].dropna().unique())
    statuses = sorted(df["Status"].dropna().unique())
    channels = sorted(df["Channel"].dropna().unique())
    min_date, max_date = df["Date"].min(), df["Date"].max()

    return html.Div([
        # First row of filters
        html.Div([
            html.Div([
                html.Label([
                    html.I(className="fas fa-calendar-alt", style={"marginRight": "8px"}),
                    "Date Range"
                ], style={"fontWeight": "600", "color": "#495057", "marginBottom": "5px"}),
                dcc.DatePickerRange(
                    id="date-range",
                    start_date=min_date,
                    end_date=max_date,
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    display_format="YYYY-MM-DD",
                    style={"width": "100%"}
                ),
            ], style={"flex": "1", "minWidth": "200px", "margin": "8px"}),

            html.Div([
                html.Label([
                    html.I(className="fas fa-map-marked-alt", style={"marginRight": "8px"}),
                    "Province"
                ], style={"fontWeight": "600", "color": "#495057", "marginBottom": "5px"}),
                dcc.Dropdown(
                    id="province",
                    options=[{"label": p, "value": p} for p in provinces],
                    value=None,
                    multi=True,
                    placeholder="Select province(s)",
                    style={"width": "100%"}
                ),
            ], style={"flex": "1", "minWidth": "200px", "margin": "8px"}),

            html.Div([
                html.Label([
                    html.I(className="fas fa-map-marker-alt", style={"marginRight": "8px"}),
                    "District"
                ], style={"fontWeight": "600", "color": "#495057", "marginBottom": "5px"}),
                dcc.Dropdown(
                    id="district",
                    options=[{"label": d, "value": d} for d in districts],
                    value=None,
                    multi=True,
                    placeholder="Select district(s)",
                    style={"width": "100%"}
                ),
            ], style={"flex": "1", "minWidth": "200px", "margin": "8px"}),
        ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "15px"}),

        # Second row of filters
        html.Div([
            html.Div([
                html.Label([
                    html.I(className="fas fa-credit-card", style={"marginRight": "8px"}),
                    "Transaction Type"
                ], style={"fontWeight": "600", "color": "#495057", "marginBottom": "5px"}),
                dcc.Dropdown(
                    id="txn-type",
                    options=[{"label": t, "value": t} for t in types],
                    value=None,
                    multi=True,
                    placeholder="Select type(s)",
                    style={"width": "100%"}
                ),
            ], style={"flex": "1", "minWidth": "200px", "margin": "8px"}),

            html.Div([
                html.Label([
                    html.I(className="fas fa-info-circle", style={"marginRight": "8px"}),
                    "Status"
                ], style={"fontWeight": "600", "color": "#495057", "marginBottom": "5px"}),
                dcc.Dropdown(
                    id="status",
                    options=[{"label": s, "value": s} for s in statuses],
                    value=None,
                    multi=True,
                    placeholder="Select status(es)",
                    style={"width": "100%"}
                ),
            ], style={"flex": "1", "minWidth": "200px", "margin": "8px"}),

            html.Div([
                html.Label([
                    html.I(className="fas fa-mobile-alt", style={"marginRight": "8px"}),
                    "Channel"
                ], style={"fontWeight": "600", "color": "#495057", "marginBottom": "5px"}),
                dcc.Dropdown(
                    id="channel",
                    options=[{"label": c, "value": c} for c in channels],
                    value=None,
                    multi=True,
                    placeholder="Select channel(s)",
                    style={"width": "100%"}
                ),
            ], style={"flex": "1", "minWidth": "200px", "margin": "8px"}),

            html.Div([
                html.Label([
                    html.I(className="fas fa-sync-alt", style={"marginRight": "8px"}),
                    "Auto-refresh"
                ], style={"fontWeight": "600", "color": "#495057", "marginBottom": "5px"}),
                dcc.Dropdown(
                    id="refresh-interval",
                    options=[
                        {"label": "Off", "value": 0},
                        {"label": "30s", "value": 30000},
                        {"label": "60s", "value": 60000}
                    ],
                    value=0,
                    clearable=False,
                    style={"width": "100%"}
                ),
            ], style={"flex": "1", "minWidth": "150px", "margin": "8px"}),
        ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap"}),

        dcc.Interval(id="interval", interval=60000, n_intervals=0, disabled=True),  # Start disabled
    ], style={
        "background": "linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
        "padding": "20px",
        "borderRadius": "12px",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
        "marginBottom": "20px"
    })
    

# -----------------------
# KPI cards
# -----------------------
def kpi_row():
    return html.Div([
        # Total Transactions KPI
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-exchange-alt", style={
                            "fontSize": "36px", 
                            "color": "#667eea",
                            "marginBottom": "0"
                        }),
                    ], style={"flex": "0 0 auto", "marginRight": "20px"}),
                    html.Div([
                        html.H4("Total Transactions", style={
                            "margin": "0", 
                            "color": "#2c3e50", 
                            "fontSize": "14px", 
                            "fontWeight": "700",
                            "textTransform": "uppercase",
                            "letterSpacing": "1px",
                            "marginBottom": "8px"
                        }),
                        html.H2(id="kpi-total", style={
                            "margin": "0", 
                            "color": "#2c3e50", 
                            "fontSize": "36px", 
                            "fontWeight": "700",
                            "lineHeight": "1"
                        }),
                    ], style={"flex": "1"}),
                ], style={
                    "display": "flex", 
                    "alignItems": "center", 
                    "padding": "25px 30px"
                }),
            ], style={
                "background": "white",
                "borderRadius": "12px",
                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                "border": "1px solid #e9ecef",
                "borderLeft": "4px solid #667eea",
                "transition": "all 0.3s ease",
                "cursor": "pointer",
                "height": "100%"
            }, className="kpi-card")
        ], style={"flex": "1", "minWidth": "250px", "margin": "10px"}),

        # Total Value KPI
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-money-bill-wave", style={
                            "fontSize": "36px", 
                            "color": "#28a745",
                            "marginBottom": "0"
                        }),
                    ], style={"flex": "0 0 auto", "marginRight": "20px"}),
                    html.Div([
                        html.H4("Total Value", style={
                            "margin": "0", 
                            "color": "#2c3e50", 
                            "fontSize": "14px", 
                            "fontWeight": "700",
                            "textTransform": "uppercase",
                            "letterSpacing": "1px",
                            "marginBottom": "8px"
                        }),
                        html.H2(id="kpi-total-value", style={
                            "margin": "0", 
                            "color": "#2c3e50", 
                            "fontSize": "36px", 
                            "fontWeight": "700",
                            "lineHeight": "1"
                        }),
                    ], style={"flex": "1"}),
                ], style={
                    "display": "flex", 
                    "alignItems": "center", 
                    "padding": "25px 30px"
                }),
            ], style={
                "background": "white",
                "borderRadius": "12px",
                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                "border": "1px solid #e9ecef",
                "borderLeft": "4px solid #28a745",
                "transition": "all 0.3s ease",
                "cursor": "pointer",
                "height": "100%"
            }, className="kpi-card")
        ], style={"flex": "1", "minWidth": "250px", "margin": "10px"}),

        # Average Value KPI
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-chart-bar", style={
                            "fontSize": "36px", 
                            "color": "#fd7e14",
                            "marginBottom": "0"
                        }),
                    ], style={"flex": "0 0 auto", "marginRight": "20px"}),
                    html.Div([
                        html.H4("Average Value", style={
                            "margin": "0", 
                            "color": "#2c3e50", 
                            "fontSize": "14px", 
                            "fontWeight": "700",
                            "textTransform": "uppercase",
                            "letterSpacing": "1px",
                            "marginBottom": "8px"
                        }),
                        html.H2(id="kpi-avg-value", style={
                            "margin": "0", 
                            "color": "#2c3e50", 
                            "fontSize": "36px", 
                            "fontWeight": "700",
                            "lineHeight": "1"
                        }),
                    ], style={"flex": "1"}),
                ], style={
                    "display": "flex", 
                    "alignItems": "center", 
                    "padding": "25px 30px"
                }),
            ], style={
                "background": "white",
                "borderRadius": "12px",
                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                "border": "1px solid #e9ecef",
                "borderLeft": "4px solid #fd7e14",
                "transition": "all 0.3s ease",
                "cursor": "pointer",
                "height": "100%"
            }, className="kpi-card")
        ], style={"flex": "1", "minWidth": "250px", "margin": "10px"}),

        # Success Rate KPI
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-check-circle", style={
                            "fontSize": "36px", 
                            "color": "#17a2b8",
                            "marginBottom": "0"
                        }),
                    ], style={"flex": "0 0 auto", "marginRight": "20px"}),
                    html.Div([
                        html.H4("Success Rate", style={
                            "margin": "0", 
                            "color": "#2c3e50", 
                            "fontSize": "14px", 
                            "fontWeight": "700",
                            "textTransform": "uppercase",
                            "letterSpacing": "1px",
                            "marginBottom": "8px"
                        }),
                        html.H2(id="kpi-success-rate", style={
                            "margin": "0", 
                            "color": "#2c3e50", 
                            "fontSize": "36px", 
                            "fontWeight": "700",
                            "lineHeight": "1"
                        }),
                    ], style={"flex": "1"}),
                ], style={
                    "display": "flex", 
                    "alignItems": "center", 
                    "padding": "25px 30px"
                }),
            ], style={
                "background": "white",
                "borderRadius": "12px",
                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                "border": "1px solid #e9ecef",
                "borderLeft": "4px solid #17a2b8",
                "transition": "all 0.3s ease",
                "cursor": "pointer",
                "height": "100%"
            }, className="kpi-card")
        ], style={"flex": "1", "minWidth": "250px", "margin": "10px"}),
        
    ], style={
        "display": "flex", 
        "gap": "0px", 
        "flexWrap": "wrap", 
        "marginBottom": "30px",
        "margin": "-10px"  # Negative margin to offset card margins
    })

# -----------------------
# Layout
# -----------------------
def get_dashboard():
    return html.Div([
    # Add Font Awesome for icons
    html.Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"),
    
    # Sidebar overlay (hidden by default)
    html.Div([
        html.Div([
            # Close button
            html.Div([
                html.I(className="fas fa-times", id="close-sidebar", style={
                    "fontSize": "24px",
                    "color": "#6c757d",
                    "cursor": "pointer",
                    "float": "right"
                })
            ], style={"marginBottom": "30px"}),
            
            # User profile section
            html.Div([
                html.Div([
                    html.I(className="fas fa-user-circle", style={
                        "fontSize": "80px",
                        "color": "#28a745",
                        "marginBottom": "15px"
                    })
                ], style={"textAlign": "center"}),
                
                html.H3("Admin User", style={
                    "textAlign": "center",
                    "color": "#2c3e50",
                    "marginBottom": "5px",
                    "fontWeight": "bold"
                }),
                
                html.P("Administrator", style={
                    "textAlign": "center",
                    "color": "#6c757d",
                    "fontSize": "14px",
                    "marginBottom": "30px"
                }),
            ]),
            
            # Divider
            html.Hr(style={"borderColor": "#e9ecef", "margin": "20px 0"}),
            
            # User details
            html.Div([
                html.Div([
                    html.I(className="fas fa-user", style={"marginRight": "10px", "color": "#6c757d"}),
                    html.Strong("Username: "),
                    html.Span("admin")
                ], style={"marginBottom": "15px", "fontSize": "14px"}),
                
                html.Div([
                    html.I(className="fas fa-shield-alt", style={"marginRight": "10px", "color": "#6c757d"}),
                    html.Strong("Role: "),
                    html.Span("Administrator")
                ], style={"marginBottom": "15px", "fontSize": "14px"}),
                
                html.Div([
                    html.I(className="fas fa-clock", style={"marginRight": "10px", "color": "#6c757d"}),
                    html.Strong("Session: "),
                    html.Span("Active")
                ], style={"marginBottom": "15px", "fontSize": "14px"}),
            ], style={"padding": "0 20px"}),
            
            # Divider
            html.Hr(style={"borderColor": "#e9ecef", "margin": "20px 0"}),
            
            # Logout button
            html.Button([
                html.I(className="fas fa-sign-out-alt", style={"marginRight": "10px"}),
                "Logout"
            ], id="logout-button", n_clicks=0, style={
                "width": "100%",
                "padding": "12px",
                "background": "#dc3545",
                "color": "white",
                "border": "none",
                "borderRadius": "6px",
                "fontSize": "16px",
                "fontWeight": "600",
                "cursor": "pointer",
                "transition": "all 0.3s ease"
            }),
            
        ], style={
            "padding": "30px 20px",
            "height": "100%"
        })
    ], id="sidebar", style={
        "position": "fixed",
        "top": "0",
        "right": "-350px",  # Hidden by default
        "width": "350px",
        "height": "100vh",
        "background": "white",
        "boxShadow": "-2px 0 10px rgba(0,0,0,0.1)",
        "transition": "right 0.3s ease",
        "zIndex": "1000",
        "overflowY": "auto"
    }),
    
    # Header
    html.Div([
        html.Div([
            # Left side - Title
            html.Div([
                html.I(className="fas fa-chart-line", style={"marginRight": "15px", "fontSize": "2.5rem"}),
                html.Span("ZAMTEL MOBILE MONEY ANALYTICS DASHBOARD")
            ], style={ 
                "display": "flex",
                "alignItems": "center",
                "flex": "1"
            }),
            
            # Right side - User menu button
            html.Div([
                html.Button([
                    html.I(className="fas fa-user-circle", style={"fontSize": "20px", "marginRight": "8px"}),
                    html.Span("Admin", style={"marginRight": "8px"}),
                    html.I(className="fas fa-caret-down", style={"fontSize": "14px"})
                ], id="user-menu-button", n_clicks=0, style={
                    "padding": "10px 20px",
                    "background": "rgba(255, 255, 255, 0.2)",
                    "color": "white",
                    "border": "1px solid rgba(255, 255, 255, 0.3)",
                    "borderRadius": "8px",
                    "fontSize": "14px",
                    "fontWeight": "500",
                    "cursor": "pointer",
                    "transition": "all 0.3s ease",
                    "display": "flex",
                    "alignItems": "center"
                })
            ])
        ], style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "space-between",
            "color": "white",
            "fontSize": "2.5rem",
            "fontWeight": "bold",
            "marginBottom": "10px",
            "textShadow": "2px 2px 4px rgba(0,0,0,0.1)",
            "textTransform": "uppercase",
            "letterSpacing": "2px"
        }),
        html.P("Real-time insights into mobile money transactions across Zambia", 
               style={
                   "textAlign": "center", 
                   "color": "white", 
                   "fontSize": "1.1rem",
                   "marginBottom": "30px",
                   "fontWeight": "400",
                   "opacity": "0.95"
               })
    ], style={"background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", 
              "color": "white", 
              "padding": "30px", 
              "marginBottom": "20px",
              "borderRadius": "12px",
              "boxShadow": "0 4px 6px rgba(0,0,0,0.1)"}),

    # Controls
    html.Div(get_controls(df)),

    kpi_row(),

    html.Div([
        html.Div([
            dcc.Graph(id="time-series")
        ], className="six columns", style={"padding": "8px"}),

        html.Div([
            dcc.Graph(id="hourly-volume")
        ], className="six columns", style={"padding": "8px"}),
    ], style={"display": "flex", "gap": "8px", "flexWrap": "wrap"}),

    html.Div([
        html.Div([
            dcc.Graph(id="type-distribution")
        ], className="six columns", style={"padding": "8px"}),

        html.Div([
            dcc.Graph(id="status-by-channel")
        ], className="six columns", style={"padding": "8px"}),
    ], style={"display": "flex", "gap": "8px", "flexWrap": "wrap"}),

    html.Div([
        html.Div([
            dcc.Graph(id="province-performance")
        ], className="six columns", style={"padding": "8px"}),

        html.Div([
            dcc.Graph(id="district-performance")
        ], className="six columns", style={"padding": "8px"}),
    ], style={"display": "flex", "gap": "8px", "flexWrap": "wrap"}),

    html.Div([
        html.Div([
            dcc.Graph(id="top-agents-value")
        ], className="six columns", style={"padding": "8px"}),

        html.Div([
            dcc.Graph(id="top-agents-volume")
        ], className="six columns", style={"padding": "8px"}),
    ], style={"display": "flex", "gap": "8px", "flexWrap": "wrap"}),

    html.H3("Transaction table"),
    dash_table.DataTable(
        id="txn-table",
        columns=[{"name": c, "id": c} for c in df.columns if c != "SuccessFlag"],
        page_size=10,
        sort_action="native",
        filter_action="native",
        style_table={"overflowX": "auto"},
    ),
    
    # Hidden div to trigger initial load
    html.Div(id="initial-load", style={"display": "none"})
    ], style={"padding": "16px"})

# Main app layout with login
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="login-status", storage_type="session", data={"logged_in": False}),
    html.Div(id="page-content")
])

# -----------------------
# Helper: apply filters
# -----------------------
def apply_filters(df, start_date, end_date, province, district, txn_type, status, channel):
    # Date filter
    if start_date is not None:
        start = pd.to_datetime(start_date).date()
        df = df[df["Date"] >= start]
    if end_date is not None:
        end = pd.to_datetime(end_date).date()
        df = df[df["Date"] <= end]

    # Multi-select filters
    if province and len(province) > 0:
        df = df[df["Province"].isin(province)]
    if district and len(district) > 0:
        df = df[df["District"].isin(district)]
    if txn_type and len(txn_type) > 0:
        df = df[df["TransactionType"].isin(txn_type)]
    if status and len(status) > 0:
        df = df[df["Status"].isin(status)]
    if channel and len(channel) > 0:
        df = df[df["Channel"].isin(channel)]

    return df

# -----------------------
# Callbacks
# -----------------------

# Login callback
@app.callback(
    [Output("login-status", "data"),
     Output("login-error", "children")],
    Input("login-button", "n_clicks"),
    [State("username-input", "value"),
     State("password-input", "value")]
)
def login(n_clicks, username, password):
    if n_clicks > 0:
        if username == USERNAME and password == PASSWORD:
            return {"logged_in": True}, ""
        else:
            return {"logged_in": False}, "❌ Invalid username or password"
    return {"logged_in": False}, ""

# Page routing callback
@app.callback(
    Output("page-content", "children"),
    [Input("login-status", "data"),
     Input("url", "pathname")]
)
def display_page(login_data, pathname):
    if login_data and login_data.get("logged_in"):
        return get_dashboard()
    else:
        return get_login_page()

# Sidebar toggle callback
@app.callback(
    Output("sidebar", "style"),
    [Input("user-menu-button", "n_clicks"),
     Input("close-sidebar", "n_clicks")],
    [State("sidebar", "style")]
)
def toggle_sidebar(open_clicks, close_clicks, current_style):
    ctx = dash.callback_context
    if not ctx.triggered:
        # Default closed state
        return {
            "position": "fixed",
            "top": "0",
            "right": "-350px",
            "width": "350px",
            "height": "100vh",
            "background": "white",
            "boxShadow": "-2px 0 10px rgba(0,0,0,0.1)",
            "transition": "right 0.3s ease",
            "zIndex": "1000",
            "overflowY": "auto"
        }
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "user-menu-button":
        # Open sidebar
        return {
            "position": "fixed",
            "top": "0",
            "right": "0",
            "width": "350px",
            "height": "100vh",
            "background": "white",
            "boxShadow": "-2px 0 10px rgba(0,0,0,0.1)",
            "transition": "right 0.3s ease",
            "zIndex": "1000",
            "overflowY": "auto"
        }
    else:
        # Close sidebar
        return {
            "position": "fixed",
            "top": "0",
            "right": "-350px",
            "width": "350px",
            "height": "100vh",
            "background": "white",
            "boxShadow": "-2px 0 10px rgba(0,0,0,0.1)",
            "transition": "right 0.3s ease",
            "zIndex": "1000",
            "overflowY": "auto"
        }

# Logout callback
@app.callback(
    Output("login-status", "data", allow_duplicate=True),
    Input("logout-button", "n_clicks"),
    prevent_initial_call=True
)
def logout(n_clicks):
    if n_clicks > 0:
        return {"logged_in": False}
    return {"logged_in": True}

# Update interval value dynamically
@app.callback(
    [Output("interval", "interval"),
     Output("interval", "disabled")],
    Input("refresh-interval", "value")
)
def set_interval(interval_ms):
    if interval_ms and interval_ms > 0:
        return interval_ms, False  # Enable with specified interval
    return 60000, True  # Disable if 0

# Central update: compute KPIs and figures when filters or interval ticks change
@app.callback(
    [
        Output("kpi-total", "children"),
        Output("kpi-total-value", "children"),
        Output("kpi-avg-value", "children"),
        Output("kpi-success-rate", "children"),
        Output("time-series", "figure"),
        Output("hourly-volume", "figure"),
        Output("type-distribution", "figure"),
        Output("status-by-channel", "figure"),
        Output("province-performance", "figure"),
        Output("district-performance", "figure"),
        Output("top-agents-value", "figure"),
        Output("top-agents-volume", "figure"),
        Output("txn-table", "data"),
    ],
    [
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("province", "value"),
        Input("district", "value"),
        Input("txn-type", "value"),
        Input("status", "value"),
        Input("channel", "value"),
        Input("interval", "n_intervals"),
    ]
)
def update_all(start_date, end_date, province, district, txn_type, status, channel, n_intervals):
    try:
        print("\n" + "="*60)
        print("🔄 Callback triggered!")
        print(f"📅 Date range: {start_date} to {end_date}")
        print(f"🔍 Filters - Province: {province}, District: {district}")
        print(f"💳 Type: {txn_type}, Status: {status}, Channel: {channel}")
        print("="*60)
        
        # Use the global df instead of reloading
        df_local = df.copy()
        print(f"📊 Data loaded: {len(df_local)} rows")
        print(f"📅 Data date range: {df_local['Date'].min()} to {df_local['Date'].max()}")

        # Apply filters
        filt = apply_filters(df_local, start_date, end_date, province, district, txn_type, status, channel)
        print(f"🔍 After filters: {len(filt)} rows")

        # KPIs - Basic calculations
        total_txns = len(filt)
        total_value = 0.0
        avg_value = 0.0
        success_rate = 0.0
        
        if total_txns > 0:
            total_value = float(filt["Amount"].sum())
            avg_value = float(filt["Amount"].mean())
            success_rate = round(100 * filt["SuccessFlag"].mean(), 2)

        print(f"📈 KPIs calculated: {total_txns} transactions, {total_value:.2f} total value")

        # Create empty charts first
        fig_time = {"data": [], "layout": {"title": "TRANSACTION AMOUNTS OVER TIME"}}
        fig_hourly = {"data": [], "layout": {"title": "TRANSACTIONS BY HOUR"}}
        fig_type = {"data": [], "layout": {"title": "TRANSACTION TYPES"}}
        fig_status_channel = {"data": [], "layout": {"title": "STATUS BY CHANNEL"}}
        fig_prov = {"data": [], "layout": {"title": "VALUE BY PROVINCE"}}
        fig_dist = {"data": [], "layout": {"title": "VALUE BY DISTRICT"}}
        fig_agents_value = {"data": [], "layout": {"title": "TOP AGENTS BY VALUE"}}
        fig_agents_volume = {"data": [], "layout": {"title": "TOP AGENTS BY VOLUME"}}
        table_data = []

        # Only create charts if we have data
        if len(filt) > 0:
            try:
                # Time series
                if "Datetime" in filt.columns and "Amount" in filt.columns:
                    ts = filt.sort_values("Datetime")
                    fig_time = px.line(ts, x="Datetime", y="Amount", 
                                     title="TRANSACTION AMOUNTS OVER TIME")
                    fig_time.update_layout(
                        height=400,
                        title_font=dict(size=16, color="#2c3e50", family="Arial Black, Arial, sans-serif"),
                        title_x=0.5,
                        title_xanchor="center"
                    )
                
                # Hourly volume
                if "Hour" in filt.columns:
                    hourly = filt.groupby("Hour")["TransactionID"].count().reset_index(name="Count")
                    fig_hourly = px.bar(hourly, x="Hour", y="Count", title="TRANSACTIONS BY HOUR")
                    fig_hourly.update_layout(
                        height=400,
                        title_font=dict(size=16, color="#2c3e50", family="Arial Black, Arial, sans-serif"),
                        title_x=0.5,
                        title_xanchor="center"
                    )
                
                # Type distribution
                if "TransactionType" in filt.columns:
                    type_dist = filt.groupby("TransactionType")["TransactionID"].count().reset_index(name="Count")
                    fig_type = px.pie(type_dist, names="TransactionType", values="Count", 
                                    title="TRANSACTION TYPES")
                    fig_type.update_layout(
                        height=400,
                        title_font=dict(size=16, color="#2c3e50", family="Arial Black, Arial, sans-serif"),
                        title_x=0.5,
                        title_xanchor="center"
                    )
                
                # Status by channel
                if "Channel" in filt.columns and "Status" in filt.columns:
                    status_channel = filt.groupby(["Channel", "Status"])["TransactionID"].count().reset_index(name="Count")
                    fig_status_channel = px.bar(status_channel, x="Channel", y="Count", color="Status",
                                              title="STATUS BY CHANNEL")
                    fig_status_channel.update_layout(
                        height=400,
                        title_font=dict(size=16, color="#2c3e50", family="Arial Black, Arial, sans-serif"),
                        title_x=0.5,
                        title_xanchor="center"
                    )
                
                # Province performance
                if "Province" in filt.columns:
                    prov_perf = filt.groupby("Province")["Amount"].sum().reset_index()
                    fig_prov = px.bar(prov_perf, x="Province", y="Amount", title="VALUE BY PROVINCE")
                    fig_prov.update_layout(
                        height=400,
                        title_font=dict(size=16, color="#2c3e50", family="Arial Black, Arial, sans-serif"),
                        title_x=0.5,
                        title_xanchor="center"
                    )
                
                # District performance
                if "District" in filt.columns:
                    dist_perf = filt.groupby("District")["Amount"].sum().reset_index()
                    fig_dist = px.bar(dist_perf, x="District", y="Amount", title="VALUE BY DISTRICT")
                    fig_dist.update_layout(
                        height=400,
                        title_font=dict(size=16, color="#2c3e50", family="Arial Black, Arial, sans-serif"),
                        title_x=0.5,
                        title_xanchor="center"
                    )
                
                # Top agents
                if "AgentID" in filt.columns:
                    agents_value = filt.groupby("AgentID")["Amount"].sum().reset_index().sort_values("Amount", ascending=False).head(10)
                    fig_agents_value = px.bar(agents_value, x="AgentID", y="Amount", title="TOP AGENTS BY VALUE")
                    fig_agents_value.update_layout(
                        height=400,
                        title_font=dict(size=16, color="#2c3e50", family="Arial Black, Arial, sans-serif"),
                        title_x=0.5,
                        title_xanchor="center"
                    )
                    
                    agents_volume = filt.groupby("AgentID")["TransactionID"].count().reset_index(name="Count").sort_values("Count", ascending=False).head(10)
                    fig_agents_volume = px.bar(agents_volume, x="AgentID", y="Count", title="TOP AGENTS BY VOLUME")
                    fig_agents_volume.update_layout(
                        height=400,
                        title_font=dict(size=16, color="#2c3e50", family="Arial Black, Arial, sans-serif"),
                        title_x=0.5,
                        title_xanchor="center"
                    )
                
                # Table data
                if "SuccessFlag" in filt.columns:
                    table_data = filt.drop(columns=["SuccessFlag"]).to_dict("records")
                else:
                    table_data = filt.to_dict("records")
                    
            except Exception as chart_error:
                print(f"⚠️ Chart creation error: {chart_error}")
                # Keep empty charts

        print("✅ Callback completed successfully")
        
        return (
            f"{total_txns}",
            f"ZMW {total_value:,.2f}",
            f"ZMW {avg_value:,.2f}",
            f"{success_rate}%",
            fig_time,
            fig_hourly,
            fig_type,
            fig_status_channel,
            fig_prov,
            fig_dist,
            fig_agents_value,
            fig_agents_volume,
            table_data
        )
    except Exception as e:
        print(f"❌ Error in callback: {e}")
        import traceback
        traceback.print_exc()
        # Return safe default values
        return (
            "0",
            "ZMW 0.00",
            "ZMW 0.00",
            "0%",
            {"data": [], "layout": {"title": "NO DATA AVAILABLE"}},
            {"data": [], "layout": {"title": "NO DATA AVAILABLE"}},
            {"data": [], "layout": {"title": "NO DATA AVAILABLE"}},
            {"data": [], "layout": {"title": "NO DATA AVAILABLE"}},
            {"data": [], "layout": {"title": "NO DATA AVAILABLE"}},
            {"data": [], "layout": {"title": "NO DATA AVAILABLE"}},
            {"data": [], "layout": {"title": "NO DATA AVAILABLE"}},
            {"data": [], "layout": {"title": "NO DATA AVAILABLE"}},
            []
        )


if __name__ == "__main__":
    try:
        # Production deployment settings
        import os
        app.run(
            debug=False,  # IMPORTANT: Set to False for production
            host='0.0.0.0',  # Allow external connections
            port=int(os.environ.get('PORT', 8050)),  # Use PORT from environment or default to 8050
            threaded=True
        )
    except KeyboardInterrupt:
        print("Shutting down gracefully...")
    except Exception as e:
        print(f"Error running app: {e}")
