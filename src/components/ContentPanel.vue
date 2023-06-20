<template>
    <div class="content">
      <LocalPlaylist
        ref="local"
        v-show="isLocalDisplaySource"
        :backgroundColor="backgroundColor"
        :foregroundColor="foregroundColor">
      </LocalPlaylist>

      <CloudPanel
        ref="cloud"
        v-show="!isLocalDisplaySource"
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
