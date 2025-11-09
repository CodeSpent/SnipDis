"""
Tests for snip command tag functionality.
Covers tag autocomplete, tag parsing, and tag integration.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import discord
from bot.cogs.snip_cog import SnipCog


class TestTagAutocomplete:
    """Tests for the tag_autocomplete function."""

    @pytest.mark.asyncio
    async def test_autocomplete_returns_all_tags_when_no_input(
        self, mock_bot, mock_autocomplete_context, mock_forum_tags
    ):
        """Test that all available tags are returned when user hasn't typed anything."""
        cog = SnipCog(mock_bot)
        mock_autocomplete_context.value = ""

        choices = await cog.tag_autocomplete(mock_autocomplete_context)

        assert len(choices) == len(mock_forum_tags)
        assert all(isinstance(choice, discord.OptionChoice) for choice in choices)
        assert choices[0].name == "Bug"
        assert choices[0].value == "Bug"

    @pytest.mark.asyncio
    async def test_autocomplete_filters_tags_by_partial_match(
        self, mock_bot, mock_autocomplete_context
    ):
        """Test that tags are filtered by partial match (case-insensitive)."""
        cog = SnipCog(mock_bot)
        mock_autocomplete_context.value = "bug"

        choices = await cog.tag_autocomplete(mock_autocomplete_context)

        assert len(choices) == 1
        assert choices[0].name == "Bug"

    @pytest.mark.asyncio
    async def test_autocomplete_case_insensitive_filtering(
        self, mock_bot, mock_autocomplete_context
    ):
        """Test that filtering is case-insensitive."""
        cog = SnipCog(mock_bot)
        mock_autocomplete_context.value = "FEATURE"

        choices = await cog.tag_autocomplete(mock_autocomplete_context)

        assert len(choices) == 1
        assert choices[0].name == "Feature Request"

    @pytest.mark.asyncio
    async def test_autocomplete_partial_match_in_middle(
        self, mock_bot, mock_autocomplete_context
    ):
        """Test that partial matches work for text in the middle of tag names."""
        cog = SnipCog(mock_bot)
        mock_autocomplete_context.value = "quest"

        choices = await cog.tag_autocomplete(mock_autocomplete_context)

        assert len(choices) == 2  # "Feature Request" and "Question"
        tag_names = [choice.name for choice in choices]
        assert "Feature Request" in tag_names
        assert "Question" in tag_names

    @pytest.mark.asyncio
    async def test_autocomplete_returns_helpful_message_for_non_forum_channel(
        self, mock_bot, mock_autocomplete_context
    ):
        """Test that a helpful message is returned if channel is not a ForumChannel."""
        cog = SnipCog(mock_bot)
        # Replace forum channel with a text channel that lacks available_tags
        text_channel = Mock(spec=discord.TextChannel)
        # Explicitly remove the attribute to trigger AttributeError
        del text_channel.available_tags

        # Update mock_bot to return the text channel
        mock_bot.get_channel = Mock(return_value=text_channel)
        mock_autocomplete_context.options["channel"] = text_channel

        choices = await cog.tag_autocomplete(mock_autocomplete_context)

        assert len(choices) == 1
        assert isinstance(choices[0], discord.OptionChoice)
        assert "not a forum" in choices[0].name.lower()
        assert choices[0].value == ""

    @pytest.mark.asyncio
    async def test_autocomplete_returns_helpful_message_when_no_channel_selected(
        self, mock_bot, mock_autocomplete_context
    ):
        """Test that a helpful message is returned if no channel is selected."""
        cog = SnipCog(mock_bot)
        mock_autocomplete_context.options["channel"] = None

        choices = await cog.tag_autocomplete(mock_autocomplete_context)

        assert len(choices) == 1
        assert isinstance(choices[0], discord.OptionChoice)
        assert "select a channel first" in choices[0].name.lower()
        assert choices[0].value == ""

    @pytest.mark.asyncio
    async def test_autocomplete_handles_channel_with_no_tags(
        self, mock_bot, mock_autocomplete_context, mock_forum_channel_no_tags
    ):
        """Test that autocomplete handles forums with no tags gracefully."""
        cog = SnipCog(mock_bot)
        mock_autocomplete_context.options["channel"] = mock_forum_channel_no_tags

        choices = await cog.tag_autocomplete(mock_autocomplete_context)

        assert len(choices) == 1
        assert isinstance(choices[0], discord.OptionChoice)
        assert "no tags configured" in choices[0].name.lower()
        assert choices[0].value == ""

    @pytest.mark.asyncio
    async def test_autocomplete_limits_to_25_choices(self, mock_bot, mock_autocomplete_context):
        """Test that autocomplete respects Discord's 25 choice limit."""
        cog = SnipCog(mock_bot)

        # Create a forum channel with 30 tags
        channel = Mock(spec=discord.ForumChannel)
        channel.available_tags = []
        for i in range(30):
            tag = Mock(spec=discord.ForumTag)
            tag.id = i
            tag.name = f"Tag{i:02d}"
            channel.available_tags.append(tag)

        mock_autocomplete_context.options["channel"] = channel
        mock_autocomplete_context.value = "tag"  # Matches all tags

        choices = await cog.tag_autocomplete(mock_autocomplete_context)

        assert len(choices) == 25  # Discord limit

    @pytest.mark.asyncio
    async def test_autocomplete_no_match_returns_helpful_message(
        self, mock_bot, mock_autocomplete_context
    ):
        """Test that no matches returns a helpful message."""
        cog = SnipCog(mock_bot)
        mock_autocomplete_context.value = "nonexistent"

        choices = await cog.tag_autocomplete(mock_autocomplete_context)

        assert len(choices) == 1
        assert isinstance(choices[0], discord.OptionChoice)
        assert "no tags match" in choices[0].name.lower()
        assert "nonexistent" in choices[0].name.lower()
        assert choices[0].value == ""

    @pytest.mark.asyncio
    async def test_autocomplete_resolves_channel_from_string_id(
        self, mock_bot, mock_autocomplete_context, mock_forum_tags
    ):
        """Test that autocomplete can resolve channel from string ID."""
        cog = SnipCog(mock_bot)

        # Simulate Discord passing channel as string ID
        mock_autocomplete_context.options["channel"] = "123456789"
        mock_autocomplete_context.value = ""

        choices = await cog.tag_autocomplete(mock_autocomplete_context)

        # Should successfully resolve and return tags
        assert len(choices) == len(mock_forum_tags)
        assert all(isinstance(choice, discord.OptionChoice) for choice in choices)
        # Verify get_channel was called with the correct ID
        mock_bot.get_channel.assert_called_once_with(123456789)


