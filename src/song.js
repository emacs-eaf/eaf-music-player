import axios from 'axios';

const HOST = 'http://localhost:';

axios.defaults.withCredentials = true;

const API = {};
API.LYRIC = '/lyric';
API.SEARCH = '/search';
API.SONG = '/song/url';

let Search = {};

Search.search = function(keyword, limit, port, callback) {
  let url = HOST + port + API.SEARCH + '?keywords=' + keyword + '?limit=' + limit + '?type=1';

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

Search.getSongId = function(song, port, callback) {
  let keyword = song.name + ' ' + song.artist.split('/')[0];
  Search.search(keyword, '100', port, (data) => {
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

Search.getLyric = function(song, port, callback) {
  Search.getSongId(song, port, (data) => {
    let songId = data[0].id;
    let url = HOST + port + API.LYRIC + '?id=' + songId;

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

