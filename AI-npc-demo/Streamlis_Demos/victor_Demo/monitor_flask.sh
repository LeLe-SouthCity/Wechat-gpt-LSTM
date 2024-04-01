#!/bin/bash

# Command to start the Flask application
FLASK_CMD="python vectorflask.py"
# URL to check the Flask service
CHECK_URL="http://localhost:5000/chat"
# Data to send in the check request
CHECK_DATA='{"user_input": "你对我了解多少？"}'
# Content type
CONTENT_TYPE="Content-Type: application/json"
# Threshold for consecutive failures
MAX_FAILS=1
# Current failure count
fail_count=0
# PID file for the Flask application
PID_FILE="flask.pid"

# Function to check if Flask service is responsive
check_flask() {
  response=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "${CONTENT_TYPE}" -d "${CHECK_DATA}" "${CHECK_URL}")
  if [ "$response" -eq 200 ]; then
    echo "Flask service is responsive."
    fail_count=0
  else
    echo "Flask service is not responding."
    ((fail_count++))
  fi
}

# Function to start the Flask service
start_flask() {
  echo "Starting Flask service..."
  nohup $FLASK_CMD > flask_output.log 2>&1 &
  echo $! > "${PID_FILE}"
  echo "Flask service has been started."
}

# Function to kill the Flask service process
kill_flask() {
  if [ -f "${PID_FILE}" ]; then
    PID=$(cat "${PID_FILE}")
    echo "Stopping Flask service (PID: ${PID})..."
    kill -9 "${PID}"
    rm -f "${PID_FILE}"
    echo "Flask service has been stopped."
  else
    echo "PID file does not exist. Cannot stop Flask service."
  fi
}

# Start the Flask service
start_flask

# Main loop to check every hour if the Flask service is responsive, and restart if it fails consecutively
while true; do
  check_flask
  if [ "$fail_count" -ge "$MAX_FAILS" ]; then
    echo "Flask service has failed to respond ${MAX_FAILS} times in a row. Attempting to restart..."
    kill_flask
    sleep 5 # Give the Flask service some time to fully stop
    start_flask
    fail_count=0
  fi
  sleep 3600 # Wait for one hour before checking again
done
