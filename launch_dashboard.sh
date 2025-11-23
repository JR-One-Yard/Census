#!/bin/bash
# Launch the Rental Stress Monitoring Dashboard

echo "=" | tr '=' '='  | head -c 80
echo ""
echo "🏘️  RENTAL STRESS MONITORING DASHBOARD"
echo "=" | tr '=' '='  | head -c 80
echo ""
echo ""
echo "Starting dashboard server..."
echo "Access the dashboard at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

# Launch Streamlit
streamlit run advanced_step5_dashboard.py --server.port 8501 --server.address 0.0.0.0
