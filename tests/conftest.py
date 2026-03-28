from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

_INITIAL_ACTIVITIES = deepcopy(activities)


def _restore_activities() -> None:
    activities.clear()
    activities.update(deepcopy(_INITIAL_ACTIVITIES))


@pytest.fixture(autouse=True)
def reset_activities_state():
    _restore_activities()
    yield
    _restore_activities()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
