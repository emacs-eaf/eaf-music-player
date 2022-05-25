<template>
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
</template>

<script>
 import { mapState } from "vuex";

 export default {
   name: 'Playlist',
   data() {
     return {
     }
   },
   computed: mapState([
     "currentTrack",
     "currentTrackIndex",
     "numberWidth",
     "fileInfos",
   ]),
   watch: {
     "currentTrack": function() {
       this.$refs.playlist.children[this.currentTrackIndex].scrollIntoViewIfNeeded(false);
     }
   },
   props: {
     backgroundColor: String,
     foregroundColor: String,
     pyobject: Object,
   },
   mounted() {
     window.addFiles = this.addFiles;
     window.scrollUp = this.scrollUp;
     window.scrollDown = this.scrollDown;
     window.scrollUpPage = this.scrollUpPage;
     window.scrollDownPage = this.scrollDownPage;
     window.scrollToBegin = this.scrollToBegin;
     window.scrollToBottom = this.scrollToBottom;
     window.jumpToFile = this.jumpToFile;
     window.sortByTitle = this.sortByTitle;
     window.sortByArtist = this.sortByArtist;
     window.sortByAlbum = this.sortByAlbum;
   },
   methods: {
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

     sortByTitle() {
       this.$store.commit("changeSort", "title");
       window.pyobject.eval_emacs_function("message", ["Sort by title."]);
     },

     sortByArtist() {
       this.$store.commit("changeSort", "artist");
       window.pyobject.eval_emacs_function("message", ["Sort by artist."]);
     },
     
     sortByAlbum() {
       this.$store.commit("changeSort", "album");
       window.pyobject.eval_emacs_function("message", ["Sort by album."]);
     }
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
   text-overflow: ellipsis;
   overflow:hidden
 }

 .item-artist {
   width: 20%;
   text-overflow: ellipsis;
   overflow:hidden
 }

 .item-album {
   width: 30%;
 }
</style>
