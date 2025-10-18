import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export let errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '2m', target: 100 }, // Ramp up
    { duration: '5m', target: 100 }, // Stay at 100 users
    { duration: '2m', target: 200 }, // Ramp up to 200 users
    { duration: '5m', target: 200 }, // Stay at 200 users
    { duration: '2m', target: 0 }, // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must complete below 500ms
    http_req_failed: ['rate<0.1'], // Error rate must be below 10%
    errors: ['rate<0.1'],
  },
};

const BASE_URL = 'http://localhost:8000';

export default function () {
  // Test homepage
  let response = http.get(`${BASE_URL}/`);
  check(response, {
    'homepage status is 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);

  // Test API endpoints
  response = http.get(`${BASE_URL}/api/posts/`);
  check(response, {
    'API posts status is 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);

  // Test search
  response = http.get(`${BASE_URL}/api/search/?q=test`);
  check(response, {
    'search status is 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);
}

