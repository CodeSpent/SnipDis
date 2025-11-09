"""
Tests for Discord service layer functions.
Tests the create_forum_thread function with tag support.
"""
import pytest
from unittest.mock import Mock, AsyncMock
import discord
from services.discord import create_forum_thread


class TestCreateForumThread:
    """Tests for the create_forum_thread service function."""

    @pytest.mark.asyncio
    async def test_create_thread_with_tags(self, mock_forum_channel, mock_forum_tags, mock_thread):
        """Test that create_forum_thread passes applied_tags to channel.create_thread."""
        # Setup
        mock_forum_channel.create_thread.return_value = mock_thread
        mock_thread.send = AsyncMock()

        author = Mock(spec=discord.User)
        author.display_name = "Test Author"
        author.mention = "<@111222333>"
        author.avatar = Mock()
        author.avatar.url = "https://example.com/avatar.png"

        selected_tags = [mock_forum_tags[0], mock_forum_tags[1]]  # Bug, Feature Request

        # Execute
        result = await create_forum_thread(
            channel=mock_forum_channel,
            title="Test Thread Title",
            url="https://example.com/article",
            message="This is a test message",
            author=author,
            mention=None,
            additional_mentions=None,
            applied_tags=selected_tags
        )

        # Verify
        assert result == mock_thread
        mock_forum_channel.create_thread.assert_called_once()

        call_kwargs = mock_forum_channel.create_thread.call_args.kwargs
        assert "applied_tags" in call_kwargs
        assert call_kwargs["applied_tags"] == selected_tags
        assert call_kwargs["name"] == "Test thread title"  # Capitalized

    @pytest.mark.asyncio
    async def test_create_thread_with_none_tags(self, mock_forum_channel, mock_thread):
        """Test that None tags are passed correctly."""
        mock_forum_channel.create_thread.return_value = mock_thread
        mock_thread.send = AsyncMock()

        author = Mock(spec=discord.User)
        author.display_name = "Test Author"
        author.mention = "<@111222333>"
        author.avatar = Mock()
        author.avatar.url = "https://example.com/avatar.png"

        result = await create_forum_thread(
            channel=mock_forum_channel,
            title="Test Thread",
            url="https://example.com",
            message="",
            author=author,
            mention=None,
            additional_mentions=None,
            applied_tags=None
        )

        assert result == mock_thread
        call_kwargs = mock_forum_channel.create_thread.call_args.kwargs
        assert call_kwargs["applied_tags"] is None

    @pytest.mark.asyncio
    async def test_create_thread_with_empty_tags_list(self, mock_forum_channel, mock_thread):
        """Test that empty tags list is converted to None."""
        mock_forum_channel.create_thread.return_value = mock_thread
        mock_thread.send = AsyncMock()

        author = Mock(spec=discord.User)
        author.display_name = "Test Author"
        author.mention = "<@111222333>"
        author.avatar = Mock()
        author.avatar.url = "https://example.com/avatar.png"

        result = await create_forum_thread(
            channel=mock_forum_channel,
            title="Test Thread",
            url="https://example.com",
            message="",
            author=author,
            mention=None,
            additional_mentions=None,
            applied_tags=[]
        )

        assert result == mock_thread
        call_kwargs = mock_forum_channel.create_thread.call_args.kwargs
        # Empty list is converted to None by the function
        assert call_kwargs["applied_tags"] is None

    @pytest.mark.asyncio
    async def test_create_thread_with_single_tag(self, mock_forum_channel, mock_forum_tags, mock_thread):
        """Test that a single tag is passed correctly."""
        mock_forum_channel.create_thread.return_value = mock_thread
        mock_thread.send = AsyncMock()

        author = Mock(spec=discord.User)
        author.display_name = "Test Author"
        author.mention = "<@111222333>"
        author.avatar = Mock()
        author.avatar.url = "https://example.com/avatar.png"

        selected_tags = [mock_forum_tags[0]]  # Just Bug

        result = await create_forum_thread(
            channel=mock_forum_channel,
            title="Bug Report",
            url="https://example.com/bug",
            message="Found a bug",
            author=author,
            mention=None,
            additional_mentions=None,
            applied_tags=selected_tags
        )

        assert result == mock_thread
        call_kwargs = mock_forum_channel.create_thread.call_args.kwargs
        assert len(call_kwargs["applied_tags"]) == 1
        assert call_kwargs["applied_tags"][0].name == "Bug"

    @pytest.mark.asyncio
    async def test_create_thread_with_mentions_and_tags(
        self, mock_forum_channel, mock_forum_tags, mock_thread, mock_user
    ):
        """Test that both mentions and tags work together."""
        mock_forum_channel.create_thread.return_value = mock_thread
        mock_thread.send = AsyncMock()

        author = Mock(spec=discord.User)
        author.display_name = "Test Author"
        author.mention = "<@111222333>"
        author.avatar = Mock()
        author.avatar.url = "https://example.com/avatar.png"

        selected_tags = [mock_forum_tags[0], mock_forum_tags[2]]  # Bug, Documentation

        result = await create_forum_thread(
            channel=mock_forum_channel,
            title="Bug in Docs",
            url="https://example.com/docs-bug",
            message="Documentation has a bug",
            author=author,
            mention=mock_user,
            additional_mentions=None,
            applied_tags=selected_tags
        )

        assert result == mock_thread

        # Verify tags were passed
        call_kwargs = mock_forum_channel.create_thread.call_args.kwargs
        assert call_kwargs["applied_tags"] == selected_tags

        # Verify the temporary mention message was sent and deleted (for notifications)
        assert mock_thread.send.call_count == 2  # Embed + temp mention message

    @pytest.mark.asyncio
    async def test_create_thread_embed_created_correctly(
        self, mock_forum_channel, mock_forum_tags, mock_thread
    ):
        """Test that embed is created with correct information."""
        mock_forum_channel.create_thread.return_value = mock_thread
        mock_thread.send = AsyncMock()

        author = Mock(spec=discord.User)
        author.display_name = "Test Author"
        author.mention = "<@111222333>"
        author.avatar = Mock()
        author.avatar.url = "https://example.com/avatar.png"

        selected_tags = [mock_forum_tags[0]]

        await create_forum_thread(
            channel=mock_forum_channel,
            title="Test Article",
            url="https://example.com/article",
            message="Check this out",
            author=author,
            mention=None,
            additional_mentions=None,
            applied_tags=selected_tags
        )

        # Verify embed was sent
        assert mock_thread.send.called
        send_kwargs = mock_thread.send.call_args.kwargs
        assert "embed" in send_kwargs

    @pytest.mark.asyncio
    async def test_create_thread_raises_exception_on_error(self, mock_forum_channel):
        """Test that exceptions from Discord API are properly raised."""
        mock_forum_channel.create_thread.side_effect = discord.HTTPException(
            response=Mock(), message="Test error"
        )

        author = Mock(spec=discord.User)
        author.display_name = "Test Author"
        author.mention = "<@111222333>"
        author.avatar = Mock()
        author.avatar.url = "https://example.com/avatar.png"

        with pytest.raises(Exception) as exc_info:
            await create_forum_thread(
                channel=mock_forum_channel,
                title="Test",
                url="https://example.com",
                message="",
                author=author,
                mention=None,
                additional_mentions=None,
                applied_tags=None
            )

        assert "Error creating thread" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_thread_content_includes_all_elements(
        self, mock_forum_channel, mock_thread
    ):
        """Test that thread content message includes all expected elements."""
        mock_forum_channel.create_thread.return_value = mock_thread
        mock_thread.send = AsyncMock()

        author = Mock(spec=discord.User)
        author.display_name = "Test Author"
        author.mention = "<@111222333>"
        author.avatar = Mock()
        author.avatar.url = "https://example.com/avatar.png"

        await create_forum_thread(
            channel=mock_forum_channel,
            title="Test Title",
            url="https://example.com/test",
            message="Test message body",
            author=author,
            mention=None,
            additional_mentions=None,
            applied_tags=None
        )

        # Get the content argument from create_thread call
        call_kwargs = mock_forum_channel.create_thread.call_args.kwargs
        content = call_kwargs["content"]

        # Verify content contains expected elements (note: title gets capitalized)
        assert "**Test title**" in content
        assert "Test message body" in content
        assert "https://example.com/test" in content
        assert author.mention in content
