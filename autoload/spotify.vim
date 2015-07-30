if !has("python")
    print "You need Python!"
    finish
end

let s:plugin_path = escape(expand('<sfile>:p:h'), '\')
exe 'pyfile ' . s:plugin_path . '/spotify.py'

function! spotify#next_song()
    python next_song()
endfunction

function! spotify#previous_song()
    python previous_song()
endfunction

function! spotify#pause_unpause()
    python pause_unpause()
endfunction

function! spotify#search_track()
    python search_spotify(type = "track")
endfunction

function! spotify#search_album()
    python search_spotify(type = "album")
endfunction

function! spotify#search_artist()
    python search_spotify(type = "artist")
endfunction

" Bindings
command! FindTrack call spotify#search_track()
command! FindAlbum call spotify#search_album()
command! FindArtist call spotify#search_artist()
command! NextSong call spotify#next_song()
command! PreviousSong call spotify#previous_song()
command! PauseUnpause call spotify#pause_unpause()
