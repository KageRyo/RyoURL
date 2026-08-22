# Testing

The consolidated test suite is an HTTP-level suite. It assumes the API is already running and uses credentials supplied through `tests/.env`.

## Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r tests/requirements.txt
cp tests/.env.example tests/.env
```

Set these values in `tests/.env`:

```text
BASE_URL=http://127.0.0.1:8003/api/
TEST_USER_USERNAME=your_test_user
TEST_USER_PASSWORD=your_test_user_password
ADMIN_USER_USERNAME=your_admin_user
ADMIN_USER_PASSWORD=your_admin_user_password
```

The named users must already exist in the running application, and the administrator must have `user_type=2`.

## API tests

Start the backend, then run the suite from the repository root:

```bash
pytest
```

The root `pytest.ini` adds `backend/` and `tests/` to the import path and selects `tests/unit_tests/`.

## Locust stress tests

Run the stress scenarios against the same API:

```bash
locust -f tests/stress_tests/locustfile.py
```

Set `BASE_URL` in `tests/.env` or the shell environment before starting Locust. The stress users use the credentials and records expected by the existing test scenarios; run them against a non-production database.
