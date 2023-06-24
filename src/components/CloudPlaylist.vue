<template>
  <div class="cloud-music">
    <div ref="cloudplaylist" class="cloud-music-list">
      <div class="music-list-item eaf-music-player-item"
        v-for="(item, index) in cloudPlaylists" :key="item.id"
        @click="switchPlaylist(index)"
        :style="{ 'background': playlistBackgroundColor(index), 'color': playlistForegroundColor(index) }">
        <div class="playlist-name">
          {{ item.name }}
        </div>
        <div class="playlist-info">
          {{ item.track_count }}首 by: {{ item.creator }}
        </div>
      </div>
    </div>
    <div class="separator"/>
    <div ref="playlist" class="playlist">
      <div class="item eaf-music-player-item"
        v-for="(item, index) in cloudTrackInfos" :key="item.id"
        @click="playItem(index)"
        :style="{ 'background': itemBackgroundColor(index), 'color': itemForegroundColor(index) }">
        <div class="item-index">
          {{ padNumber(index + 1, cloudNumberWidth) }}
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
  </div>
</template>

<script>
 import { mapState, mapGetters } from "vuex";

 export default {
   name: 'CloudPlaylist',
   data() {
     return {
     }
   },
   computed: {
     ...mapState([
       "cloudCurrentTrackIndex",
       "cloudNumberWidth",
       "cloudTrackInfos",
       "cloudPlaylists",
       "cloudCurrentPlaylistIndex",
       "playSource",
     ]),
     ...mapGetters([
       "currentPlayTrackKey"
     ])
   },
   props: {
     backgroundColor: String,
     foregroundColor: String,
   },
   watch: {
     cloudCurrentTrackIndex: function() {
       this.scrollToCurrentTrack();
     },
     cloudTrackInfos: {
       // eslint-disable-next-line no-unused-vars
       handler: function(val, oldVal) {
         /* Play music when first time load cloud list. */
         if (oldVal.length === 0 && val.length > 0) {
           this.playItem(0);
         }
       }
     }
   },
   mounted() {
     this.scrollToCurrentTrack();
   },
   methods: {
     playItem(index) {
       this.$store.commit('setPlaySource', 'cloud');
       this.$root.$emit("playTrack", index);
     },

     switchPlaylist(index) {
       this.$store.commit('setPlaySource', 'cloud');
       var playlistId = this.cloudPlaylists[index].id;
       this.$store.commit('updateCloudSwitchingPlaylist', true);
       this.$store.commit('updateCloudCurrentPlaylistIndex', index);
       window.pyobject.vue_update_playlist_tracks(playlistId);

       this.$nextTick(function() {
         this.scrollToCurrentTrack();
         this.$refs.cloudplaylist.children[this.cloudCurrentPlaylistIndex]?.scrollIntoViewIfNeeded(false);
       })
     },

     playlistPrev() {
       var index;
       if (this.cloudCurrentPlaylistIndex > 0) {
         index = this.cloudCurrentPlaylistIndex - 1;
       } else {
         index = this.cloudPlaylists.length - 1;
       }
       if (index !== undefined) {
         this.switchPlaylist(index);
       }
     },

     playlistNext() {
       var index;
       if (this.cloudCurrentPlaylistIndex < this.cloudPlaylists.length - 1) {
         index = this.cloudCurrentPlaylistIndex + 1;
       } else {
         index = 0;
       }
       if (index !== undefined) {
         this.switchPlaylist(index);
       }
     },

     scrollPlaylistUp() {
       this.$refs.cloudplaylist.scrollTop += 30;
     },

     scrollPlaylistDown() {
       this.$refs.cloudplaylist.scrollTop -= 30;
     },

     padNumber(num, size) {
       var s = num + "";
       while (s.length < size) s = "0" + s;
       return s;
     },

     playlistBackgroundColor(index) {
       if (index == this.cloudCurrentPlaylistIndex) {
         return this.foregroundColor;
       } else {
         return this.backgroundColor;
       }
     },

     playlistForegroundColor(index) {
       if (index == this.cloudCurrentPlaylistIndex) {
         return this.backgroundColor;
       } else {
         return this.foregroundColor;
       }
     },

     itemBackgroundColor(index) {
       if (index == this.cloudCurrentTrackIndex) {
         return this.foregroundColor;
       } else {
         return this.backgroundColor;
       }
     },

     itemForegroundColor(index) {
       if (index == this.cloudCurrentTrackIndex) {
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

     scrollToCurrentTrack() {
       if (this.$refs.playlist) {
         this.$refs.cloudplaylist.children[this.cloudCurrentPlaylistIndex]?.scrollIntoViewIfNeeded(false);
         this.$refs.playlist.children[this.cloudCurrentTrackIndex]?.scrollIntoViewIfNeeded(false);
       }
     }
   }
 }

</script>

<style scoped>
 .cloud-music {
   width: 100%;
   height: 100%;
   display: flex;
   flex-direction: row;
 }

 .cloud-music-list {
   min-width: 300px;
   max-width: 300px;
   height: 100%;
   overflow: scroll;
 }

 .music-list-item {
   padding-left: 10px;
   padding-right: 10px;
   padding-top: 5px;
   padding-bottom: 5px;
   user-select: none;
 }

 .separator {
   margin-left: 2px;
   margin-right: 2px;
   width: 1px;
   height: 100%;
   background: currentColor;
 }

 .playlist-name {
   white-space: nowrap;
   overflow: hidden;
   text-overflow: ellipsis;
   font-size: 15px;
 }

 .playlist-info {
   font-size: 12px;
 }

 .playlist {
   flex-grow: 1;
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
