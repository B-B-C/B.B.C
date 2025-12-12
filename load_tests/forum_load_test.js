import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
export let errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up to 10 users
    { duration: '5m', target: 10 }, // Stay at 10 users
    { duration: '2m', target: 20 }, // Ramp up to 20 users
    { duration: '5m', target: 20 }, // Stay at 20 users
    { duration: '2m', target: 0 },  // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests must complete below 2s
    http_req_failed: ['rate<0.1'],     // Error rate must be below 10%
    errors: ['rate<0.1'],               // Custom error rate
  },
};

const BASE_URL = 'http://localhost:8000';

export default function() {
  // Test homepage
  let response = http.get(`${BASE_URL}/`);
  check(response, {
    'homepage status is 200': (r) => r.status === 200,
    'homepage contains forum title': (r) => r.body.includes('Темы форума'),
  }) || errorRate.add(1);

  sleep(1);

  // Test post creation (if authenticated)
  let loginResponse = http.post(`${BASE_URL}/users/login/`, {
    username: 'testuser',
    password: 'testpass123',
  });

  if (loginResponse.status === 200 || loginResponse.status === 302) {
    // Test creating a post
    let postData = {
      title: `Load Test Post ${__VU}`,
      body: 'This is a load test post',
    };

    let postResponse = http.post(`${BASE_URL}/new-post/`, postData);
    check(postResponse, {
      'post creation status is 200 or 302': (r) => r.status === 200 || r.status === 302,
    }) || errorRate.add(1);

    sleep(1);

    // Test commenting on a post
    let commentData = {
      content: `Load test comment ${__VU}`,
    };

    let commentResponse = http.post(`${BASE_URL}/post/1/`, commentData);
    check(commentResponse, {
      'comment creation status is 200 or 302': (r) => r.status === 200 || r.status === 302,
    }) || errorRate.add(1);
  }

  sleep(2);

  // Test search functionality
  let searchResponse = http.get(`${BASE_URL}/?q=test`);
  check(searchResponse, {
    'search status is 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);

  // Test sorting
  let sortResponse = http.get(`${BASE_URL}/?sort=popular`);
  check(sortResponse, {
    'sort status is 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);
}

export function handleSummary(data) {
  return {
    'load_test_results.json': JSON.stringify(data, null, 2),
  };
}




