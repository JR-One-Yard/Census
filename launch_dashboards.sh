#!/bin/bash
# Dashboard Launcher Script
# Easily launch either the Lifestyle Explorer or Investment Research dashboard

echo "=========================================="
echo "🏖️ CENSUS LIFESTYLE DASHBOARDS"
echo "=========================================="
echo ""
echo "Select a dashboard to launch:"
echo ""
echo "1) 🏖️  Lifestyle Explorer Dashboard"
echo "   - Explore 61,844 SA1 areas"
echo "   - Filter by state, income, lifestyle score"
echo "   - Interactive maps and visualizations"
echo ""
echo "2) 💰 Investment Research Dashboard"
echo "   - Property investment analysis"
echo "   - Price forecasting (5-20 years)"
echo "   - ROI calculations"
echo "   - Portfolio builder"
echo ""
echo "3) 🚀 Launch Both (in separate terminals)"
echo ""
echo "4) Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🏖️  Launching Lifestyle Explorer Dashboard..."
        echo "Dashboard will open in your browser at http://localhost:8501"
        echo ""
        cd /home/user/Census
        streamlit run dashboard_lifestyle_explorer.py
        ;;
    2)
        echo ""
        echo "💰 Launching Investment Research Dashboard..."
        echo "Dashboard will open in your browser at http://localhost:8501"
        echo ""
        cd /home/user/Census
        streamlit run dashboard_investment_research.py
        ;;
    3)
        echo ""
        echo "🚀 Launching both dashboards..."
        echo "Lifestyle Explorer: http://localhost:8501"
        echo "Investment Research: http://localhost:8502"
        echo ""
        cd /home/user/Census
        streamlit run dashboard_lifestyle_explorer.py --server.port 8501 &
        streamlit run dashboard_investment_research.py --server.port 8502 &
        echo ""
        echo "✓ Both dashboards launched!"
        echo "Press Ctrl+C to stop all dashboards"
        wait
        ;;
    4)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac
