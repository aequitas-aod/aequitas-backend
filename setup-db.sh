#!/bin/bash

# Wait for the server to start
while ! nc -z 127.0.0.1 4005; do
  sleep 1
  echo "Wait for the server to start"
done

# Load questions in the database
curl -X DELETE http://localhost:4005/questions
curl -X POST -H "Content-Type: text/yaml" --data-binary "@resources/questions-fairness-graph.yml" http://localhost:4005/questions/load
