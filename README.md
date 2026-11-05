# API lab: QuickPizza

ITDS362 — API testing with Python, pytest and requests (lab version 2.0).

The suite sends real HTTP requests to https://quickpizza.grafana.com. It covers public endpoints, registration/login errors, rating CRUD, input partitions, update boundaries and ownership. Each test that needs private data creates a unique `lab-<12 hex digits>` user and logs in. All requests use one session to preserve the load-balancer cookies. Created ratings are deleted during fixture teardown, including when a test fails.

## Install and run

Requires Python 3.10+, Git and curl. From the repository directory on macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -v
```

Generate and open the self-contained report:

```bash
pytest -v --html=report.html --self-contained-html
```

Open `report.html` in a browser. Expected results while Defect 1 remains: **32 passed, 1 xfailed** (33 cases). The strict xfail becomes a failure when the API fixes the defect, signalling that the mark should be removed. See `RESULTS.md` for the observed run, defect report and reflection.

`conftest.py` selects short tracebacks by default so report failures do not display fixture arguments containing login tokens.

Check that the delete test works independently:

```bash
pytest -v test_ratings.py::test_delete_rating
```

This is a shared service: run when needed, never in a loop. Use only the users and ratings created by these tests. The public practice token in `auth.txt` is used only to read tools or request pizza recommendations, never to mutate ratings. `madeup.txt` is only for the read-only investigation in Part B.7. No real passwords or private API keys are required. Each HTTP request has a 30-second timeout; transport errors remain visible rather than being retried or hidden.

## Curl exercises

```bash
curl https://quickpizza.grafana.com/api/names
curl -i https://quickpizza.grafana.com/api/names
curl -i https://quickpizza.grafana.com/api/tools
curl -H "@auth.txt" https://quickpizza.grafana.com/api/tools
curl -H "@auth.txt" -d "@veg.json" https://quickpizza.grafana.com/api/pizza
curl -i -H "@auth.txt" -H "Content-Type: application/json" -d "@excluded_all.json" https://quickpizza.grafana.com/api/pizza
curl -i -H "@madeup.txt" https://quickpizza.grafana.com/api/ratings
```

Use `curl.exe` instead of `curl` in Windows PowerShell. The all-tools-excluded request generates no rating. Never use either example token to create, update or delete ratings.

## A1–A2: Input domain model and base choice coverage

Operation: `POST /api/ratings`. Base choice: integer `stars=3`, a pizza returned for this test, and this test user's own login token. Each additional case changes one characteristic from the base. Case names below are in `test_create_rating.py`.

| Characteristic | Block | Representative input | Covering test |
| --- | --- | --- | --- |
| C1 Value of stars | Below 1 | `0` | `test_stars_out_of_range[0]` |
| C1 Value of stars | 1–5 **(base)** | `3` | `test_base_choice_is_saved` |
| C1 Value of stars | Above 5 | `6` | `test_stars_out_of_range[6]` |
| C2 Type of stars | Whole number **(base)** | `3` | `test_base_choice_is_saved` |
| C2 Type of stars | Decimal | `3.5` | `test_invalid_stars_type[decimal]` |
| C2 Type of stars | Text | `"3"` | `test_invalid_stars_type[text]` |
| C2 Type of stars | Missing | No `stars` field | `test_invalid_stars_type[missing]` |
| C3 Pizza | Exists **(base)** | This test's generated pizza id | `test_base_choice_is_saved` |
| C3 Pizza | Does not exist | `999999999` | `test_nonexistent_pizza_is_refused` |
| C4 Token | User's own **(base)** | Token returned by login | `test_base_choice_is_saved` |
| C4 Token | None | No Authorization header | `test_invalid_token_is_refused[none]` |
| C4 Token | Wrong length | `token short` | `test_invalid_token_is_refused[wrong-length]` |

Base choice requires `1 + (3−1) + (4−1) + (2−1) + (3−1) = 9` cases. The model's Cartesian product has `3 × 4 × 2 × 3 = 72` combinations. This is the lab's simplified model: C1 describes numeric range, so it has no meaningful numeric value when C2 is missing or nonnumeric; the count of 72 is the formal model count before considering infeasible combinations.

The expected invalid-input messages were first checked using curl with a newly registered user and a shared cookie jar. Decimal and string stars produce Go JSON-decoding errors; missing stars produces the range error; a nonexistent pizza produces `pizza ID 999999999 not found`; missing and short tokens produce `authentication failed`. Tests check both status and exact JSON error.

## A3–A4: Boundaries and ownership

`test_update_rating.py` covers `(stars, status)` values `(0,400)`, `(1,200)`, `(5,200)`, `(6,400)`. Each case reads the rating back: accepted updates must persist, and refused updates must preserve the complete original rating.

`test_rating_owner.py` creates an independent second user for each of GET, PUT and DELETE. Each attempted operation must return a 4xx response, followed by an owner read proving the rating still exists unchanged. Exact observed codes are recorded in `RESULTS.md` and captured in the HTML report.

## Repository structure

```text
api-lab/
  .gitignore
  README.md
  RESULTS.md
  requirements.txt
  report.html
  auth.txt
  veg.json
  madeup.txt
  conftest.py
  test_names.py
  test_tools.py
  test_pizza.py
  test_users.py
  test_ratings.py
  test_refused.py
  test_excluded_tools.py
  test_create_rating.py
  test_update_rating.py
  test_rating_owner.py
  excluded_all.json
```

`excluded_all.json` is the additional JSON request body used by curl in Step 0.16.

## Test files

| File | Coverage |
| --- | --- |
| `test_names.py`, `test_tools.py`, `test_pizza.py` | Public reads, vegetarian ingredients and missing authentication |
| `test_users.py`, `test_refused.py` | New-user login, duplicate username, wrong password and empty username |
| `test_ratings.py` | Create, read, update and delete |
| `test_excluded_tools.py` | Zero, one, two and three excluded tools; strict expected failure |
| `test_create_rating.py` | Nine base-choice cases |
| `test_update_rating.py` | Four update boundary cases |
| `test_rating_owner.py` | Three cross-user access attempts |

The optional no-session experiment (Step 0.12) was not performed, and no flaky no-session test is included.
