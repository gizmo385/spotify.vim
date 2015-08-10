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
command! Track              exec 'python search_spotify(type="track")'
command! Album              exec 'python search_spotify(type="album")'
command! Artist             exec 'python search_spotify(type="artist")'
command! NextSong           exec 'python adapter.next_track()'
command! PreviousSong       exec 'python adapter.previous_track()'
command! PauseUnpause       exec 'python adapter.pause_unpause()'
command! CurrentTrack       exec 'python adapter.print_current_track()'
