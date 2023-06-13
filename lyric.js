const {lyric, search} = require('NeteaseCloudMusicApi');
const songName = process.argv[2];
const artist = process.argv[3];
const album = process.argv[4];
const song = {name: songName, artist: artist, album: album}

normalizeString = function(str) {
  return str.replace(/[\(\)\[\]\/!?@#￥%…&*・]/g, ' ')
            .replace(/\s+/g, ' ');
};

isSubstring = function(string1, string2) {
  return string1.includes(string2) || string2.includes(string1);
};

searchSong = function(keywords, limit, callback) {
  search({
    keywords: keywords,
    type: 1,
    limit: limit, 
  }).then(response => {
    let data = response.body;
    if (data.code == 200) {
      callback && callback(data);
    }   
  }).catch(error => {
    console.error(error);
    callback && callback([]);
  });
};

getSongId = function(song, callback) {
  let songName = normalizeString(song.name);
  let keyword = songName + ' ' +
                song.artist.split('/')[0];
  var sameSong = [];
  searchSong(keyword, 50, (data) => {
    if (!data.result.hasOwnProperty('songs')) {
      callback && callback(-1);
    } else {
      let songs = data.result.songs;
      
      for (const item of songs) {
        let itemName = normalizeString(item.name);
        if (isSubstring(itemName, songName)) {
          sameSong = item;
          break;
        }
      }

      for (const item of songs) {
        let itemName = normalizeString(item.name);
        if (itemName == songName) {
          sameSong = item;
          break;
        }
      }

      for (const item of songs) {
        let itemName = normalizeString(item.name);
        if (isSubstring(itemName, songName) &&
            item.artists[0].name == song.artist.split('/')[0]) {
          sameSong = item;
          break;
        }
      }

      for (const item of songs) {
        let itemName = normalizeString(item.name);
        if (itemName == songName &&
            item.artists[0].name == song.artist.split('/')[0]) {
          sameSong = item;
          break;
        }
      }

      for (const item of songs) {
        if (item.name == song.name &&
            item.artists[0].name == song.artist.split('/')[0]) {
          sameSong = item;
          break;
        }
      }

      for (const item of songs) {
        if (item.name == song.name &&
            item.artists[0].name == song.artist.split('/')[0] &&
            isSubstring(item.album.name, song.album)) {
          sameSong = item;
          break;
        }
      }
      
      for (const item of songs) {
        if (item.name == song.name &&
            item.artists[0].name == song.artist.split('/')[0] &&
            item.album.name == song.album) {
          sameSong = item;
          break;
        }
      }
      
      if (sameSong.length != 0) {
        callback && callback(sameSong);
      } else {
        callback && callback(-1);
      }
    }
  });    
};

getLyric = function (song, callback) {
  let name = song.name;
  let artist = song.artist.split('/')[0];
  getSongId(song, (data) => {
    const noLyric = '[00:01.00]' + name + '\n' +
                    '[00:02.00]' + artist + '\n' +
                    '[00:03.00]暂无歌词，请欣赏。\n' +
                    '[99:00.00]Lyrics not available, please enjoy the music.\n';
    if (data == -1) {
      callback && callback(noLyric);
    } else {
      let songId = data.id;
      lyric({id : songId}).then(response => {
        let data = response.body;
        if (data.code == 200) {
          let lyric = data.lrc.lyric;
          lyric = '[00:00.00]' + name + '\n' + lyric;
          callback && callback(lyric);
        }
      }).catch(error => {
        console.error(error);
        callback && callback(noLyric);
      });
    }
  });
};

getLyric(song, (res) => {
  console.log(res);
});

