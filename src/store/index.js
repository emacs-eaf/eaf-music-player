import Vue from "vue"
import Vuex from "vuex"

Vue.use(Vuex)

const store = new Vuex.Store({
  state: {
    currentTrack: "",
    currentTrackIndex: 0,
    numberWidth: 0,
    fileInfos: []
  },
  getters: {
    currentTrack: state => {
      return state.currentTrack;
    },
    currentTrackIndex: state => {
      return state.currentTrackIndex;
    },
    fileInfos: state => {
      return state.fileInfos;
    }
  },
  mutations: {
    updateCurrentTrack(state, track) {
      state.currentTrack = track;

      var tracks = state.fileInfos.map(function (track) { return track.path });
      state.currentTrackIndex = tracks.indexOf(state.currentTrack);
    },
    updateFileInfos(state, infos) {
      state.fileInfos = infos;
      state.numberWidth = state.fileInfos.length.toString().length;
    },
    changeSort(state, compareType) {
      var currentSong = state.fileInfos[state.currentTrackIndex];
      state.fileInfos.sort(function (a, b) {
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
      state.currentTrackIndex = state.fileInfos.indexOf(currentSong);
    }
    
  },
  
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

export default store