class TestTagParsing:
    """Tests for tag parsing logic in the snip command."""

    def test_parse_single_tag(self, mock_forum_channel):
        """Test parsing a single tag name."""
        tags_string = "Bug"
        tag_names = [tag.strip() for tag in tags_string.split(',') if tag.strip()]

        assert len(tag_names) == 1
        assert tag_names[0] == "Bug"

    def test_parse_multiple_comma_separated_tags(self):
        """Test parsing comma-separated tag names."""
        tags_string = "Bug,Feature Request,Documentation"
        tag_names = [tag.strip() for tag in tags_string.split(',') if tag.strip()]

        assert len(tag_names) == 3
        assert tag_names == ["Bug", "Feature Request", "Documentation"]

    def test_parse_tags_with_whitespace(self):
        """Test that whitespace around tag names is stripped."""
        tags_string = "  Bug  ,  Feature Request  ,  Documentation  "
        tag_names = [tag.strip() for tag in tags_string.split(',') if tag.strip()]

        assert len(tag_names) == 3
        assert tag_names == ["Bug", "Feature Request", "Documentation"]

    def test_parse_empty_string_returns_empty_list(self):
        """Test that empty string returns no tags."""
        tags_string = ""
        tag_names = [tag.strip() for tag in tags_string.split(',') if tag.strip()]

        assert tag_names == []

    def test_parse_only_commas_returns_empty_list(self):
        """Test that string with only commas returns no tags."""
        tags_string = ",,,"
        tag_names = [tag.strip() for tag in tags_string.split(',') if tag.strip()]

        assert tag_names == []

    def test_match_valid_tag_names_to_forum_tags(self, mock_forum_tags):
        """Test matching tag names to actual ForumTag objects."""
        tag_names = ["Bug", "Documentation"]
        applied_tags = []

        for tag_name in tag_names:
            matching_tag = next(
                (tag for tag in mock_forum_tags if tag.name == tag_name), None
            )
            if matching_tag:
                applied_tags.append(matching_tag)

        assert len(applied_tags) == 2
        assert applied_tags[0].name == "Bug"
        assert applied_tags[1].name == "Documentation"

    def test_ignore_invalid_tag_names(self, mock_forum_tags):
        """Test that invalid tag names are ignored."""
        tag_names = ["Bug", "InvalidTag", "Documentation"]
        applied_tags = []

        for tag_name in tag_names:
            matching_tag = next(
                (tag for tag in mock_forum_tags if tag.name == tag_name), None
            )
            if matching_tag:
                applied_tags.append(matching_tag)

        assert len(applied_tags) == 2
        assert all(tag.name in ["Bug", "Documentation"] for tag in applied_tags)

    def test_all_invalid_tags_returns_empty_list(self, mock_forum_tags):
        """Test that all invalid tag names results in empty list."""
        tag_names = ["Invalid1", "Invalid2", "Invalid3"]
        applied_tags = []

        for tag_name in tag_names:
            matching_tag = next(
                (tag for tag in mock_forum_tags if tag.name == tag_name), None
            )
            if matching_tag:
                applied_tags.append(matching_tag)

        assert applied_tags == []


