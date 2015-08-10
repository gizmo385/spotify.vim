from __future__ import unicode_literals
import requests
import vim
import subprocess
import json

from sys import platform, exit

# Spotify API Information
SEARCH_API_URL = "https://api.spotify.com/v1/search"
TIMEOUT = 10

# Handles communication using the proper mechanism for the operating system
adapter = None


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
        response_content = requests.get(request_url, timeout=TIMEOUT).text
        response_content = response_content.encode("ascii", "ignore")
        response_content = json.loads(response_content)
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
    # vim.command("redraw!")
    adapter.play_uri('"{item}"'.format(item=selected_item["uri"]))


def _parse_tracks(tracks):
    for track_number, track in enumerate(tracks):
        status = "{number}: {name} - {artist}"
        artist_name = track["artists"][0]["name"]

        message = status.format(number=track_number, name=track["name"],
                                artist=artist_name)

        print message


def _parse_artists(artists):
    for artist_number, artist in enumerate(artists):
        status = "{number}: {artist}"
        print "%d: %s" % (artist_number, artist["name"])


def _parse_albums(albums):
    for album_number, album in enumerate(albums):
        status = "{number}: {album}"
        print "%d: %s" % (album_number, album["name"])


def shell_command(*args):
    command = shlex.split(" ".join(args).strip())
    p = subprocess.Popen(command, stdout=subprocess.PIPE)

    response = p.communicate()[0].strip()
    return response.encode("ascii", "ignore").strip()


# This will be removed
def dbus_command(command, *args):
    args = list(args)
    args.append(">/dev/null")
    x = shell_command("dbus-send", "--dest=org.mpris.MediaPlayer2.spotify",
                      "--print-reply", "/org/mpris/MediaPlayer2", command,
                      *args)


class SpotifyAdapter(object):

    def play_track(self, track_name):
        error = "Must be implemented by subclass of {cls}"
        raise NotImplementedError(error.format(cls=self.__class__.__name__))

    def play_album(self, album_name):
        error = "Must be implemented by subclass of {cls}"
        raise NotImplementedError(error.format(cls=self.__class__.__name__))

    def play_artist(self, artist_name):
        error = "Must be implemented by subclass of {cls}"
        raise NotImplementedError(error.format(cls=self.__class__.__name__))

    def print_current_track(self):
        error = "Must be implemented by subclass of {cls}"
        raise NotImplementedError(error.format(cls=self.__class__.__name__))


class OsascriptAdapter(SpotifyAdapter):
    # Commands to send
    PLAY_URI = "play track"
    NEXT_SONG = "next track"
    PREVIOUS_SONG = "previous track"
    PLAY_PAUSE = "playpause"
    CURRENT_SONG = "name of current track"
    CURRENT_ARTIST = "artist of current track"
    CURRENT_ALBUM = "album of current track"

    def __init__(self):
        super(OsascriptAdapter, self).__init__()

    def _send_command(self, command, *args):
        command_string = "'tell application \"Spotify\" to {command}"
        command_string = command_string.format(command=command)

        if args:
            command_string += " {args}".format(args="  ".join(args))
        else:
            command_string += "'"

        return shell_command("osascript", "-e", command_string)

    def print_current_track(self):
        status = "Playing {song} by {artist} on {album}"

        song = self._send_command(OsascriptAdapter.CURRENT_SONG)
        artist = self._send_command(OsascriptAdapter.CURRENT_ARTIST)
        album = self._send_command(OsascriptAdapter.CURRENT_ALBUM)
        vim.command("redraw!")

        print status.format(song=song, artist=artist, album=album)

    def play_uri(self, uri):
        command = "{command} {uri}"
        self._send_command(command.format(command=OsascriptAdapter.PLAY_URI,
                                          uri=uri))
        self.print_current_track()

    def next_track(self):
        self._send_command(OsascriptAdapter.NEXT_SONG)
        self.print_current_track()

    def previous_track(self):
        self._send_command(OsascriptAdapter.PREVIOUS_SONG)
        self.print_current_track()

    def pause_unpause(self):
        self._send_command(OsascriptAdapter.PLAY_PAUSE)


class DbusAdapter(SpotifyAdapter):
    # Commands to send
    PLAY_URI = "org.mpris.MediaPlayer2.Player.OpenUri"
    NEXT_SONG = "org.mpris.MediaPlayer2.Player.Next"
    PREVIOUS_SONG = "org.mpris.MediaPlayer2.Player.Previous"
    PLAY_PAUSE = "org.mpris.MediaPlayer2.Player.PlayPause"

    def __init__(self):
        super(DbusAdapter, self).__init__()

    def current_song():
        pass


# Set the commands based on what platform this is running on
if platform == "win32":  # Windows
    print "This plugin requires OSX or Linux!"
    exit(1)
elif platform == "darwin":  # OSX
    adapter = OsascriptAdapter()
elif platform in ["linux", "linux2"]:  # Linux
    adapter = DbusAdapter()
