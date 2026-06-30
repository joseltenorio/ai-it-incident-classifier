# tests/conftest.py

import os

# Tests must not depend on the developer's local .env file.
# The mock provider keeps the test suite deterministic and avoids external
# calls to Gemini API during automated validation.
os.environ["CLASSIFIER_PROVIDER"] = "mock"