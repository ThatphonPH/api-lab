# API lab results

## Part 0

- Step 0.1, the number of pizza names: 18.
- Step 0.3, status code of the request without a token: 401, with `{"error":"authentication failed"}`.
- Step 0.4, the name of your pizza: A Big Siciliana. The response returned 200 and every ingredient was vegetarian.
- Step 0.12, results of the three runs without a session (optional): Not performed.
- Step 0.16, blocks of "how many of the three tools are excluded": 0, 1, 2 and 3. The original inputs covered only 1 excluded tool. Added inputs were `[]` for 0, `["Knife", "Scissors"]` for 2, and `["Knife", "Pizza cutter", "Scissors"]` for 3. Excluding all 3 revealed the defect and is covered by a separate strict xfail test.

## Defect report

- Title: Defect 1 — Excluding all three tools causes an empty 500 response.
- Request: `POST https://quickpizza.grafana.com/api/pizza`, with a valid Authorization header, `Content-Type: application/json`, and body `{"excludedTools":["Knife","Pizza cutter","Scissors"]}`. Reproduce using `curl -i -H "@auth.txt" -H "Content-Type: application/json" -d "@excluded_all.json" https://quickpizza.grafana.com/api/pizza`. The pytest case uses its own newly registered user's token; the public practice token is used only for this recommendation request, never to modify ratings.
- Expected result: 400 with a nonempty JSON error explaining that no pizza can satisfy the restrictions.
- Actual result: HTTP/2 500, `Content-Length: 0`, and an empty body. Confirmed with curl and pytest on 5 November 2026 (Asia/Bangkok).
- Severity: Medium. An unsatisfiable restriction breaks recommendation handling and gives the caller no useful explanation. No data loss was observed, and requests leaving an available tool still work.

## Part A

- Step A4, status codes when the other user reads, changes and deletes: GET 404, PUT 400, DELETE 400. GET returned `{"error":"not found"}`; PUT and DELETE returned `{"error":"rating ID <id> not found"}`. After every attempt, the owner read returned 200 with the original rating unchanged.

## Part B

1. Real API tests can reveal incorrect HTTP routing/authentication middleware or JSON serialization, and failures in the interaction between registration, load balancing and stored user data. Unit tests with stubbed neighbours cannot prove those deployed components work together. Unit tests are still useful because they are fast, deterministic and can exercise rare internal error paths without depending on internet access or a running service.

2. A unique user provides its own token and isolates each test's ratings from classmates and other tests. The shared public token would mix test data with everyone's ratings. In Project 2, create identifiable test-owned customers and orders or guests and bookings, record their ids, use only the group's authorized credentials, and clean up only records created by the tests. Do not modify other groups' data.

3. A session retains the AWSALB cookies returned by the load balancer, so registration, login and later requests stay on the same backend, where that user's state exists. Without those cookies, a login can reach a different backend and be rejected even though registration succeeded. Sharing a session does not mean sharing the same user: each test still gets a fresh token. The optional three-run experiment was not performed.

4. The block excluding all three tools revealed Defect 1. A 500 incorrectly suggests a server failure and its empty body cannot be parsed into a useful JSON explanation; a caller may display a generic error or retry an impossible request. A 400 with a message lets the app ask the user to relax a restriction. Keeping the test as strict xfail documents the unmet requirement and detects when the fix makes the expected failure obsolete.

5. Base choice needs `1 + (3−1) + (4−1) + (2−1) + (3−1) = 9` tests. All combinations in the given model need `3 × 4 × 2 × 3 = 72`. Base choice varies one characteristic at a time while holding the others at base. As explained in README, 72 is the formal product before excluding semantically infeasible combinations, such as assigning a numeric range to a missing value.

6. The observed other-user codes were GET 404, PUT 400 and DELETE 400. For a logged-in user without ownership, 403 Forbidden is a natural expectation; 404 is also reasonable when deliberately concealing resource existence. The general 400 used for PUT and DELETE is less precise and inconsistent with GET. It is an API design concern, but the lab's explicit requirement accepts any 4xx refusal followed by an unchanged owner read, so these responses do not establish an ownership defect. No unauthorized read, modification or deletion succeeded in these tests.

7. With `Authorization: token 0000000000000000`, `GET /api/ratings` returned **200** and a JSON object containing a nonempty `ratings` list. In the curl observation there were **50 ratings**, including `{"id":1,"stars":5,"pizza_id":1}`; contents can change on the shared demo. This made-up token was never obtained by login, so an authentication-enforcing production API should reject it with 401. Accepting it for this read is a security defect against that expectation: a stranger could read rating data without authenticating. Whether they could modify data was not tested; only GET was sent with this token. Demo behavior should not be copied as a production authorization design.

8. API tests can check exact status codes, headers, JSON field types and malformed-input responses more directly than browser tests. Only a test through the web pages can check whether the visible error is actually displayed correctly or whether a user can operate the buttons and forms in the browser.
