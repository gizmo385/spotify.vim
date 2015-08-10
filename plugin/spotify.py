import requests
import vim
import os

from sys import platform, exit

# Spotify API Information
SEARCH_API_URL = "https://api.spotify.com/v1/search"
TIMEOUT = 10

# Command keys
PLAY_URI = "playUri"
NEXT_SONG = "nextSong"
PREVIOUS_SONG = "previousSong"
PLAY_PAUSE = "playPause"

commands = {k: None for k in [PLAY_URI, NEXT_SONG, PREVIOUS_SONG, PLAY_PAUSE]}


def _user_input(message, variable_name):
    try:
        input_command = "let {variable_name} = inputdialog('{message}')"

        vim.command("call inputsave()")
        vim.command(input_command.format(message=message,
                                         variable_name=variable_name))
        vim.command("call inputrestore()")
        vim.command("echo '\n'")
        return vim.eval(variable_name)
    except:
        return None


def search_spotify(type="track"):
    # Get the user's input and script settings
    query = _user_input("Enter the {type} name: ".format(type=type), "query")
    limit = vim.eval("g:spotify_limit")

    if not query:
        return

    # Send the request
    request_url = "{url}?query={query}&type={type}&limit={limit}"
    request_url = request_url.format(url=SEARCH_API_URL, query=query,
                                     type=type, limit=limit)

    try:
        response_content = requests.get(request_url, timeout=TIMEOUT).json()
    except requests.exceptions.Timeout as Timeout:
        print "Your query timed out!"
        return

    item_key = "{type}s".format(type=type)
    items = response_content[item_key]["items"]

    # Print the found results
    if type == "track":
        _parse_tracks(items)
    elif type == "artist":
        _parse_artists(items)
    elif type == "album":
        _parse_albums(items)

    # Get the selected item
    item_num = _user_input("Select a {type} number: ".format(type=type),
                           "item_num")

    if not item_num:
        return

    try:
        item_num = int(item_num)
    except:
        print "%s is not a valid selection!" % vim.eval("user_input")
        return

    # Play the track
    selected_item = items[item_num]
    vim.command("redraw!")
    print "Playing %s" % selected_item["name"]
    play_uri('"{item}"'.format(item=selected_item["uri"]))


def _parse_tracks(tracks):
    for track_number, track in enumerate(tracks):
        status = "{number}: {name} - {artist}"
        artist_name = track["artists"][0]["name"]

        print status.format(number=track_number, name=track["name"],
                            artist=artist_name)


def _parse_artists(artists):
    for artist_number, artist in enumerate(artists):
        print "%d: %s" % (artist_number, artist["name"])


def _parse_albums(albums):
    for album_number, album in enumerate(albums):
        print "%d: %s" % (album_number, album["name"])


def shell_command(*args):
    return os.system(" ".join(args))


def osascript_command(command, *args):
    command_string = "'tell application \"Spotify\" to {command}"
    command_string = command_string.format(command=command)

    if args:
        command_string += " {args}".format(args="  ".join(args))
    else:
        command_string += "'"

    shell_command("osascript", "-e", command_string)


def dbus_command(command, *args):
    args = list(args)
    args.append(">/dev/null")
    x = shell_command("dbus-send", "--dest=org.mpris.MediaPlayer2.spotify",
                      "--print-reply", "/org/mpris/MediaPlayer2", command,
                      *args)


def pause_unpause():
    """Toggles between paused and unpaused"""
    spotify_command(commands[PLAY_PAUSE])


def next_song():
    """Skips to the next track"""
    spotify_command(commands[NEXT_SONG])


def previous_song():
    """Moves to the previous track"""
    spotify_command(commands[PREVIOUS_SONG])


def play_uri(uri):
    """Plays the song that with the provided URI"""
    if platform == "darwin":
        spotify_command(commands[PLAY_URI], uri)
    elif platform in ["linux", "linux2"]:
        spotify_command(commands[PLAY_URI], "string:%s" % uri)
    else:
        print "Your platform is invalid!"
        exit(1)


# Set the commands based on what platform this is running on
if platform == "win32":  # Windows
    print "This plugin requires OSX or Linux!"
    exit(1)

elif platform == "darwin":  # OSX
    commands = {
        PLAY_URI: "play track",
        NEXT_SONG: "next track",
        PREVIOUS_SONG: "previous track",
        PLAY_PAUSE: "playpause"
    }
    spotify_command = osascript_command

elif platform in ["linux", "linux2"]:  # Linux
    commands = {
        PLAY_URI: "org.mpris.MediaPlayer2.Player.OpenUri",
        NEXT_SONG: "org.mpris.MediaPlayer2.Player.Next",
        PREVIOUS_SONG: "org.mpris.MediaPlayer2.Player.Previous",
        PLAY_PAUSE: "org.mpris.MediaPlayer2.Player.PlayPause"
    }
    spotify_command = dbus_command
