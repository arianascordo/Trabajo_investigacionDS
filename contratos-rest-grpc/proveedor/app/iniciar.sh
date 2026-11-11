#!/bin/sh

uvicorn servidor_rest:app --host 0.0.0.0 --port 8000 &

exec python -u servidor_grpc.py
