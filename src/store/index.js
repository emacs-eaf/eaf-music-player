import Vue from "vue"
import Vuex from "vuex"

Vue.use(Vuex)

const store = new Vuex.Store({
    state: {
        // settings
        settings: {},

        // local
        localCurrentTrackIndex: -1,
        localNumberWidth: 0,
        localTrackInfos: [],

        // lyric
        currentLyric: "",
        currentCover: "",
        lyricColor: "#CCCCCC",

        // player
        trackName: "",
        trackArtist: "",
        playSource: 'local',

        // cloud
        cloudLoginState: true,
        cloudLoginQr: '',
        cloudCurrentTrackIndex: -1,
        cloudNumberWidth: 0,
        cloudTrackInfos: [],

        // cloud playlists
        cloudPlaylists: [],
        cloudCurrentPlaylistIndex: 0,
        cloudSwitchingPlaylist: false,

        // display
        displaySource: 'local',
    },
    getters: {
        localCurrentTrackPath: state => {
            var track = state.localTrackInfos[state.localCurrentTrackIndex];
            return track.path;
        },
        currentPlayTrackKey: state => {
            if (isLocalSourceType(state.playSource)) {
                return state.localTrackInfos[state.localCurrentTrackIndex].path;
            } else {
                return state.cloudTrackInfos[state.cloudCurrentTrackIndex].id;
            }
        },
        isLocalPlaySource: state => {
            return isLocalSourceType(state.playSource);
        },
        isLocalDisplaySource: state => {
            return isLocalSourceType(state.displaySource);
        }
    },
    mutations: {
        // settings
        updateSettings(state, settings) {
            state.settings = settings;

            // set display source
            state.displaySource = settings.music_source;
            state.playSource = settings.music_source;
        },

        // local
        updateLocalCurrentTrackIndex(state, index) {
            state.localCurrentTrackIndex = index;
        },

        updateLocalTrackInfos(state, infos) {
            state.localTrackInfos = infos;
            state.localNumberWidth = state.localTrackInfos.length.toString().length;

            // load last play track
            if (state.settings.local_track_path) {
                var tracks = state.localTrackInfos.map(function (track) { return track.path });
                state.localCurrentTrackIndex = tracks.indexOf(state.settings.local_track_path);
            }
        },

        updateLocalTrackTagInfo(state, payload) {
            var tracks = state.localTrackInfos.map(function (track) { return track.path });
            var index = tracks.indexOf(payload.track);

            state.localTrackInfos[index].name = payload.name;
            state.localTrackInfos[index].artist = payload.artist;
            state.localTrackInfos[index].album = payload.album;
        },

        // sort
        sortTrackInfos(state, compareType) {
            var isLocal = isLocalSourceType(state.displaySource)
            var trackInfos = null;
            var currentTrack = null;
            if (isLocal) {
                currentTrack = state.localTrackInfos[state.localCurrentTrackIndex];
                trackInfos = state.localTrackInfos;
            } else {
                currentTrack = state.cloudTrackInfos[state.cloudCurrentTrackIndex];
                trackInfos = state.cloudTrackInfos;
            }
            trackInfos.sort(function (a, b) {
                var compareA, compareB;
                if (compareType === "title") {
                    compareA = a.name;
                    compareB = b.name;
                } else if (compareType === "artist") {
                    compareA = a.artist;
                    compareB = b.artist;
                } else if (compareType === "album") {
                    compareA = a.album;
                    compareB = b.album;
                }
                return charCompare(compareA, compareB);
            });

            if (isLocal) {
                state.localTrackInfos = trackInfos;
                state.localCurrentTrackIndex = trackInfos.indexOf(currentTrack);
            } else {
                state.cloudTrackInfos = trackInfos;
                state.cloudCurrentTrackIndex = trackInfos.indexOf(currentTrack);
            }
        },

        // lyric and cover
        updateLyric(state, lyric) {
            state.currentLyric = lyric;
        },
        updateCover(state, url) {
            state.currentCover = url;
        },
        updateLyricColor(state, color) {
            state.lyricColor = color;
        },

        // player
        updatePlayTrackInfo(state, track) {
            state.trackName = track.name
            state.trackArtist = track.artist
        },
        setPlaySource(state, sourceType) {
            state.playSource = sourceType
        },

        // cloud
        updateCloudCurrentTrackIndex(state, index) {
            state.cloudCurrentTrackIndex = index;
        },

        updateCloudTrackInfos(state, infos) {
            var currentTrackId = 0;
            if (state.cloudTrackInfos.length > 0) {
                if (state.cloudCurrentTrackIndex !== -1) {
                    currentTrackId = state.cloudTrackInfos[state.cloudCurrentTrackIndex].id;
                }
            } else {
                // load config
                currentTrackId = state.settings.cloud_track_id;
            }
            state.cloudTrackInfos = infos;
            state.cloudNumberWidth = state.cloudTrackInfos.length.toString().length;

            if (currentTrackId > 0) {
                var trackIds = state.cloudTrackInfos.map(function (track) { return track.id });
                var currentIndex = trackIds.indexOf(currentTrackId)
                if (currentIndex !== -1) {
                    state.cloudCurrentTrackIndex = currentIndex;
                }
            }
        },

        // cloud playlists
        updateCloudPlaylists(state, infos) {
            var currentPlaylistId;
            if (state.cloudPlaylists.length > 0) {
                currentPlaylistId = state.cloudPlaylists[state.cloudCurrentPlaylistIndex].id;
            } else {
                currentPlaylistId = state.settings.cloud_playlist_id;
            }

            state.cloudPlaylists = infos;
            if (currentPlaylistId > 0) {
                var playlistIds = state.cloudPlaylists.map(function (playlist) { return playlist.id });
                var currentIndex = playlistIds.indexOf(currentPlaylistId)
                if (currentIndex !== -1) {
                    state.cloudCurrentPlaylistIndex = currentIndex;
                }
            }
        },

        updateCloudSwitchingPlaylist(state, val) {
            state.cloudSwitchingPlaylist = val;
        },

        updateCloudCurrentPlaylistIndex(state, index) {
            state.cloudCurrentPlaylistIndex = index;
        },

        updateCloudLoginQr(state, val) {
            state.cloudLoginQr = val;
        },
        updateCloudLoginState(state, val) {
            state.cloudLoginState = val;
        },

        // display
        updateDisplaySource(state, val) {
            state.displaySource = val;
        }
    }
})

function charCompare(charA, charB) {
    if (charA === undefined || charA === null || charA === '' || charA === ' ' || charA === '　') {
        return -1;
    }
    if (charB === undefined || charB === null || charB === '' || charB === ' ' || charB === '　') {
        return 1;
    }
    if ((notChinese(charA) && notChinese(charB))) {
        return charA.localeCompare(charB);
    } else if (!notChinese(charA) && !notChinese(charB)){
        return charA .localeCompare(charB, 'zh-Hans-CN', {sensitivity: 'accent'});
    } else {
        if (notChinese(charA)) {
            return -1;
        } else {
            return 1;
        }
    }
}

function notChinese(char) {
    const charCode = char.charCodeAt(0);
    return 0 <= charCode && charCode <= 128;
}

function isLocalSourceType(source) {
    return source === 'local'
}

export default store
