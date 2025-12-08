"""DataUpdateCoordinator for the Todoist component."""

from __future__ import annotations

from datetime import timedelta
import logging

from todoist_api_python.api_async import TodoistAPIAsync
from todoist_api_python.models import Label, Project, Section, Task

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)


class TodoistCoordinator(DataUpdateCoordinator[list[Task]]):
    """Coordinator for updating task data from Todoist."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        entry: ConfigEntry | None,
        update_interval: timedelta,
        api: TodoistAPIAsync,
        token: str,
    ) -> None:
        """Initialize the Todoist coordinator."""
        super().__init__(
            hass,
            logger,
            config_entry=entry,
            name="Todoist",
            update_interval=update_interval,
        )

        self.api = api
        self._projects: list[Project] | None = None
        self._labels: list[Label] | None = None
        self.token = token

    async def _async_update_data(self) -> list[Task]:
        """Fetch tasks from Todoist.

        Filtering is handled entirely in the frontend.
        The coordinator always returns the full list of tasks.
        """
        try:
            return await self.api.get_tasks()
        except Exception as err:  # pragma: no cover - defensive
            raise UpdateFailed(f"Error communicating with Todoist API: {err}") from err

    # --------------------------------------------------------------------
    # SUPPORT METHODS
    # --------------------------------------------------------------------

    async def async_get_projects(self) -> list[Project]:
        """Return Todoist projects fetched at most once."""
        if self._projects is None:
            self._projects = await self.api.get_projects()
        return self._projects

    async def async_get_sections(self, project_id: str) -> list[Section]:
        """Return Todoist sections for a given project ID."""
        return await self.api.get_sections(project_id=project_id)

    async def async_get_labels(self) -> list[Label]:
        """Return Todoist labels fetched at most once."""
        if self._labels is None:
            self._labels = await self.api.get_labels()
        return self._labels
