<template>
<div>
  <div class="top-bar">
    <div class="item-index"> #&nbsp; </div>
    <div class="item-name"> TITLE </div>
    <div class="item-artist"> ARTIST </div>
    <div class="item-album"> ALBUM </div>
  </div>
  <div
    ref="playlist"
    class="playlist">
    <div
      class="item eaf-music-player-item"
      v-for="(item, index) in fileInfos"
      @click="playItem(item)"
      :key="item.path"
      :style="{ 'background': itemBackgroundColor(item), 'color': itemForegroundColor(item) }">
      <div class="item-index">
        {{ padNumber(index + 1, numberWidth) }}
      </div>
      <div class="item-name">
        {{ item.name }}
      </div>
      <div class="item-artist">
        {{ item.artist }}
      </div>
      <div class="item-album">
        {{ item.album }}
      </div>
    </div>
  </div>
<div>
</template>

<script>
 import { mapState } from "vuex";
 import { QWebChannel } from "qwebchannel";

 export default {
   name: 'Playlist',
   data() {
     return {
       backgroundColor: "",
       foregroundColor: "",
     }
   },
   computed: mapState([
     "currentTrack",
     "currentTrackIndex",
     "numberWidth",
     "fileInfos",
     "playListSortIndex"
   ]),
   watch: {
     "currentTrack": function() {
       this.$refs.playlist.children[this.currentTrackIndex].scrollIntoViewIfNeeded(false);
     }
   },
   props: {
   },
   mounted() {
     window.initPlaylistColor = this.initPlaylistColor;
     window.addFiles = this.addFiles;
     window.scrollUp = this.scrollUp;
     window.scrollDown = this.scrollDown;
     window.scrollUpPage = this.scrollUpPage;
     window.scrollDownPage = this.scrollDownPage;
     window.scrollToBegin = this.scrollToBegin;
     window.scrollToBottom = this.scrollToBottom;
     window.jumpToFile = this.jumpToFile;
     window.changeSort = this.changeSort;
   },
   created() {
     // eslint-disable-next-line no-undef
     new QWebChannel(qt.webChannelTransport, channel => {
       window.pyobject = channel.objects.pyobject;
     });
   },
   methods: {
     initPlaylistColor(backgroundColor, foregroundColor) {
       this.backgroundColor = backgroundColor;
       this.foregroundColor = foregroundColor;
     },

     addFiles(files) {
       this.$store.commit("updateFileInfos", files);
     },

     playItem(item) {
       this.$root.$emit("playItem", item);
     },

     padNumber(num, size) {
       var s = num+"";
       while (s.length < size) s = "0" + s;

       return s;
     },

     itemBackgroundColor(item) {
       if (item.path == this.currentTrack) {
         return this.foregroundColor;
       } else {
         return this.backgroundColor;
       }
     },

     itemForegroundColor(item) {
       if (item.path == this.currentTrack) {
         return this.backgroundColor;
       } else {
         return this.foregroundColor;
       }
     },

     scrollUp() {
       this.$refs.playlist.scrollTop += 30;
     },

     scrollDown() {
       this.$refs.playlist.scrollTop -= 30;
     },

     scrollUpPage() {
       this.$refs.playlist.scrollTop += this.$refs.playlist.offsetHeight;
     },

     scrollDownPage() {
       this.$refs.playlist.scrollTop -= this.$refs.playlist.offsetHeight;
     },

     scrollToBegin() {
       this.$refs.playlist.scrollTop = 0;
     },

     scrollToBottom() {
       this.$refs.playlist.scrollTop = this.$refs.playlist.scrollHeight;
     },

     jumpToFile() {
       window.pyobject.eval_emacs_function("eaf-open-in-file-manager", [this.currentTrack]);
     },
     changeSort() {
       this.$store.commit("changeSort");
       var tempIndex = (this.playListSortIndex + 1) % 3;
       if (tempIndex === 0) {
         window.pyobject.eval_emacs_function("message", ["Sort by title."]);
       } else if (tempIndex === 1) {
         window.pyobject.eval_emacs_function("message", ["Sort by article."]);
       } else if (tempIndex === 2) {
         window.pyobject.eval_emacs_function("message", ["Sort by album."]);
       }
    },
   }
 }

</script>

<style scoped>
 .playlist {
   width: 100%;
   height: 100%;

   white-space: nowrap;
   text-overflow: ellipsis;
 }
 .top-bar {
   padding-left: 20px;
   padding-right: 20px;
   padding-top: 5px;
   padding-bottom: 5px;

   display: flex;
   position: sticky;
   flex-direction: row;
   align-items: center;

   user-select: none;
 }
 .item {
   padding-left: 20px;
   padding-right: 20px;
   padding-top: 5px;
   padding-bottom: 5px;

   display: flex;
   flex-direction: row;
   align-items: center;

   user-select: none;
 }

 .item-index {
   margin-right: 10px;
 }

 .item-name {
   width: 40%;
 }

 .item-artist {
   width: 20%;
 }

 .item-album {
   width: 30%;
 }
</style>
