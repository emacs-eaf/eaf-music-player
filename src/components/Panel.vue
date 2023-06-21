<template>
  <div
    class="panel"
    :style="{ 'background': backgroundColor }">
    <div class="coverBox">
      <img
        v-if="currentCover !== ''"
        class="cover"
        :src="currentCover"/>
    </div>
    <div
      class="info"
      :style="{ 'color': foregroundColor }">
      <div>
        {{ trackName }}
      </div>
      <div>
        {{ trackArtist }}
      </div>
    </div>
    <div
      class="control"
      :style="{ 'color': foregroundColor }">
      <img
        class="repeat"
        :style="{ 'color': foregroundColor }"
        :src="fileIconPath(playOrderIcon)"
        @click="togglePlayOrder"
      />
      <img
        class="backward"
        :style="{ 'color': foregroundColor }"
        :src="fileIconPath(stepBackwardIcon)"
        @click="playPrev"
      />
      <img
        class="play"
        :style="{ 'color': foregroundColor }"
        :src="fileIconPath(playIcon)"
        @click="togglePlayStatus"
      />
      <img
        class="forward"
        :style="{ 'color': foregroundColor }"
        :src="fileIconPath(stepForwardIcon)"
        @click="playNext"
      />
      <div class="current-time">
        {{ currentTime }}
      </div>
      /
      <div class="duration">
        {{ duration }}
      </div>
    </div>
    <div class="visual">
      <audio id="audio" ref="player">
        <source :src="audioSource">
      </audio>
      <div id="audio-visual">
      </div>
    </div>
  </div>
</template>

