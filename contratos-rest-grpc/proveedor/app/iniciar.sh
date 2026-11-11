#!/bin/sh

uvicorn servidor_rest:app --host 0.0.0.0 --port 8000 &

python servidor_grpc.py &

wait
