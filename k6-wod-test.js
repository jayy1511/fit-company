import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 50,           // number of virtual users
  duration: '30s',   // duration of the test
};

export default function () {
  const url = 'http://localhost:5001/fitness/wod';
  const headers = {
    Authorization: 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbjIyQGV4YW1wbGUuY29tIiwibmFtZSI6IkFkbWluMjIiLCJyb2xlIjoiYWRtaW4iLCJpc3MiOiJmaXQtYXBpIiwiaWF0IjoxNzQ4OTA5ODM2LCJleHAiOjE3NDg5MTE2MzZ9.xrVscUOGZCIiKFLiJ0djKSCHU8Xb9icqUJEzfTggtSw',  // paste a valid token here
  };

  const res = http.get(url, { headers });

  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  sleep(1);
}
