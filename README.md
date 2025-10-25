# Zamtel Mobile Money Analytics Dashboard

A professional analytics dashboard for Zamtel Mobile Money transactions built with Dash and Plotly.

## Features

-  Real-time KPI tracking (Total Transactions, Total Value, Average Value, Success Rate)
-  Interactive charts and visualizations
- Advanced filtering (Date, Province, District, Transaction Type, Status, Channel)
- Auto-refresh functionality
-  Responsive design
-  Professional UI with modern styling

## Tech Stack

- **Python 3.11**
- **Dash 2.14** - Web framework
- **Plotly 5.17** - Interactive charts
- **Pandas 2.1** - Data processing
- **Gunicorn** - Production server

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
python app.py
```

3. Open browser to: http://localhost:8050

## Deployment

This app is configured for deployment on Render.com. See deployment instructions in the repository.

## Data

The dashboard uses `zamtel_mobile_money_200.csv` containing 200 sample transactions from October 1-11, 2025.

## Author

CHUNDA LUCHEMBE AKA SPL_DEV
