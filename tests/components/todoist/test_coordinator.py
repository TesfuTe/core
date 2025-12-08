"""Tests for the Todoist coordinator."""

from __future__ import annotations

from datetime import timedelta
import logging
from unittest.mock import AsyncMock

import pytest

from homeassistant.components.todoist.coordinator import TodoistCoordinator
from tests.common import MockConfigEntry


# ---------------------------------------------------------------------------
# Helper: build a coordinator with minimal dependencies
# ---------------------------------------------------------------------------


def _make_coordinator(mock_api: AsyncMock) -> TodoistCoordinator:
    """Create a TodoistCoordinator instance for tests."""
    # Dummy hass object – coordinator doesn't use it in _async_update_data
    hass = object()

    # Minimal config entry (same shape as real integration)
    entry = MockConfigEntry(
        domain="todoist",
        data={"token": "fake-token"},
        options={},  # no filters
    )

    logger = logging.getLogger(__name__)

    return TodoistCoordinator(
        hass,
        logger,
        entry,
        timedelta(minutes=1),
        mock_api,
        "fake-token",
    )


@pytest.fixture
def mock_api() -> AsyncMock:
    """Return a mocked Todoist API client."""
    api = AsyncMock()
    api.get_tasks = AsyncMock()
    return api


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_update_data_returns_tasks(mock_api: AsyncMock) -> None:
    """Coordinator should return tasks from the API unchanged."""
    task1 = AsyncMock()
    task2 = AsyncMock()
    mock_api.get_tasks.return_value = [task1, task2]

    coordinator = _make_coordinator(mock_api)

    result = await coordinator._async_update_data()

    assert result == [task1, task2]
    mock_api.get_tasks.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_update_data_raises_update_failed(
    mock_api: AsyncMock,
) -> None:
    """Coordinator should wrap API errors in UpdateFailed."""
    from homeassistant.helpers.update_coordinator import UpdateFailed

    mock_api.get_tasks.side_effect = Exception("API crash!")

    coordinator = _make_coordinator(mock_api)

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
