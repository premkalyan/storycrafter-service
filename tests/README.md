# StoryCrafter Test Suite

Automated tests for the StoryCrafter API service.

## Test Structure

```
tests/
├── __init__.py                  # Test package initialization
├── conftest.py                  # Pytest fixtures and configuration
├── test_api_endpoints.py        # API endpoint tests (11 tests)
├── test_generate_epics.json     # Sample data for generate-epics
├── test_generate_stories.json   # Sample data for generate-stories
├── test_regenerate_epic.json    # Sample data for regenerate-epic
├── test_regenerate_story.json   # Sample data for regenerate-story
└── README.md                    # This file
```

## Running Tests

### Automated Tests

Run all automated tests:
```bash
pytest tests/
```

### Run with verbose output
```bash
pytest tests/ -v
```

### Run specific test class
```bash
pytest tests/test_api_endpoints.py::TestGenerateEpicsEndpoint
```

### Run with coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

### Manual API Testing

Use the provided JSON test data for manual API testing:

```bash
# Test generate-epics endpoint
curl -X POST https://storycrafter-service.vercel.app/generate-epics \
  -H "Content-Type: application/json" \
  -d @tests/test_generate_epics.json

# Test generate-stories endpoint
curl -X POST https://storycrafter-service.vercel.app/generate-stories \
  -H "Content-Type: application/json" \
  -d @tests/test_generate_stories.json

# Test regenerate-epic endpoint
curl -X POST https://storycrafter-service.vercel.app/regenerate-epic \
  -H "Content-Type: application/json" \
  -d @tests/test_regenerate_epic.json

# Test regenerate-story endpoint
curl -X POST https://storycrafter-service.vercel.app/regenerate-story \
  -H "Content-Type: application/json" \
  -d @tests/test_regenerate_story.json
```

## Test Coverage

### API Endpoints (11 tests)
- ✅ Health check endpoints (3 tests)
- ✅ `/generate-epics` endpoint (2 tests)
- ✅ `/generate-stories` endpoint (2 tests)
- ✅ `/regenerate-epic` endpoint (2 tests)
- ✅ `/regenerate-story` endpoint (2 tests)

## Continuous Integration

Tests run automatically on:
- Every push to `master`, `main`, or `develop` branches
- Every pull request to these branches
- Multiple Python versions (3.10, 3.11, 3.12)

See `.github/workflows/test.yml` for CI configuration.

## Test Requirements

Test dependencies are in `requirements.txt`:
- `pytest>=8.0.0` - Test framework
- `pytest-asyncio>=0.23.0` - Async test support
- `pytest-mock>=3.12.0` - Mocking utilities
- `httpx>=0.26.0` - HTTP client for FastAPI testing

## Writing New Tests

1. Add test file to `tests/` directory with `test_` prefix
2. Use fixtures from `conftest.py` for common test data
3. Mock external API calls (Anthropic, OpenAI) to avoid costs
4. Follow naming convention: `test_<feature>_<scenario>`

Example:
```python
def test_new_endpoint_success(client, sample_data):
    response = client.post("/new-endpoint", json=sample_data)
    assert response.status_code == 200
```

## Test Philosophy

- **Fast**: Tests run in < 1 second (mocked external calls)
- **Isolated**: No real API calls or external dependencies
- **Comprehensive**: Cover success and failure scenarios
- **Maintainable**: Use fixtures for common test data