<script>
 import { mapState, mapGetters } from "vuex";
 import AudioMotionAnalyzer from 'audiomotion-analyzer';

 export default {
   name: 'Panel',
   data() {
     return {
       audioSource: "",
       currentTime: "",
       currentCover: "",
       iconCacheDir: "",
       coverCacheDir: "",
       pathSep: "",
       duration: "",
       backgroundColor: "",
       foregroundColor: "",
       /* Download icon from https://www.iconfont.cn/collections/detail?spm=a313x.7781069.0.da5a778a4&cid=18739 */
       stepBackwardIcon: "step-backward",
       stepForwardIcon: "step-forward",
       playIcon: "play-circle",
       playOrderIcon: "list",
       iconKey: 1,
       audioMotion: Object,
     }
   },
   computed: {
     ...mapState([
       "trackName",
       "trackArtist",
       "playSource",
       "displaySource",
       "localCurrentTrackIndex",
       "localTrackInfos",
       "cloudCurrentTrackIndex",
       "cloudTrackInfos",
     ]),
     ...mapGetters([
       "currentPlayTrackKey",
       "isLocalPlaySource",
     ])
   },
   watch: {
     localTrackInfos: function() {
       if (this.playOrderIcon === "random") {
         this.playRandom();
       } else {
         if (this.$refs.player.paused) {
           this.playTrack(this.localCurrentTrackIndex);
         }
       }
     },
     currentTime: function(newVal) {
       this.$emit('getCurrentTime', newVal);
     }
   },
   mounted() {
     window.initPanel = this.initPanel;
     window.forward = this.forward;
     window.backward = this.backward;
     window.playNext = () => {
       this.$store.commit('setPlaySource', this.displaySource);
       this.playNext();
     };
     window.playPrev = () => {
       this.$store.commit('setPlaySource', this.displaySource);
       this.playPrev();
     };
     window.playRandom = () => {
       this.$store.commit('setPlaySource', this.displaySource);
       this.playRandom();
     };
     window.togglePlayStatus = this.togglePlayStatus;
     window.togglePlayOrder = this.togglePlayOrder;
     window.updateCover = this.updateCover;
     window.updateLyric = this.updateLyric;
     window.updateLyricColor = this.updateLyricColor;
     window.setAudioMotion = this.setAudioMotion;

     // cloud
     window.cloudUpdateTrackInfos = this.cloudUpdateTrackInfos;
     window.cloudUpdateLoginState = this.cloudUpdateLoginState;
     window.cloudUpdateLoginQr = this.cloudUpdateLoginQr;
     window.cloudUpdateTrackAudioSource = this.cloudUpdateTrackAudioSource;

     this.audioMotion = new AudioMotionAnalyzer(
       document.getElementById('audio-visual'),
       {
         source: document.getElementById('audio')
       }
     )

     this.$root.$on("playTrack", this.playTrack);
     let that = this;
     this.$refs.player.addEventListener("ended", this.handlePlayFinish);
     this.$refs.player.addEventListener('timeupdate', () => {
       that.currentTime = that.formatTime(that.$refs.player.currentTime);
       that.duration = that.formatTime(that.$refs.player.duration);
     });

   },
   methods: {
     updateCover(url) {
       var dynamicallyId = new Date();
       var src = url + "?cache=" + dynamicallyId;
       this.currentCover = src;
       this.$store.commit("updateCover", src);
     },

     updateLyricColor(color) {
       this.$store.commit("updateLyricColor", color);
     },

     updateLyric(lyric) {
       lyric = decodeURIComponent(escape(window.atob(lyric)))
       let lines = lyric.split('\n');
       let newLyric = [];
       lines.forEach((line, index) => {
         let newLine = {};
         if (!line) {
           return ;
         }
         let pattern = /\[\S*\]/g;
         let time = line.match(pattern)[0];
         let lineLyric = line.replace(time, '');
         time = time.replace(/\[/, '');
         time = time.replace(/\]/, '');
         newLine.index = index;
         newLine.time = time;
         newLine.content = lineLyric.trim();
         if (newLine.content == '') {
           newLine.content = "~";
         }
         newLine.second = (time.split(":")[0] * 60 + parseFloat(time.split(":")[1])).toFixed(0);
         newLyric.push(newLine);
       })
       this.$store.commit("updateLyric", newLyric);
     },

     setAudioMotion(colorList) {
       if (colorList.length === 0) {
         colorList = [this.foregroundColor];
       }

       const options = {
         bgColor: '#011a35', // background color (optional) - defaults to '#111'
         dir: 'h',           // add this property to create a horizontal gradient (optional)
         colorStops: colorList
       }
       this.audioMotion.registerGradient( 'myGradient', options );

       this.audioMotion.setOptions({
         showBgColor: true,
         overlay: true,
         bgAlpha: 0,
         showScaleX: false,
         gradient: 'myGradient',
         mode: 2
       })

       this.audioMotion.setCanvasSize(460, 88)
     },

     togglePlayOrder() {
       if (this.playOrderIcon === "list") {
         this.playOrderIcon = "random";
       } else if (this.playOrderIcon === "random") {
         this.playOrderIcon = "repeat";
       } else if (this.playOrderIcon === "repeat") {
         this.playOrderIcon = "list";
       }
     },

     handlePlayFinish() {
       if (this.playOrderIcon === "list") {
         this.playNext();
       } else if (this.playOrderIcon === "random") {
         this.playRandom();
       } else if (this.playOrderIcon === "repeat") {
         this.playAgain();
       }
     },

     initPanel(playOrderIcon, backgroundColor, foregroundColor, iconCacheDir, coverCacheDir, pathSep, defaultCoverPath) {
       this.playOrderIcon = playOrderIcon;
       this.backgroundColor = backgroundColor;
       this.foregroundColor = foregroundColor;
       this.iconCacheDir = iconCacheDir;
       this.coverCacheDir = coverCacheDir;
       this.pathSep = pathSep;
       this.currentCover = defaultCoverPath;
       this.iconKey = new Date();
       this.setAudioMotion([this.foregroundColor]);
     },
     
     fileIconPath(iconFile) {
       return this.iconCacheDir + this.pathSep + iconFile + ".svg" + "?cache=" + this.iconKey;
     },

     getBarColors() {
       return [this.backgroundColor, this.foregroundColor, this.foregroundColor]
     },

     formatTime(seconds) {
       if (isNaN(seconds)) {
         return "00:00"
       } else {
         var minutes = Math.floor(seconds / 60);
         minutes = (minutes >= 10) ? minutes : "0" + minutes;
         seconds = Math.floor(seconds % 60);
         seconds = (seconds >= 10) ? seconds : "0" + seconds;
         return minutes + ":" + seconds;
       }
     },

     forward() {
       this.$refs.player.currentTime += 10;
     },

     backward() {
       this.$refs.player.currentTime -= 10;
     },

     togglePlayStatus() {
       if (this.$refs.player.paused) {
         this.$refs.player.play();
         this.playIcon = "pause-circle";
       } else {
         this.$refs.player.pause();
         this.playIcon = "play-circle";
       }
     },

     // player
     playAudioSource(source) {
       if (source) {
         this.audioSource = source;
         this.playIcon = "pause-circle";
         this.$refs.player.load();
         var playPromise = this.$refs.player.play();
         if (playPromise !== undefined) {
           // eslint-disable-next-line no-unused-vars
           playPromise.then(_ => {}).catch(error => {
             console.log(error);
           });
         }
       } else {
         this.$refs.player.pause();
         this.playIcon = "play-circle";
       }
     },
     
     playTrack(index) {
       var track;
       if (this.isLocalPlaySource) {
         track = this.localTrackInfos[index];
         this.$store.commit('updateLocalCurrentTrackIndex', index);
       } else {
         track = this.cloudTrackInfos[index];
         this.$store.commit('updateCloudCurrentTrackIndex', index);
       }
       this.$store.commit('updatePlayTrackInfo', track);

       this.currentCover = "";
       window.pyobject.vue_update_current_track(this.playSource,
                                                this.currentPlayTrackKey);
       this.playAudioSource(track.path);

     },

     playPrev() {
       var currentIndex;
       var total;
       if (this.isLocalPlaySource) {
         currentIndex = this.localCurrentTrackIndex;
         total = this.localTrackInfos.length;
       } else {
         currentIndex = this.cloudCurrentTrackIndex;
         total = this.cloudTrackInfos.length;
       }
       if (currentIndex > 0) {
         currentIndex -= 1;
       } else {
         currentIndex = total -1;
       }
       this.playTrack(currentIndex);
     },

     playNext() {
       var currentIndex;
       var total;
       if (this.isLocalPlaySource) {
         currentIndex = this.localCurrentTrackIndex;
         total = this.localTrackInfos.length;
       } else {
         currentIndex = this.cloudCurrentTrackIndex;
         total = this.cloudTrackInfos.length;
       }
       if (currentIndex < total - 1) {
         currentIndex += 1;
       } else {
         currentIndex = 0;
       }
       this.playTrack(currentIndex);
     },

     playRandom() {
       var total;
       if (this.isLocalPlaySource) {
         total = this.localTrackInfos.length;
       } else {
         total = this.cloudTrackInfos.length;
       }
       var min = 0;
       var max = total;
       var randomIndex = Math.floor(Math.random() * (max - min + 1)) + min;
       this.playTrack(randomIndex);
     },

     playAgain() {
       var currentIndex;
       if (this.isLocalPlaySource) {
         currentIndex = this.localCurrentTrackIndex;
       } else {
         currentIndex = this.cloudCurrentTrackIndex;
       }
       this.playTrack(currentIndex);
     },

     cloudUpdateTrackInfos(track_infos) {
       this.$store.commit("updateCloudTrackInfos", track_infos);
     },

     cloudUpdateLoginQr(val) {
       this.$store.commit("updateCloudLoginQr", val.qrcode);
     },

     cloudUpdateLoginState(val) {
       this.$store.commit("updateCloudLoginState", val);
     },

     cloudUpdateTrackAudioSource(val) {
       if (val) {
         this.playAudioSource(val);
       } else {
         this.playNext();
       }
     }
   }
 }
