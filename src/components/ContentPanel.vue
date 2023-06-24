<template>
  <div class="content">
    <LocalPlaylist
      ref="local"
      v-if="isLocalDisplaySource"
      :backgroundColor="backgroundColor"
      :foregroundColor="foregroundColor">
    </LocalPlaylist>

    <CloudPanel
      ref="cloud"
      v-if="!isLocalDisplaySource"
      :backgroundColor="backgroundColor"
      :foregroundColor="foregroundColor">
    </CloudPanel>
  </div>
</template>
  
<script>
 import LocalPlaylist from './LocalPlaylist.vue';
 import CloudPanel from './CloudPanel.vue';
 import { mapGetters } from 'vuex';
 export default {
   name: 'ContentPanel',
   mounted() {
     window.togglePlaySource = this.togglePlaySource;

     // playlist sorted
     window.sortByTitle = this.sortByTitle;
     window.sortByArtist = this.sortByArtist;
     window.sortByAlbum = this.sortByAlbum;

     // scroll
     window.scrollUp = this.scrollUp;
     window.scrollDown = this.scrollDown;
     window.scrollUpPage = this.scrollUpPage;
     window.scrollDownPage = this.scrollDownPage;
     window.scrollToBegin = this.scrollToBegin;
     window.scrollToBottom = this.scrollToBottom;

     // playlist
     window.playlistPrev = this.playlistPrev;
     window.playlistNext = this.playlistNext;
     window.scrollPlaylistUp = this.scrollPlaylistUp;
     window.scrollPlaylistDown = this.scrollPlaylistDown;

   },
   components: {
     LocalPlaylist,
     CloudPanel
   },
   computed: {
     ...mapGetters([
       "isLocalDisplaySource"
     ])
   },
   props: {
     backgroundColor: String,
     foregroundColor: String
   },
   methods: {
     togglePlaySource() {
       if (this.isLocalDisplaySource) {
         this.$store.commit('updateDisplaySource', 'cloud');
       } else {
         this.$store.commit('updateDisplaySource', 'local');
       }
     },
     sortByTitle() {
       this.$store.commit("sortTrackInfos", "title");
       window.pyobject.eval_emacs_function("message", ["Sort by title."]);
     },

     sortByArtist() {
       this.$store.commit("sortTrackInfos", "artist");
       window.pyobject.eval_emacs_function("message", ["Sort by artist."]);
     },

     sortByAlbum() {
       this.$store.commit("sortTrackInfos", "album");
       window.pyobject.eval_emacs_function("message", ["Sort by album."]);
     },

     scrollUp() {
       if (this.isLocalDisplaySource) {
         this.$refs.local.scrollUp();
       } else {
         this.$refs.cloud.scrollUp();
       }
     },

     scrollDown() {
       if (this.isLocalDisplaySource) {
         this.$refs.local.scrollDown();
       } else {
         this.$refs.cloud.scrollDown();
       }
     },

     scrollUpPage() {
       if (this.isLocalDisplaySource) {
         this.$refs.local.scrollUpPage();
       } else {
         this.$refs.cloud.scrollUpPage();
       }
     },

     scrollDownPage() {
       if (this.isLocalDisplaySource) {
         this.$refs.local.scrollDownPage();
       } else {
         this.$refs.cloud.scrollDownPage();
       }
     },

     scrollToBegin() {
       if (this.isLocalDisplaySource) {
         this.$refs.local.scrollToBegin();
       } else {
         this.$refs.cloud.scrollToBegin();
       }
     },

     scrollToBottom() {
       if (this.isLocalDisplaySource) {
         this.$refs.local.scrollToBottom();
       } else {
         this.$refs.cloud.scrollToBottom();
       }
     },

     playlistPrev() {
       if (!this.isLocalDisplaySource) {
         this.$refs.cloud.playlistPrev();
       }
     },

     playlistNext() {
       if (!this.isLocalDisplaySource) {
         this.$refs.cloud.playlistNext();
       }
     },

     scrollPlaylistUp() {
       if (!this.isLocalDisplaySource) {
         this.$refs.cloud.scrollPlaylistUp();
       }
     },

     scrollPlaylistDown() {
       if (!this.isLocalDisplaySource) {
         this.$refs.cloud.scrollPlaylistDown();
       }
     }

   }
 }
</script>


<style scoped>
 .page {
   width: 100%;
   height: 100%;
   display: flex;
   flex-direction: column;
   align-items: center;
   justify-content: center;
   position: relative;
 }
 .content {
   width: 100%;
   height: 100%;
   overflow: hidden;
   display: flex;
   flex-direction: column;
   overflow: scroll;
 }
 ::-webkit-scrollbar {
   display: none;
 }
</style>
