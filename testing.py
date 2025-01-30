import os

import discohook

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
PUBLIC_KEY = os.environ["PUBLIC_KEY"]
APPLICATION_ID = os.environ["APPLICATION_ID"]
APPLICATION_PASSWORD = os.environ["APPLICATION_PASSWORD"]

app = discohook.Client(
    application_id=APPLICATION_ID,
    public_key=PUBLIC_KEY,
    token=DISCORD_TOKEN,
    password=APPLICATION_PASSWORD,  # Must be provided if you want to use the dashboard.
    default_help_command=True,  # This will enable your bot to use  default help command (/help).
)


# Adding a error handler for all interactions
@app.on_interaction_error()
async def handler(i: discohook.Interaction, err: Exception):
    user_response = "Some error occurred! Please contact the developer."
    if i.responded:
        await i.response.followup(user_response, ephemeral=True)
    else:
        await i.response.send(user_response, ephemeral=True)

    await app.send("12345678910", f"Error: {err}")  # send error to a channel in development server


# Adding a error handler for any serverside exception
@app.on_error()
async def handler(_request, err: Exception):
    # request: starlette.requests.Request
    # err is the error object
    await app.send("12345678910", f"Error: {err}")  # send error to a channel in development server
    # If you don't have reference to `app` object, you can use `request.app` to get the app object.


# Note: ApplicationCommand is a decorator factory.
# It will return a decorator which will register the function as a command.
# The decorator for different command types are different and take a different set of arguments.
# If name is not provided, it will use the callback function name as the command name
# If command description is not provided for slash command and function's docstring is not found, it will raise ValueError.


# Making slash command
@app.load
@discohook.command.slash()
async def ping(i: discohook.Interaction):
    """Ping the bot."""
    await i.response.send("Pong!")


# Making user command
@app.load
@discohook.command.user()
async def avatar(i: discohook.Interaction, user: discohook.User):
    embed = discohook.Embed()
    embed.set_image(img=user.avatar.url)
    await i.response.send(embed=embed)


# Making message command
@app.load
@discohook.command.message()
async def quote(i: discohook.Interaction, message: discohook.Message):
    embed = discohook.Embed()
    embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
    embed.description = message.content
    await i.response.send(embed=embed)