</script>

<style scoped>
 .panel {
   position: absolute;
   bottom: 0;

   width: 100%;

   box-shadow: 0px -4px 3px rgba(30, 30, 30, 0.2);

   display: flex;
   flex-direction: row;
   align-items: center;

   padding-left: 20px;
   padding-right: 20px;
 }

 .coverBox {
   width: 60px;
   margin: 0;
   margin-right: 20px;
 }
 
 .cover {
   width: 100%;
 }

 .info {
   width: 30%;
   user-select: none;
   overflow: hidden;
   white-space: nowrap;
   text-overflow: ellipsis;
   margin: 0;
 }

 .control {
   display: flex;
   flex-direction: row;
   align-items: center;
   justify-content: center;
 }

 .visual {
   height: 100%;
   margin: 0;
   margin-left: 20px;
   width: 30%;
 }

 .backward {
   cursor: pointer;
   height: 48px;
 }

 .forward {
   cursor: pointer;
   height: 48px;
 }

 .play {
   margin-left: 10px;
   margin-right: 10px;
   cursor: pointer;
   height: 60px;
 }

 .play-order {
   margin-right: 20px;
   height: 60px;
 }

 .repeat {
   margin-right: 20px;
   height: 24px;
 }
 
 .current-time {
   margin-left: 20px;
   margin-right: 5px;
 }

 .duration {
   margin-left: 5px;
 }
</style>