class TestTagIntegration:
    """Tests for tag integration with thread creation."""

    @pytest.mark.asyncio
    async def test_tags_passed_to_create_forum_thread(
        self, mock_forum_channel, mock_forum_tags
    ):
        """Test that parsed tags are passed to create_forum_thread."""
        from services.discord import create_forum_thread

        # Create mock author
        author = Mock(spec=discord.User)
        author.display_name = "Test User"
        author.mention = "<@123>"
        author.avatar = Mock()
        author.avatar.url = "https://example.com/avatar.png"

        # Select subset of tags
        selected_tags = [mock_forum_tags[0], mock_forum_tags[2]]  # Bug, Documentation

        thread = await create_forum_thread(
            channel=mock_forum_channel,
            title="Test Title",
            url="https://example.com",
            message="Test message",
            author=author,
            mention=None,
            additional_mentions=None,
            applied_tags=selected_tags
        )

        # Verify create_thread was called with applied_tags
        mock_forum_channel.create_thread.assert_called_once()
        call_kwargs = mock_forum_channel.create_thread.call_args.kwargs
        assert "applied_tags" in call_kwargs
        assert call_kwargs["applied_tags"] == selected_tags

    @pytest.mark.asyncio
    async def test_none_tags_handled_gracefully(self, mock_forum_channel):
        """Test that None tags are handled gracefully."""
        from services.discord import create_forum_thread

        author = Mock(spec=discord.User)
        author.display_name = "Test User"
        author.mention = "<@123>"
        author.avatar = Mock()
        author.avatar.url = "https://example.com/avatar.png"

        thread = await create_forum_thread(
            channel=mock_forum_channel,
            title="Test Title",
            url="https://example.com",
            message="Test message",
            author=author,
            mention=None,
            additional_mentions=None,
            applied_tags=None
        )

        # Verify create_thread was called with applied_tags=None
        mock_forum_channel.create_thread.assert_called_once()
        call_kwargs = mock_forum_channel.create_thread.call_args.kwargs
        assert "applied_tags" in call_kwargs
        assert call_kwargs["applied_tags"] is None

    @pytest.mark.asyncio
    async def test_empty_tags_list_handled_gracefully(self, mock_forum_channel):
        """Test that empty tags list is handled gracefully."""
        from services.discord import create_forum_thread

        author = Mock(spec=discord.User)
        author.display_name = "Test User"
        author.mention = "<@123>"
        author.avatar = Mock()
        author.avatar.url = "https://example.com/avatar.png"

        thread = await create_forum_thread(
            channel=mock_forum_channel,
            title="Test Title",
            url="https://example.com",
            message="Test message",
            author=author,
            mention=None,
            additional_mentions=None,
            applied_tags=[]
        )

        # Verify create_thread was called
        mock_forum_channel.create_thread.assert_called_once()
