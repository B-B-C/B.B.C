#!/bin/bash

echo "Starting monitoring stack..."

# Start the main application with monitoring
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

echo "Waiting for services to start..."
sleep 30

echo "Monitoring services started:"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3000 (admin/admin)"
echo "- Alertmanager: http://localhost:9093"
echo "- Node Exporter: http://localhost:9100"
echo "- Postgres Exporter: http://localhost:9187"

echo "To view logs:"
echo "docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml logs -f"




