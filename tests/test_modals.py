"""
Tests for Discord modal interactions.
Tests that TitleInputModal preserves tags through the modal flow.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import discord
from ui.modals import TitleInputModal


class TestTitleInputModal:
    """Tests for the TitleInputModal class."""

    @pytest.mark.asyncio
    async def test_modal_initialization_with_tags(
        self, mock_application_context, mock_bot, mock_forum_channel, mock_forum_tags
    ):
        """Test that modal is initialized with applied_tags parameter."""
        selected_tags = [mock_forum_tags[0], mock_forum_tags[1]]

        modal = TitleInputModal(
            ctx=mock_application_context,
            bot=mock_bot,
            channel=mock_forum_channel,
            url="https://example.com",
            message="Test message",
            mention=None,
            additional_mentions=None,
            applied_tags=selected_tags
        )

        assert modal.applied_tags == selected_tags
        assert modal.channel == mock_forum_channel
        assert modal.url == "https://example.com"

    @pytest.mark.asyncio
    async def test_modal_initialization_with_none_tags(
        self, mock_application_context, mock_bot, mock_forum_channel
    ):
        """Test that modal handles None tags correctly."""
        modal = TitleInputModal(
            ctx=mock_application_context,
            bot=mock_bot,
            channel=mock_forum_channel,
            url="https://example.com",
            message="Test message",
            mention=None,
            additional_mentions=None,
            applied_tags=None
        )

        assert modal.applied_tags is None

    @pytest.mark.asyncio
    async def test_modal_initialization_with_empty_tags_list(
        self, mock_application_context, mock_bot, mock_forum_channel
    ):
        """Test that modal handles empty tags list correctly."""
        modal = TitleInputModal(
            ctx=mock_application_context,
            bot=mock_bot,
            channel=mock_forum_channel,
            url="https://example.com",
            message="Test message",
            mention=None,
            additional_mentions=None,
            applied_tags=[]
        )

        assert modal.applied_tags == []

    @pytest.mark.asyncio
    async def test_modal_has_title_input_field(
        self, mock_application_context, mock_bot, mock_forum_channel
    ):
        """Test that modal has a title input field."""
        modal = TitleInputModal(
            ctx=mock_application_context,
            bot=mock_bot,
            channel=mock_forum_channel,
            url="https://example.com",
            message="",
            mention=None,
            additional_mentions=None,
            applied_tags=None
        )

        assert hasattr(modal, 'title_input')
        assert modal.title_input.label == "Post Title:"
        assert modal.title_input.max_length == 100

    @pytest.mark.asyncio
    async def test_modal_callback_passes_tags_to_create_forum_thread(
        self, mock_application_context, mock_bot, mock_forum_channel, mock_forum_tags, mock_interaction
    ):
        """Test that modal callback passes applied_tags to create_forum_thread."""
        selected_tags = [mock_forum_tags[0], mock_forum_tags[2]]  # Bug, Documentation

        modal = TitleInputModal(
            ctx=mock_application_context,
            bot=mock_bot,
            channel=mock_forum_channel,
            url="https://example.com/article",
            message="Test message",
            mention=None,
            additional_mentions=None,
            applied_tags=selected_tags
        )

        # Mock the title input value
        modal.title_input.value = "User Provided Title"

        # Mock create_forum_thread
        with patch('ui.modals.create_forum_thread', new_callable=AsyncMock) as mock_create:
            mock_thread = Mock(spec=discord.Thread)
            mock_thread.jump_url = "https://discord.com/channels/123/456"
            mock_create.return_value = mock_thread

            # Execute callback
            await modal.callback(mock_interaction)

            # Verify create_forum_thread was called with tags
            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["applied_tags"] == selected_tags
            assert call_kwargs["title"] == "User Provided Title"
            assert call_kwargs["url"] == "https://example.com/article"

    @pytest.mark.asyncio
    async def test_modal_callback_handles_none_tags(
        self, mock_application_context, mock_bot, mock_forum_channel, mock_interaction
    ):
        """Test that modal callback handles None tags correctly."""
        modal = TitleInputModal(
            ctx=mock_application_context,
            bot=mock_bot,
            channel=mock_forum_channel,
            url="https://example.com",
            message="",
            mention=None,
            additional_mentions=None,
            applied_tags=None
        )

        modal.title_input.value = "Title From Modal"

        with patch('ui.modals.create_forum_thread', new_callable=AsyncMock) as mock_create:
            mock_thread = Mock(spec=discord.Thread)
            mock_thread.jump_url = "https://discord.com/channels/123/456"
            mock_create.return_value = mock_thread

            await modal.callback(mock_interaction)

            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["applied_tags"] is None

    @pytest.mark.asyncio
    async def test_modal_callback_rejects_empty_title(
        self, mock_application_context, mock_bot, mock_forum_channel, mock_interaction
    ):
        """Test that modal callback rejects empty title input."""
        modal = TitleInputModal(
            ctx=mock_application_context,
            bot=mock_bot,
            channel=mock_forum_channel,
            url="https://example.com",
            message="",
            mention=None,
            additional_mentions=None,
            applied_tags=None
        )

        modal.title_input.value = ""

        with patch('ui.modals.create_forum_thread', new_callable=AsyncMock) as mock_create:
            await modal.callback(mock_interaction)

            # Verify create_forum_thread was NOT called
            mock_create.assert_not_called()

    @pytest.mark.asyncio
    async def test_modal_callback_with_mentions_and_tags(
        self, mock_application_context, mock_bot, mock_forum_channel, mock_forum_tags,
        mock_interaction, mock_user
    ):
        """Test that modal callback handles both mentions and tags together."""
        selected_tags = [mock_forum_tags[1]]  # Feature Request

        additional_users = [mock_user]

        modal = TitleInputModal(
            ctx=mock_application_context,
            bot=mock_bot,
            channel=mock_forum_channel,
            url="https://example.com",
            message="Check this out",
            mention=mock_user,
            additional_mentions=additional_users,
            applied_tags=selected_tags
        )

        modal.title_input.value = "Feature Suggestion"

        with patch('ui.modals.create_forum_thread', new_callable=AsyncMock) as mock_create:
            mock_thread = Mock(spec=discord.Thread)
            mock_thread.jump_url = "https://discord.com/channels/123/456"
            mock_create.return_value = mock_thread

            await modal.callback(mock_interaction)

            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["applied_tags"] == selected_tags
            assert call_kwargs["mention"] == mock_user
            assert call_kwargs["additional_mentions"] == additional_users

    @pytest.mark.asyncio
    async def test_modal_callback_handles_forbidden_exception(
        self, mock_application_context, mock_bot, mock_forum_channel, mock_interaction
    ):
        """Test that modal callback handles Forbidden exceptions properly."""
        modal = TitleInputModal(
            ctx=mock_application_context,
            bot=mock_bot,
            channel=mock_forum_channel,
            url="https://example.com",
            message="",
            mention=None,
            additional_mentions=None,
            applied_tags=None
        )

        modal.title_input.value = "Valid Title"

        with patch('ui.modals.create_forum_thread', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = discord.Forbidden(
                response=Mock(), message="Missing permissions"
            )

            # Should not raise, but handle gracefully
            await modal.callback(mock_interaction)

            # Verify create_forum_thread was called
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_modal_callback_handles_general_exception(
        self, mock_application_context, mock_bot, mock_forum_channel, mock_interaction
    ):
        """Test that modal callback handles general exceptions properly."""
        modal = TitleInputModal(
            ctx=mock_application_context,
            bot=mock_bot,
            channel=mock_forum_channel,
            url="https://example.com",
            message="",
            mention=None,
            additional_mentions=None,
            applied_tags=None
        )

        modal.title_input.value = "Valid Title"

        with patch('ui.modals.create_forum_thread', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = Exception("Unexpected error")

            # Should not raise, but handle gracefully
            await modal.callback(mock_interaction)

            # Verify create_forum_thread was called
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_modal_preserves_all_context_attributes(
        self, mock_application_context, mock_bot, mock_forum_channel, mock_forum_tags, mock_user
    ):
        """Test that modal preserves all initialization attributes."""
        selected_tags = [mock_forum_tags[0]]

        modal = TitleInputModal(
            ctx=mock_application_context,
            bot=mock_bot,
            channel=mock_forum_channel,
            url="https://test.example.com/page",
            message="Custom message body",
            mention=mock_user,
            additional_mentions=[mock_user],
            applied_tags=selected_tags
        )

        assert modal.ctx == mock_application_context
        assert modal.bot == mock_bot
        assert modal.channel == mock_forum_channel
        assert modal.url == "https://test.example.com/page"
        assert modal.message == "Custom message body"
        assert modal.mention == mock_user
        assert modal.additional_mentions == [mock_user]
        assert modal.applied_tags == selected_tags
