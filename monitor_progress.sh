#!/bin/bash

# Monitor Bayesian model execution progress

echo "=========================================="
echo "Bayesian Model Execution Monitor"
echo "=========================================="
echo ""

while true; do
    clear
    echo "=========================================="
    echo "Bayesian Model Execution Monitor"
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="
    echo ""

    # Check if process is still running
    if pgrep -f "hierarchical_bayesian_spatial_model.py" > /dev/null; then
        echo "Status: ✓ MODEL RUNNING"
        echo ""

        # Show last 30 lines of output
        echo "Recent output:"
        echo "----------------------------------------"
        tail -30 bayesian_model_output.log
        echo "----------------------------------------"

    else
        echo "Status: ✗ MODEL COMPLETED OR STOPPED"
        echo ""
        echo "Final output:"
        echo "----------------------------------------"
        tail -50 bayesian_model_output.log
        echo "----------------------------------------"
        break
    fi

    echo ""
    echo "Refreshing in 60 seconds... (Ctrl+C to stop monitoring)"
    sleep 60
done
