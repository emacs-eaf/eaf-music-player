import Vue from "vue"
import Vuex from "vuex"

Vue.use(Vuex)

const store = new Vuex.Store({
    state: {
        // local
        localCurrentTrackIndex: 0,
        localNumberWidth: 0,
        localTrackInfos: [],

        // lyric
        currentLyric: "",
        currentCover: "",
        lyricColor: "#CCCCCC",

        // player
        playMode: "",
        audioSource: "",
        trackName: "",
        trackArtist: "",
        playSource: 'local',

        // cloud
        cloudLoginState: true,
        cloudLoginQr: '',
        cloudCurrentTrackIndex: 0,
        cloudNumberWidth: 0,
        cloudTrackInfos: [],

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
        // local
        updateLocalCurrentTrackIndex(state, index) {
            state.localCurrentTrackIndex = index;
        },
        updateLocalTrackInfos(state, infos) {
            state.localTrackInfos = infos;
            state.localNumberWidth = state.localTrackInfos.length.toString().length;
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
        playTrack(state, track) {
            if (isLocalSourceType(state.playSource)) {
                state.audioSource = track.path;
            } else {
                state.audioSource = '';
            }
            state.trackName = track.name;
            state.trackArtist = track.artist;
        },
        updateAudioSource(state, source) {
            state.audioSource = source;
        },
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
            state.cloudTrackInfos = infos;
            state.cloudNumberWidth = state.cloudTrackInfos.length.toString().length;
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
    },
    actions: {
        playTrack({commit, state}, index) {
            if (index == -1) {
                return;
            }
            var track;
            if (isLocalSourceType(state.playSource)) {
                track = state.localTrackInfos[index];
                commit('updateLocalCurrentTrackIndex', index);
            } else {
                track = state.cloudTrackInfos[index];
                commit('updateCloudCurrentTrackIndex', index);
            }
            commit('playTrack', track);
        },

        playPrev({dispatch, state}) {
            var currentIndex;
            var total;
            if (isLocalSourceType(state.playSource)) {
                currentIndex = state.localCurrentTrackIndex;
                total = state.localTrackInfos.length;
            } else {
                currentIndex = state.cloudCurrentTrackIndex;
                total = state.cloudTrackInfos.length;
            }
            if (currentIndex > 0) {
                currentIndex -= 1;
            } else {
                currentIndex = total -1;
            }
            dispatch('playTrack', currentIndex);
        },
        playNext({dispatch, state}) {
            var currentIndex;
            var total;
            if (isLocalSourceType(state.playSource)) {
                currentIndex = state.localCurrentTrackIndex;
                total = state.localTrackInfos.length;
            } else {
                currentIndex = state.cloudCurrentTrackIndex;
                total = state.cloudTrackInfos.length;
            }
            if (currentIndex < total - 1) {
                currentIndex += 1;
            } else {
                currentIndex = 0;
            }
            dispatch('playTrack', currentIndex);
        },
        playRandom({dispatch, state}) {
            var total;
            if (isLocalSourceType(state.playSource)) {
                total = state.localTrackInfos.length;
            } else {
                total = state.cloudTrackInfos.length;
            }
            var min = 0;
            var max = total;
            var randomIndex = Math.floor(Math.random() * (max - min + 1)) + min;
            dispatch('playTrack', randomIndex);
        },
        playAgain({dispatch, state}) {
            var currentIndex;
            if (isLocalSourceType(state.playSource)) {
                currentIndex = state.localCurrentTrackIndex;
            } else {
                currentIndex = state.cloudCurrentTrackIndex;
            }
            dispatch('playTrack', currentIndex);
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
