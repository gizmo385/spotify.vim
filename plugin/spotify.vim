" Ensure that dependencies are satisfied
if !has("python")
    print "You need Python for spotify.vim!"
    finish
end

" Load the python code
let s:plugin_path = escape(expand('<sfile>:p:h'), '\')
exe 'pyfile ' . s:plugin_path . '/spotify.py'

" Script configuration information
let g:spotify_limit = 20

" Bindings
command! SpotifyTrack              exec 'python search_spotify(type = "track")'
command! SpotifyAlbum              exec 'python search_spotify(type = "album")'
command! SpotifyArtist             exec 'python search_spotify(type = "artist")'
command! SpotifyNextSong           exec 'python next_song()'
command! SpotifyPreviousSong       exec 'python previous_song()'
command! SpotifyPauseUnpause       exec 'python pause_unpause()'
