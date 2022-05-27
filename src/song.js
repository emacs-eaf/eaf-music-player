let Search = {};

const {
  song_url,
  lyric,
  search,
} = require('NeteaseCloudMusicApi');

Search.searchSong = async function(keyword, limit, callback) {
  try {
    let result = await search({
      type: '1',
      limit: limit,
      keywords: keyword
    }).then((response) =>{
      let data = response.body;
      if (data.code == 200) {
        callback && callback(data);
      }
    });
  } catch (error) {
      console.log(error);
      callback && callback([]);
  }
};

Search.getSongId = function(song, callback) {
  let keyword = song.name + ' ' + song.artist.split('/')[0];

  searchSong(keyword, '100', (data) => {
    let songs = data.result.songs;
    
    var sameSong = songs.filter((item) => {
      return item.name === song.name &&
             item.artists[0].name === song.artist.split('/')[0];
    });
    if (sameSong.legth != 0) {
      console.log(sameSong.length);
      callback(sameSong);
    }
  });
};

Search.getLyric = async function(song, callback) {
  getSongId(song, async (data) => {
    let songId = data[0].id;
    try {
      let result = await lyric({
        id: songId,
      })
      .then((response) => {
        callback && callback(response);
        console.log(response);
      });
    } catch (error) {
      callback && callback([]);
      console.log(error);
    }
  });
};

export default {
  Search,
};
