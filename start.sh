#!/bin/bash
# Start backend
cd /projects/grocery-calculator
uvicorn app.main:app --port 8080 --reload &
BACKEND_PID=$!

# Start frontend
cd /projects/grocery-calculator/frontend
npm run dev &
FRONTEND_PID=$!

echo "Backend running on PID $BACKEND_PID"
echo "Frontend running on PID $FRONTEND_PID"

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
