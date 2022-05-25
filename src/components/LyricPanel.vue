<template>
  <div ref="lp" class="lp">
    <img class="cover" :src="currentCover">
    <div class="lyrics-container"
         :style="{ 'color': foregroundColor }">
      <p class="lyric-0 row" > {{lyric0}} </p>
      <p class="lyric-1 row" > {{lyric1}} </p>
      <p class="lyric-2 row" > {{lyric2}} </p>
      <p class="lyric-3 row" > {{lyric3}} </p>
      <p class="lyric-4 row" > {{lyric4}} </p>
      <p class="lyric-3 row" > {{lyric5}} </p>
      <p class="lyric-2 row" > {{lyric6}} </p>
      <p class="lyric-1 row" > {{lyric7}} </p>
      <p class="lyric-0 row" > {{lyric8}} </p>
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
     }
   },
   computed: mapState([
	   "currentTrack",
	   "currentTrackIndex",
	   "numberWidth",
	   "fileInfos",
	   "currentLyric",
	   "currentCover"
   ]),
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
       this.lyric0 = this.lyric1;
       this.lyric1 = this.lyric2;
       this.lyric2 = this.lyric3;
       this.lyric3 = this.lyric4;
       this.lyric4 = this.currentLyric[this.activeLyricRowIndex].content;
       this.lyric5 = this.currentLyric[(this.activeLyricRowIndex + 1) % this.currentLyric.length].content;
       this.lyric6 = this.currentLyric[(this.activeLyricRowIndex + 2) % this.currentLyric.length].content;
       this.lyric7 = this.currentLyric[(this.activeLyricRowIndex + 3) % this.currentLyric.length].content;
       this.lyric8 = this.currentLyric[(this.activeLyricRowIndex + 4) % this.currentLyric.length].content;
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
   margin-top: 10px;
   margin-bottom: 10px;
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
