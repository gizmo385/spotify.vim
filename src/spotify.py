import requests
import vim
import subprocess
import pprint

API_URL = "https://api.spotify.com/v1/search"
TIMEOUT = 10

def search_track():
    # Get the user's input
    vim.command("call inputsave()")
    vim.command("let user_input = inputdialog('Enter your query: ')")
    vim.command("call inputrestore()")
    vim.command("echo '\n'")
    track_name = vim.eval("user_input")

    # Send the request
    request_url = "%s?query=%s&type=track&" % (API_URL, track_name)
    try:
        response_content = requests.get(request_url, timeout = TIMEOUT).json()
    except requests.exceptions.Timeout as Timeout:
        print "Your query timed out!"
        return
    items = response_content["tracks"]["items"]

    items_list = {}
    index = 1
    for item in items:
        print "%d: %s - %s" % (index, item["name"], item["artists"][0]["name"])
        items_list[index] = item
        index += 1

    # Get the selected song
    vim.command("call inputsave()")
    vim.command("let user_input = inputdialog('Select a track number: ')")
    vim.command("call inputrestore()")
    vim.command("echo '\n'")

    try:
        track_num = int(vim.eval("user_input"))
    except:
        print "%s is not a valid selection!" % vim.eval("user_input")
        return

    # Play the track
    selected_item = items_list[track_num]
    print "Playing %s by %s..." % (selected_item["name"], selected_item["artists"][0]["name"])
    play_spotify_track(selected_item["uri"])

def shell_command(*args):
    return subprocess.check_output(list(args))

def spotify_command(command, *args):
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

def play_spotify_track(song_uri):
    """Plays the song that with the provided URI"""
    spotify_command("org.mpris.MediaPlayer2.Player.OpenUri", "string:%s" % song_uri)
