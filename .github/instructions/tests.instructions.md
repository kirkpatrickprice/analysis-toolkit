---
applyTo: "tests/**"
---

# GitHub Copilot Instructions for Test Writing

You are a Python testing expert working as a collaborative development partner. Write comprehensive, maintainable tests using Pytest.

## Testing Standards
- Follow Arrange-Act-Assert (AAA) pattern for test structure
- Use descriptive test names that explain the scenario and expected outcome
- Apply Python 3.13+ type hints with modern syntax (`str | None` instead of `Optional[str]`)
- Follow PEP 8 and SOLID principles in test code
- Lint all tests with `uv ruff`
- Validate type hints with `uv mypy`
- Use dependency injection and mocking for external dependencies

## Test Organization Structure
```
tests/
├── unit/           # Fast, isolated tests for individual functions/classes
├── integration/    # Tests for component interactions and data flow
├── e2e/           # End-to-end tests for complete user workflows
└── fixtures/      # Shared test data and reusable fixtures
    ├── __init__.py
    ├── data/      # Static test data files (JSON, CSV, etc.)
    ├── factories/ # Dynamic test data generators
    └── <domain-specific-fixtures>/ # Fixtures required for complex, domain-specific implementations
```

## Pytest Best Practices

### Test Naming Convention
- Use `test_` prefix for test functions
- Format: `test_<action>_<condition>_<expected_result>`
- Examples:
  - `test_calculate_discount_with_valid_coupon_returns_reduced_price`
  - `test_user_login_with_invalid_credentials_raises_authentication_error`

### Test Structure
```python
def test_function_name():
    # Arrange: Set up test data and dependencies
    user = User(email="test@example.com")
    
    # Act: Execute the functionality being tested
    result = user.validate_email()
    
    # Assert: Verify the expected outcome
    assert result is True
```

### Fixture Guidelines
- Place shared fixtures in `fixtures/**/*` files
- Use `@pytest.fixture` with appropriate scope (`function`, `class`, `module`, `session`)
- Prefer factory fixtures for dynamic test data
- Use `autouse=True` sparingly and only when necessary

## Test Types by Directory

### Unit Tests (`tests/unit/`)
- Test individual functions, methods, and classes in isolation
- Mock external dependencies and I/O operations
- Shared mocks will be created in `tests/fixtures` folder
- Focus on edge cases, boundary conditions, and error handling
- Should run in milliseconds and have no external dependencies
- Avoid magic numbers -- use CONSTANTS instead

```python
import pytest
from unittest.mock import Mock, patch
from myapp.calculator import Calculator

# TEST CONSTANTS
RESULT_5 = 5

class TestCalculator:
    def test_add_positive_numbers_returns_sum(self):
        calculator = Calculator()
        result = calculator.add(2, 3)
        assert result == RESULT_5
    
    @pytest.mark.parametrize("a,b,expected", [
        (0, 0, 0),
        (-1, 1, 0),
        (100, -50, 50)
    ])
    def test_add_various_inputs_returns_correct_sum(self, a: int, b: int, expected: int):
        calculator = Calculator()
        result = calculator.add(a, b)
        assert result == expected
```

### Integration Tests (`tests/integration/`)
- Test interactions between components, modules, or services
- Include database operations, API calls, and file I/O
- Use test databases or containers for data persistence
- Focus on data flow and component communication

```python
import pytest
from myapp.database import DatabaseManager
from myapp.user_service import UserService

class TestUserServiceIntegration:
    @pytest.fixture
    def db_manager(self):
        return DatabaseManager(test_database=True)
    
    def test_create_user_persists_to_database(self, db_manager: DatabaseManager):
        user_service = UserService(db_manager)
        
        user_data = {"name": "John Doe", "email": "john@example.com"}
        user_id = user_service.create_user(user_data)
        
        stored_user = db_manager.get_user(user_id)
        assert stored_user["name"] == "John Doe"
        assert stored_user["email"] == "john@example.com"
```

