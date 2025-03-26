#!/bin/bash

PORT=$1

echo "PORT: $PORT"

# Reset all questions
curl -X DELETE http://localhost:"$PORT"/questions
sleep 2
# Create sample project
curl -X POST -H "Content-Type: application/json" http://localhost:4005/projects -d '{"code": "p-1", "name": "Project 1"}'
curl -X POST -H "Content-Type: application/json" http://localhost:4005/projects -d '{"code": "p-2", "name": "Project 2"}'

sleep 1
# Load questions in the database
curl -X POST -H "Content-Type: text/yaml" --data-binary "@resources/questions-fairness-graph.yml" http://localhost:"$PORT"/questions/load
