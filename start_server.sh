#!/bin/bash
# Process manager script for the Django chatbot application
# Provides automatic restart on crashes and proper signal handling

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$PROJECT_DIR/server.pid"
MAX_RESTARTS=5
RESTART_DELAY=5

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to handle cleanup
cleanup() {
    echo "[$(date)] Shutting down server..."
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill -TERM "$PID"
            echo "[$(date)] Sent TERM signal to process $PID"
            # Wait for graceful shutdown
            for i in {1..10}; do
                if ! kill -0 "$PID" 2>/dev/null; then
                    echo "[$(date)] Process $PID terminated gracefully"
                    break
                fi
                sleep 1
            done
            # Force kill if still running
            if kill -0 "$PID" 2>/dev/null; then
                kill -KILL "$PID"
                echo "[$(date)] Force killed process $PID"
            fi
        fi
        rm -f "$PID_FILE"
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Function to start the server
start_server() {
    echo "[$(date)] Starting Django server..."
    
    # Change to project directory
    cd "$PROJECT_DIR"
    
    # Run startup validation first
    if ! python validate_startup.py; then
        echo "[$(date)] Startup validation failed"
        return 1
    fi
    
    # Start the server with gunicorn for production-like behavior
    gunicorn --bind 127.0.0.1:8000 \
             --workers 2 \
             --timeout 120 \
             --keep-alive 2 \
             --max-requests 1000 \
             --max-requests-jitter 100 \
             --access-logfile "$LOG_DIR/access.log" \
             --error-logfile "$LOG_DIR/error.log" \
             --pid "$PID_FILE" \
             --daemon \
             chatbot_project.wsgi:application
    
    if [ $? -eq 0 ]; then
        echo "[$(date)] Server started successfully with PID $(cat "$PID_FILE")"
        return 0
    else
        echo "[$(date)] Failed to start server"
        return 1
    fi
}

# Function to check if server is running
is_server_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            return 0
        else
            # PID file exists but process is dead
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to monitor and restart server
monitor_server() {
    restart_count=0
    
    while [ $restart_count -lt $MAX_RESTARTS ]; do
        if ! is_server_running; then
            echo "[$(date)] Server is not running. Attempting restart ($((restart_count + 1))/$MAX_RESTARTS)..."
            
            if start_server; then
                restart_count=0  # Reset counter on successful start
            else
                restart_count=$((restart_count + 1))
                if [ $restart_count -lt $MAX_RESTARTS ]; then
                    echo "[$(date)] Restart failed. Waiting ${RESTART_DELAY}s before retry..."
                    sleep $RESTART_DELAY
                fi
            fi
        fi
        
        sleep 10  # Check every 10 seconds
    done
    
    echo "[$(date)] Maximum restart attempts reached. Giving up."
    cleanup
}

# Main execution
echo "[$(date)] Starting chatbot server manager..."

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "[$(date)] Warning: No virtual environment detected. Consider activating one."
fi

# Start monitoring
monitor_server
