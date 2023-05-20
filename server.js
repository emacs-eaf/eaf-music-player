const WebSocket = require('ws');
const {lyric, search} = require('NeteaseCloudMusicApi');


let handler = null;
let stopFlag = false;
const port = process.argv[2];
const wss = new WebSocket.Server({ port: port });

wss.on('connection', (ws) => {
  console.log('music server connected');
  
  ws.on('message', (message) => {
    message = JSON.parse(message);
    console.log('get message', message);

    if (message === 'stop') {
      stopFlag = true;
    } else {
      handler(message, (output) => {
        ws.send(output);
      });
    }
  });
  
  ws.on('close', () => {
    console.log('music api close');
  });
});

handler = (input, callback) => {
  getLyric(input, (rawLyric) => {
    console.log(rawLyric);
    callback(rawLyric);
  });
};

searchSong = function(keywords, limit, callback) {
  console.log(keywords);
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
  let keyword = song.name + ' ' + song.artist.split('/')[0];
  searchSong(keyword, 100, (data) => {
    let songs = data.result.songs;
    var sameSong = songs.filter((item) => {
      return item.name == song.name &&
             item.artists[0].name == song.artist.split('/')[0];
    });
    if (sameSong.length != 0) {
      callback(sameSong);
    }
  });
};

getLyric = function (song, callback) {
  getSongId(song, (data) => {
    let songId = data[0].id;
    lyric({id : songId}).then(response => {
      let data = response.body;
      if (data.code == 200) {
        let lyric = data.lrc.lyric;
        callback && callback(lyric);
      }
    });
  });
};

