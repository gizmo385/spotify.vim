if !has("python")
    print "You need Python!"
    finish
end

pyfile ./src/spotify.py

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
    python search_track()
endfunction

" Bindings
command! FindTrack call spotify#search_track()
command! NextSong call spotify#next_song()
command! PreviousSong call spotify#previous_song()
command! PauseUnpause call spotify#pause_unpause()
