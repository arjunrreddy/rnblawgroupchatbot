#!/bin/bash
cd "$(dirname "$0")"  # Ensure script runs from backend directory
uvicorn main:app --host 0.0.0.0 --port 8000