### End-to-End Tests (`tests/e2e/`)
- Test complete user workflows and system behavior
- Include UI interactions, API endpoints, and data persistence
- Use realistic test data and scenarios
- Focus on critical user paths and business requirements

```python
import pytest
import requests
from myapp.test_client import TestClient

class TestUserRegistrationWorkflow:
    @pytest.fixture
    def test_client(self):
        return TestClient()
    
    def test_complete_user_registration_workflow(self, test_client: TestClient):
        # User visits registration page
        response = test_client.get("/register")
        assert response.status_code == 200
        
        # User submits registration form
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        }
        response = test_client.post("/register", json=user_data)
        assert response.status_code == 201
        
        # User receives confirmation email
        # User activates account
        # User can log in successfully
        login_response = test_client.post("/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()
```

### Fixtures (`tests/fixtures/`)
- Organize reusable test data and setup code
- Use factory patterns for generating varied test data
- Include realistic data that represents production scenarios
- Create concern-specific fixtures in their own file -- or package when needed for complexity
    - `tests/fixtures/concern_1.py`
    - `tests/fixtures/complex_concern_1/`
        - `__init__.py`     # Package init and external interface
        - `concern_1.py`    # Concern-specific fixtures...
        - `concern_2.py`    # Concern-specific fixtures...
        - `concern_n.py`    # Concern-specific fixtures...

```python
# tests/fixtures/user_factory.py
import pytest
from faker import Faker
from myapp.models import User

fake = Faker()

@pytest.fixture
def user_factory():
    def _create_user(**kwargs):
        defaults = {
            "name": fake.name(),
            "email": fake.email(),
            "age": fake.random_int(min=18, max=80)
        }
        defaults.update(kwargs)
        return User(**defaults)
    return _create_user

# tests/fixtures/data/sample_users.json
[
    {"name": "Alice Smith", "email": "alice@example.com", "age": 30},
    {"name": "Bob Johnson", "email": "bob@example.com", "age": 25}
]
```

## Testing Patterns

### Parametrized Tests
Use `@pytest.mark.parametrize` for testing multiple input scenarios:

```python
@pytest.mark.parametrize("input_data,expected", [
    ("valid@email.com", True),
    ("invalid-email", False),
    ("", False),
    (None, False)
])
def test_email_validation(input_data: str | None, expected: bool):
    result = validate_email(input_data)
    assert result == expected
```

### Exception Testing
Test error conditions and exception handling:

```python
def test_divide_by_zero_raises_value_error():
    calculator = Calculator()
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calculator.divide(10, 0)
```

### Async Testing
Handle asynchronous code with `pytest-asyncio`:

```python
import pytest

@pytest.mark.asyncio
async def test_async_user_creation():
    user_service = AsyncUserService()
    user_data = {"name": "Test User", "email": "test@example.com"}
    
    user_id = await user_service.create_user(user_data)
    
    assert user_id is not None
    user = await user_service.get_user(user_id)
    assert user["name"] == "Test User"
```

## Mock and Patch Guidelines
- Mock external dependencies (APIs, databases, file systems)
- Use `unittest.mock.patch` for temporarily replacing objects
- Prefer dependency injection over patching when possible
- Verify mock calls with `assert_called_with()` and `call_count`

```python
from unittest.mock import Mock, patch

@patch('myapp.external_api.requests.get')
def test_fetch_user_data_handles_api_failure(mock_get: Mock):
    mock_get.side_effect = requests.RequestException("API unavailable")
    
    with pytest.raises(UserDataError):
        fetch_user_data(user_id=123)
    
    mock_get.assert_called_once_with("https://api.example.com/users/123")
```

## Performance and Reliability
- Keep unit tests under 100ms execution time
- Use `pytest.mark.slow` for longer-running tests
- Implement proper test cleanup with fixtures or `teardown` methods
- Use test markers for categorizing and selective test execution
- Add recommended markers to `pyproject.toml`

## Test Documentation
- Include docstrings for complex test scenarios
- Document test setup requirements and dependencies
- Explain business logic being tested
- Provide examples of expected vs. actual behavior

