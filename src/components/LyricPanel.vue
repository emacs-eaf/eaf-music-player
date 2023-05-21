<template>
  <div ref="lp" class="lp" >
    <img class="cover" :src="currentCover">
    <div class="lyrics-container"
         :style="{ 'color': foregroundColor }">
      <p class="lyric-0 row" :style="{...lyricStyleIn, ...lyricStyleOut}"> {{lyric0}} </p>
      <p class="lyric-1 row" :style="{...lyricStyleIn, ...lyricStyleOut}"> {{lyric1}} </p>
      <p class="lyric-2 row" :style="{...lyricStyleIn, ...lyricStyleOut}"> {{lyric2}} </p>
      <p class="lyric-3 row" :style="{...lyricStyleIn, ...lyricStyleOut}"> {{lyric3}} </p>
      <p class="lyric-4 row" > {{lyric4}} </p>
      <p class="lyric-3 row" :style="{...lyricStyleIn, ...lyricStyleOut}"> {{lyric5}} </p>
      <p class="lyric-2 row" :style="{...lyricStyleIn, ...lyricStyleOut}"> {{lyric6}} </p>
      <p class="lyric-1 row" :style="{...lyricStyleIn, ...lyricStyleOut}"> {{lyric7}} </p>
      <p class="lyric-0 row" :style="{...lyricStyleIn, ...lyricStyleOut}"> {{lyric8}} </p>
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
       "currentCover"
     ]), 
     lyricStyleOut() {
       return {
         opacity: this.showLyric ? 1 : 0,
         transition: 'opacity 1.1s ease-in-out',
       };
     },
     lyricStyleIn() {
       return {
         opacity: this.showLyric ? 0 : 1,
         transition: 'opacity 0.4s ease-in-out',
       };
     },
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
       
       this.showLyric = !this.showLyric;
       setTimeout(() => {
         this.lyric0 = this.lyric1;
         this.lyric1 = this.lyric2;
         this.lyric2 = this.lyric3;
         this.lyric3 = this.lyric4;
         this.lyric4 = this.currentLyric[this.activeLyricRowIndex].content;
         this.lyric5 = this.currentLyric[(this.activeLyricRowIndex + 1) % this.currentLyric.length].content;
         this.lyric6 = this.currentLyric[(this.activeLyricRowIndex + 2) % this.currentLyric.length].content;
         this.lyric7 = this.currentLyric[(this.activeLyricRowIndex + 3) % this.currentLyric.length].content;
         this.lyric8 = this.currentLyric[(this.activeLyricRowIndex + 4) % this.currentLyric.length].content;
         this.showLyric = !this.showLyric;
       }, 800);
     },
     currentLyric: function() {
       this.lyric0 = "";
       this.lyric1 = "";
       this.lyric2 = "";
       this.lyric3 = "";
       this.lyric4 = "";
       this.lyric5 = "";
       this.lyric6 = "";
       this.lyric7 = "";
       this.lyric8 = "";
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
 }
 .cover {
   filter: blur(12px);
   width: 100%;
   height: 100%;
   opacity: 0.8;
   object-fit: contain;
   position: absolute;
   z-index: -1;
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
