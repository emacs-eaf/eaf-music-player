import axios from 'axios';

const HOST = 'https://netease-cloud-music-api-teal-tau.vercel.app';

axios.defaults.withCredentials = true;

const API = {};
API.LYRIC = '/lyric';
API.SEARCH = '/search';
API.SONG = '/song/url';

let Search = {};

Search.search = function(keyword, limit, callback) {
  let url = HOST + API.SEARCH + '?keywords=' + keyword + '?limit=' + limit + '?type=1';

  axios.get(url)
  .then((response) => {
    let data = response.data;
    if (data.code == 200) {
      callback && callback(data);
    }
  })
  .catch((error) => {
    console.log(error);
    callback && callback([]);
  });
};

Search.getSongId = function(song, callback) {
  let keyword = song.name + ' ' + song.artist.split('/')[0];

  Search.search(keyword, '100', (data) => {
    let songs = data.result.songs;
    var sameSong = songs.filter((item) => {
      return item.name === song.name &&
             item.artists[0].name === song.artist.split('/')[0];
    });
    if (sameSong.legth != 0) {
      callback(sameSong);
    }
  });
};

Search.getLyric = function(song, callback) {
  Search.getSongId(song, (data) => {
    let songId = data[0].id;
    let url = HOST + API.LYRIC + '?id=' + songId;

    axios.get(url)
    .then((response) => {
      let data = response.data;
      if (data.code == 200) {
        let lyric = data.lrc.lyric;
        callback && callback(lyric);
      }
    })
    .catch((error) => {
      console.log(error);
      callback && callback([]);
    });
  });
};

export default {
  Search,
};
