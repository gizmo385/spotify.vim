if (exists('g:spotify_disable') || exists('loaded_spotify') || &cp)
    finish
endif
let loaded_spotify = 1

" Bindings
command! Track              exec 'python search_spotify(type = "track")'
command! Album              exec 'python search_spotify(type = "album")'
command! Artist             exec 'python search_spotify(type = "artist")'
command! NextSong           exec 'python next_song()'
command! PreviousSong       exec 'python previous_song()'
command! PauseUnpause       exec 'python pause_unpause()'
