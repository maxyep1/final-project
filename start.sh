#!/bin/bash
# start Flask backend
python code/backend/app.py &
# start Streamlit frontend
streamlit run code/frontend/main.py --server.port=8080 --server.address=0.0.0.0
