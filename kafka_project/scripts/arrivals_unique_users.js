import http from 'k6/http';
import { check, fail } from 'k6';
import { SharedArray } from 'k6/data';
import exec from 'k6/execution';

// 여러 "고유 유저"가 각 1회씩 요청.
// TOTAL 명이 DURATION 동안 정확히 도착하도록 constant-arrival-rate 사용.
// CSV( users.csv: user_id,token ) 있으면 각기 다른 토큰으로 호출.


// 환경변수 
const BASE_URL = __ENV.BASE_URL || 'http://proxy';
const TOTAL = Number(__ENV.TOTAL || 14000);
const DURATION = __ENV.DURATION || '180s';        // 예: '5m' 또는 '300s'
const USE_CSV = (__ENV.CSV || '1') === '1';     // 기본 CSV 사용
const COMMON_TOKEN = __ENV.TOKEN || '';         // CSV 없을 때만 사용
const EVENT_ID = Number(__ENV.EVENT_ID || 1);


// '5m' / '300s' → 초(second)
function toSeconds(s) {
  const m = s.match(/^(\d+)([ms])$/);
  if (!m) fail(`DURATION 형식 오류: ${s}`);
  const n = Number(m[1]);
  return m[2] === 'm' ? n * 60 : n;
}
const DURATION_SEC = toSeconds(DURATION);
const DURATION_MS = DURATION_SEC * 1000;

// 초당 도착률 
const ratePerSec = TOTAL / DURATION_SEC;

// gcd로 timeUnit을 ms로 잡아 rate를 정수로 만든다. 
function gcd(a, b) { while (b) { const t = a % b; a = b; b = t; } return a; }
const g = gcd(TOTAL, DURATION_MS);              // BOTH 정수
const TIMEUNIT_MS = Math.max(1, Math.floor(DURATION_MS / g)); // ms
const RATE_INT    = Math.floor(TOTAL / g);      // 정수 rate
const TIMEUNIT_STR = (TIMEUNIT_MS % 1000 === 0)
  ? `${TIMEUNIT_MS / 1000}s`
  : `${TIMEUNIT_MS}ms`;

// 내부 VU 풀 크기(경험칙) : 초당 도착률 기준으로 계산
const MAX_VUS = 180


// CSV 로드(유저)
const users = new SharedArray('users', () => {
  if (!USE_CSV) return [];
  const raw = open('/infra/users.csv').trim().split('\n'); //경로 기준 main-pj
  const header = raw.shift().split(',');
  const uidIdx = header.indexOf('user_id');
  const tokIdx = header.indexOf('token');
  if (uidIdx < 0 || tokIdx < 0) fail("users.csv 헤더는 'user_id,token' 여야 합니다.");
  return raw.map((line) => {
    const cols = line.split(',');
    return { user_id: Number(cols[uidIdx]), token: cols[tokIdx].trim() };
  });
});


export const options = {
  scenarios: {
    unique_arrivals: {
      executor: 'constant-arrival-rate',
      rate: RATE_INT,
      timeUnit: TIMEUNIT_STR,  // 예: '1m' 또는 '750s' 등
      duration: DURATION,
      preAllocatedVUs: 70,
      maxVUs: MAX_VUS,
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<1000', 'p(99)<2000'],
    http_req_failed: ['rate<0.05'],
  },
};

// 시나리오의 본체, 메인
export default function () {
  let user_id, token;

  if (USE_CSV) {
    // TOTAL ≤ users.length 권장 (1유저 1회에 가까움)
    const u = users[Math.floor(Math.random() * users.length)];
    user_id = u.user_id;
    token = u.token;
  } else {
    // CSV 없으면 공용 토큰(한 계정) 사용 → "모두 같은 사용자"로 인식됨
    user_id = Math.floor(Math.random() * 1e12); // 의미 없는 난수
    token = COMMON_TOKEN || null;
  }

  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = http.post(
    `${BASE_URL}/api/coupon-issue/`,
    JSON.stringify({ event_id: EVENT_ID, user_id }),
    { headers }
  );
  const ok = check(res, { 'status 2xx/3xx': (r) => r.status >= 200 && r.status < 400 });

  // 처음 5건 실패 샘플만 로그
  const i = exec.scenario.iterationInTest;
  if (!ok && i < 5) {
	  console.log(`FAIL[${i}] status=${res.status} body=${res.body && res.body.substring(0, 200)}`);
  }


}

