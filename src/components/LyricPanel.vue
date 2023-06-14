<template>
  <div ref="lp" class="lp" >
    <img class="cover" :src="currentCover">
    <div class="lyrics-container"
         :style="{ 'color': foregroundColor }">
      <p class="lyric-0 row" :style="{ 'color': lyricColor }"> {{lyric0}} </p>
      <p class="lyric-1 row" :style="{ 'color': lyricColor }"> {{lyric1}} </p>
      <p class="lyric-2 row" :style="{ 'color': lyricColor }"> {{lyric2}} </p>
      <p class="lyric-3 row" :style="{ 'color': lyricColor }"> {{lyric3}} </p>
      <p class="lyric-4 row" :style="{ 'color': lyricColor }"> {{lyric4}} </p>
      <p class="lyric-3 row" :style="{ 'color': lyricColor }"> {{lyric5}} </p>
      <p class="lyric-2 row" :style="{ 'color': lyricColor }"> {{lyric6}} </p>
      <p class="lyric-1 row" :style="{ 'color': lyricColor }"> {{lyric7}} </p>
      <p class="lyric-0 row" :style="{ 'color': lyricColor }"> {{lyric8}} </p>
    </div>
  </div>
</template>

<script>
 import { mapState } from "vuex";
 export default {
   name: 'LyricPanel',
   data() {
     return {
       activeLyricRowIndex: 0,
       backgroundColor1: "",
       lyric0: "",
       lyric1: "",
       lyric2: "",
       lyric3: "",
       lyric4: "",
       lyric5: "",
       lyric6: "",
       lyric7: "",
       lyric8: "",
       showLyric: true,
     }
   },
   computed: {
     ...mapState([
       "currentTrack",
       "currentTrackIndex",
       "numberWidth",
       "fileInfos",
       "currentLyric",
       "currentCover",
       "lyricColor",
     ])
   },
   props: {
     currentTime: String,
     foregroundColor: String,
   },
   watch: {
     currentTime: function(newVal) {
       var activeLyricRows = this.currentLyric.filter((item) => {
         return parseInt(item.second) <= this.parseToSecond(newVal);
       });
       if (activeLyricRows.length <= 0) {
         return ;
       }
       let currentRow = activeLyricRows.pop();
       if (this.activeLyricRowIndex == currentRow.index) {
         return;
       }
       this.activeLyricRowIndex = currentRow.index;
       
       for (let i = -4, j = 0; i <= 4; i ++, j ++ ) {
         let pos = this.activeLyricRowIndex + i;
         if (pos < 0) {
           this["lyric" + j] = "";
         } else {
           this["lyric" + j] = this.currentLyric[pos % this.currentLyric.length].content;
         }
       }
     },
     currentLyric: function() { 
      for(let i = 0; i <= 8; i++) {
        if (i < 4) {
          this["lyric" + i] = ""
        } else {
          this["lyric" + i] = this.currentLyric[i-4] ? this.currentLyric[i-4].content : "";
        }
        
      }
     },
     currentTrack: {
       // eslint-disable-next-line no-unused-vars
       handler: function(val, oldVal) {
         window.pyobject.vue_update_current_track(val);
         this.$root.$emit("currentTrackVisibleInPlayList");
       }
     }
   },
   mounted() {
   },
   methods: {
     parseToSecond(time) {
       let minute = parseInt(time.split(":")[0]) * 60;
       let second = minute + parseInt(time.split(":")[1]);
       return second;
     },
   }
 }
</script>

<style scoped>
 .lp {
   height: 100%;
   width: 100%;
   display: flex;
   white-space: nowrap;
   text-overflow: ellipsis;
   z-index: -2;
   position: relative;
   overflow: hidden;
 }
 .cover {
   filter: blur(45px);
   width: 100%;
   height: 100%;
   opacity: 0.8;
   position: absolute;
   z-index: -1;
   object-fit: cover;
   position: absolute;
   top: 50%;
   left: 50%;
   transform: translate(-50%, -50%);
 }
 .lyrics-container {
   flex-direction: column;
   word-wrap: break-word;
   
   margin: auto;
   z-index: 1;
   
 }
 .row {
   margin-top: 15px;
   margin-bottom: 15px;
   text-align: center;
   width: 1000px;
   white-space: normal;
 }
 .lyric-0 {
   font-size: 30px;
   filter: blur(6px);
 }
 .lyric-1 {
   font-size: 35px;
   filter: blur(4.5px);
 }
 .lyric-2 {
   font-size: 40px;
   filter: blur(3px);
 }
 .lyric-3 {
   font-size: 45px;
   filter: blur(1.5px);
 }
 .lyric-4 {
   font-size: 50px;
   font-weight: bold;
 }
</style>
