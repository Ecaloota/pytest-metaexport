# Pytest MetaExport Plugin

This `pytest` plugin allows you to attach custom metadata to your test functions using dynamic decorators, then exports a JSON report and PDF at the end of the test session containing metadata and execution results for all tests.

## Features

- Add arbitrary metadata to test functions using dynamic decorators.
- Collect test outcome data: passed, failed, and skipped.
- Export a full JSON report and PDF summarizing the test run and metadata.
- Track execution duration for each test.

---

## Usage

```bash
pytest --metaexport-json=output.json
```

## Test Definition

```python
import decorators as m

# You can add decorators dynamically
@m.title("Login succeeds with correct credentials")
@m.tags(["auth", "smoke"])
def test_login():
    assert True
```

## Example Output
```json
{
  "run_date": "2025-06-17T14:22:53.439Z",
  "duration_seconds": 1.23,
  "collected": 3,
  "passed": 2,
  "skipped": 1,
  "failed": 0,
  "tests": [
    {
      "nodeid": "test_auth.py::test_login",
      "title": "Login succeeds with correct credentials",
      "tags": ["auth", "smoke"],
      "status": "passed",
      "duration": 0.12
    },
    ...
  ]
}
```