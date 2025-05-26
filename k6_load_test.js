import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 50,
  duration: '30s',
};

const BASE_URL = 'http://localhost:5001'; 
const TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsIm5hbWUiOiJBZG1pbiIsInJvbGUiOiJhZG1pbiIsImlzcyI6ImZpdC1hcGkiLCJpYXQiOjE3NDgyOTA4NzQsImV4cCI6MTc0ODI5MjY3NH0.ulVal9AxYGDIz9Oy_fBq5GPsGxVKl9-KtbEUlJ9WxTY'; 

export default function () {
  const res = http.get(`${BASE_URL}/fitness/wod`, {
    headers: {
      Authorization: `Bearer ${TOKEN}`,  // ✅ Fixed here
    },
  });

  check(res, {
    'status is 200': (r) => r.status === 200,
  });
}
