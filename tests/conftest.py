"""
Pytest fixtures for Discord bot testing.
Provides mock Discord objects for testing commands, modals, and interactions.
"""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
import discord


@pytest.fixture
def mock_forum_tags():
    """Create a list of mock ForumTag objects for testing."""
    tags = []
    tag_names = ["Bug", "Feature Request", "Documentation", "Question", "Help Wanted"]

    for i, name in enumerate(tag_names):
        tag = Mock(spec=discord.ForumTag)
        tag.id = i + 1
        tag.name = name
        tag.moderated = False
        tag.emoji = None
        tags.append(tag)

    return tags


@pytest.fixture
def mock_forum_channel(mock_forum_tags):
    """Create a mock ForumChannel with available tags."""
    channel = Mock(spec=discord.ForumChannel)
    channel.id = 123456789
    channel.name = "test-forum"
    channel.available_tags = mock_forum_tags
    channel.create_thread = AsyncMock(return_value=Mock(spec=discord.Thread))

    return channel


@pytest.fixture
def mock_forum_channel_no_tags():
    """Create a mock ForumChannel with no tags."""
    channel = Mock(spec=discord.ForumChannel)
    channel.id = 987654321
    channel.name = "forum-no-tags"
    channel.available_tags = []
    channel.create_thread = AsyncMock(return_value=Mock(spec=discord.Thread))

    return channel


@pytest.fixture
def mock_application_context():
    """Create a mock ApplicationContext for slash command testing."""
    ctx = Mock(spec=discord.ApplicationContext)
    ctx.author = Mock(spec=discord.User)
    ctx.author.id = 111222333
    ctx.author.name = "TestUser"
    ctx.author.display_name = "Test User"
    ctx.author.discriminator = "1234"
    ctx.author.mention = "<@111222333>"
    ctx.author.avatar = Mock()
    ctx.author.avatar.url = "https://example.com/avatar.png"

    ctx.guild = Mock(spec=discord.Guild)
    ctx.guild.id = 444555666
    ctx.guild.name = "Test Guild"

    ctx.channel = Mock(spec=discord.TextChannel)
    ctx.channel.id = 777888999
    ctx.channel.name = "test-channel"

    ctx.defer = AsyncMock()
    ctx.respond = AsyncMock()
    ctx.send_modal = AsyncMock()

    return ctx


@pytest.fixture
def mock_autocomplete_context(mock_forum_channel, mock_bot):
    """Create a mock AutocompleteContext for autocomplete testing."""
    ctx = Mock(spec=discord.AutocompleteContext)
    ctx.options = {"channel": mock_forum_channel}
    ctx.value = ""  # Current user input
    ctx.bot = mock_bot

    return ctx


@pytest.fixture
def mock_bot(mock_forum_channel):
    """Create a mock Discord Bot instance."""
    bot = Mock(spec=discord.Bot)
    bot.user = Mock(spec=discord.User)
    bot.user.id = 999888777
    bot.user.name = "TestBot"

    # Mock channel resolution methods
    bot.get_channel = Mock(return_value=mock_forum_channel)
    bot.fetch_channel = AsyncMock(return_value=mock_forum_channel)

    return bot


@pytest.fixture
def mock_interaction():
    """Create a mock Interaction for modal callback testing."""
    interaction = Mock(spec=discord.Interaction)
    interaction.user = Mock(spec=discord.User)
    interaction.user.id = 111222333
    interaction.user.name = "TestUser"
    interaction.user.display_name = "Test User"

    interaction.response = Mock()
    interaction.response.send_message = AsyncMock()
    interaction.followup = Mock()
    interaction.followup.send = AsyncMock()

    return interaction


@pytest.fixture
def mock_thread():
    """Create a mock Thread object."""
    thread = Mock(spec=discord.Thread)
    thread.id = 555666777
    thread.name = "Test Thread"
    thread.jump_url = "https://discord.com/channels/444555666/555666777"
    thread.send = AsyncMock()

    return thread


@pytest.fixture
def sample_tag_names():
    """Provide sample tag names for testing tag parsing."""
    return ["Bug", "Feature Request", "Documentation"]


@pytest.fixture
def mock_user():
    """Create a mock User object."""
    user = Mock(spec=discord.User)
    user.id = 123123123
    user.name = "MentionedUser"
    user.display_name = "Mentioned User"
    user.mention = "<@123123123>"

    return user
