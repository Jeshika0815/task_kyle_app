"""Tests for the Discord bot's slash-command logic in discord_ver/.

These do not connect to Discord or the real API: `discord.Interaction` is
replaced with a MagicMock, and `httpx.AsyncClient.get`/`post` are patched so
each command's HTTP call returns a canned response.
"""

import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ.setdefault("ENDPOINT", "http://testserver")
os.environ.setdefault("DISCORD_BOT_TOKEN", "test-discord-token")

from discord_ver import main as bot_main  # noqa: E402


class FakeResponse:
    """Minimal stand-in for httpx.Response."""

    def __init__(self, status_code: int = 200, json_data=None):
        self.status_code = status_code
        self._json_data = {} if json_data is None else json_data

    def json(self):
        return self._json_data


def make_interaction(user_id: int = 123) -> MagicMock:
    interaction = MagicMock()
    interaction.user.id = user_id
    interaction.response.send_message = AsyncMock()
    interaction.response.send_modal = AsyncMock()
    return interaction


@pytest.fixture(autouse=True)
def _reset_hold_task():
    bot_main.hold_task = {}
    bot_main.linked_users = {}
    yield
    bot_main.hold_task = {}
    bot_main.linked_users = {}


@pytest.mark.asyncio
async def test_auth_command_opens_login_modal():
    interaction = make_interaction()

    await bot_main.auth.callback(interaction)

    interaction.response.send_modal.assert_called_once()


@pytest.mark.asyncio
async def test_list_command_shows_tasks_on_success():
    interaction = make_interaction()
    fake_tasks = [{"id": 1, "plan_name": "Test Task"}]

    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=FakeResponse(200, fake_tasks))):
        await bot_main.lists.callback(interaction, "fake-api-key")

    interaction.response.send_message.assert_called_once()
    sent_text = interaction.response.send_message.call_args[0][0]
    assert "Test Task" in sent_text


@pytest.mark.asyncio
async def test_list_command_reports_failure_on_error_status():
    interaction = make_interaction()

    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=FakeResponse(401))):
        await bot_main.lists.callback(interaction, "bad-key")

    interaction.response.send_message.assert_called_once_with(
        "予定を取得できませんでした...", ephemeral=True
    )


@pytest.mark.asyncio
async def test_add_command_holds_parsed_task_for_review():
    interaction = make_interaction()
    parsed = {
        "plan_name": "テスト",
        "date": {"start_date": "2026-08-01", "finish_date": None},
        "time": {"start_time": None, "finish_time": None},
    }

    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=FakeResponse(200, parsed))):
        await bot_main.add.callback(interaction, "fake-api-key", "テスト 2026/08/01")

    assert bot_main.hold_task == parsed
    interaction.response.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_add_command_reports_failure_on_error_status():
    interaction = make_interaction()

    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=FakeResponse(500))):
        await bot_main.add.callback(interaction, "fake-api-key", "テスト")

    interaction.response.send_message.assert_called_once_with(
        "予定を作成できませんでした...", ephemeral=True
    )


@pytest.mark.asyncio
async def test_accept_command_posts_held_task_to_task_add():
    interaction = make_interaction()
    bot_main.hold_task = {"plan_name": "テスト"}

    with patch(
        "httpx.AsyncClient.post", new=AsyncMock(return_value=FakeResponse(200, {"id": 1}))
    ) as mock_post:
        await bot_main.accept.callback(interaction, "fake-api-key", "-all")

    mock_post.assert_called_once()
    called_url = mock_post.call_args[0][0]
    assert called_url.endswith("/task/add")
    interaction.response.send_message.assert_called_once_with(
        "全ての予定を登録しました!!", ephemeral=True
    )


@pytest.mark.asyncio
async def test_accept_command_reports_failure_on_error_status():
    interaction = make_interaction()
    bot_main.hold_task = {"plan_name": "テスト"}

    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=FakeResponse(422))):
        await bot_main.accept.callback(interaction, "fake-api-key", "-all")

    interaction.response.send_message.assert_called_once_with(
        "予定を登録できませんでした....", ephemeral=True
    )
