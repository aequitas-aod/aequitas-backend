#!/bin/bash


# Wait for the server to start
while ! nc -z 127.0.0.1 4005; do
  sleep 1
  echo "Wait for the server to start"
done

# Reset all questions
curl -X DELETE http://localhost:4005/questions
sleep 2
# Create sample project
curl -X POST -H "Content-Type: application/json" http://localhost:4005/projects -d '{"id": {"code": "p-1"}, "name": "Project 1"}'
sleep 1
# Load questions in the database
curl -X POST -H "Content-Type: text/yaml" --data-binary "@resources/questions-fairness-graph.yml" http://localhost:4005/questions/load
