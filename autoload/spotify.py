import requests
import vim
import subprocess
import pprint

API_URL = "https://api.spotify.com/v1/search"
TIMEOUT = 10

def _user_input(message, variable_name):
    input_command = "let {variable_name} = inputdialog('{message}')"

    vim.command("call inputsave()")
    vim.command(input_command.format(message = message, variable_name = variable_name))
    vim.command("call inputrestore()")
    vim.command("echo '\n'")
    return vim.eval(variable_name)

def search_spotify(type="track", limit=20):
    # Get the user's input
    track_name = _user_input("Enter the {type} name: ".format(type=type), "track_name")

    # Send the request
    request_url = "{url}?query={query}&type={type}&limit={limit}"
    request_url = request_url.format(url=API_URL, query=track_name, type=type, limit=limit)

    try:
        response_content = requests.get(request_url, timeout = TIMEOUT).json()
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
    item_num = _user_input("Select a {type} number: ".format(type = type), "item_num")

    try:
        item_num = int(item_num)
    except:
        print "%s is not a valid selection!" % vim.eval("user_input")
        return

    # Play the track
    selected_item = items[item_num]
    print "Playing %s" % selected_item["name"]
    play_uri(selected_item["uri"])

def _parse_tracks(tracks):
    for track_number, track in enumerate(tracks):
        print "%d: %s - %s" % (track_number, track["name"], track["artists"][0]["name"])

def _parse_artists(artists):
    for artist_number, artist in enumerate(artists):
        print "%d: %s" % (artist_number, artist["name"])

def _parse_albums(albums):
    for album_number, album in enumerate(albums):
        print "%d: %s" % (album_number, album["name"])

def shell_command(*args):
    return subprocess.check_output(list(args))

def spotify_command(command, *args):
    print "dbus-send --dest=org.mpris.MediaPlayer2.spotify --print-reply /org/mpris/MediaPlayer2 %s %s" % (command, " ".join(args))
    x = shell_command("dbus-send",
            "--dest=org.mpris.MediaPlayer2.spotify",
            "--print-reply",
            "/org/mpris/MediaPlayer2",
            command,
            *args)

def pause_unpause():
    """Toggles between paused and unpaused"""
    spotify_command("org.mpris.MediaPlayer2.Player.PlayPause")

def next_song():
    """Skips to the next track"""
    spotify_command("org.mpris.MediaPlayer2.Player.Next")

def previous_song():
    """Moves to the previous track"""
    spotify_command("org.mpris.MediaPlayer2.Player.Previous")

def play_uri(uri):
    """Plays the song that with the provided URI"""
    spotify_command("org.mpris.MediaPlayer2.Player.OpenUri", "string:%s" % uri)
