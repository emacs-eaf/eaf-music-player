<template>
  <div
    ref="playlist"
    class="playlist">
    <div
      class="item eaf-music-player-item"
      v-for="(item, index) in localTrackInfos"
      @click="playItem(index)"
      :key="item.path"
      :style="{ 'background': itemBackgroundColor(index), 'color': itemForegroundColor(index) }">
      <div class="item-index">
        {{ padNumber(index + 1, localNumberWidth) }}
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
 import { mapState, mapGetters } from "vuex";


 export default {
   name: 'LocalPlaylist',
   data() {
     return {
     }
   },
   computed: {
     ...mapState([
       "localCurrentTrackIndex",
       "localNumberWidth",
       "localTrackInfos",
       "playSource"
     ]),
     ...mapGetters([
       "localCurrentTrackPath",
       "currentPlayTrackKey"
     ])
   },
   props: {
     backgroundColor: String,
     foregroundColor: String
   },
   watch: {
     localCurrentTrackIndex: function() {
       this.scrollToCurrentTrack();
     }
   },
   updated() {
     this.$nextTick(function () {
       this.scrollToCurrentTrack();
     })
   },
   mounted() {
     window.addLocalTrackInfos = this.addLocalTrackInfos;
     window.jumpToFile = this.jumpToFile;
     window.updateTagInfo = this.updateTagInfo;

     this.$nextTick(function() {
       this.scrollToCurrentTrack();
     })
   },
   created() {
   },
   methods: {
     addLocalTrackInfos(infos) {
       this.$store.commit("updateLocalTrackInfos", infos);
     },

     playItem(index) {
       this.$store.commit('setPlaySource', 'local');
       this.$root.$emit("playTrack", index);
     },

     padNumber(num, size) {
       var s = num+"";
       while (s.length < size) s = "0" + s;
       return s;
     },

     itemBackgroundColor(index) {
       if (index == this.localCurrentTrackIndex) {
         return this.foregroundColor;
       } else {
         return this.backgroundColor;
       }
     },

     itemForegroundColor(index) {
       if (index == this.localCurrentTrackIndex) {
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
       window.pyobject.eval_emacs_function("eaf-open-in-file-manager", [this.localCurrentTrackPath]);
     },

     updateTagInfo(track, name, artist, album) {
       this.$store.commit("updateLocalTrackTagInfo", { track, name, artist, album });
       this.$store.commit("updatePlayTrackInfo", {name, artist});
     },

     scrollToCurrentTrack() {
       if (this.$refs.playlist) {
         this.$refs.playlist.children[this.localCurrentTrackIndex]?.scrollIntoViewIfNeeded(false);
       }
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
   overflow: scroll;
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
   overflow: hidden;
   white-space: nowrap;
   text-overflow: ellipsis;
   width: 40%;
 }

 .item-artist {
   width: 20%;
   overflow: hidden;
   white-space: nowrap;
   text-overflow: ellipsis;
 }

 .item-album {
   width: 30%;
 }
</style>
