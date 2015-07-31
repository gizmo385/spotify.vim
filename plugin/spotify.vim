" Ensure that dependencies are satisfied
if !has("python")
    print "You need Python!"
    finish
end

" Load the python code
let s:plugin_path = escape(expand('<sfile>:p:h'), '\')
exe 'pyfile ' . s:plugin_path . '/spotify.py'

" Script configuration information
let g:spotify_limit = 20

" Bindings
command! Track              exec 'python search_spotify(type = "track")'
command! Album              exec 'python search_spotify(type = "album")'
command! Artist             exec 'python search_spotify(type = "artist")'
command! NextSong           exec 'python next_song()'
command! PreviousSong       exec 'python previous_song()'
command! PauseUnpause       exec 'python pause_unpause()'
