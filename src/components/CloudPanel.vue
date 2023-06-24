<template>
    <div class="cloud-panel">
      <CloudLogin
        v-if="!cloudLoginState">
        </CloudLogin>
        <CloudPlaylist
          v-if="cloudLoginState"
          ref="playlist"
          :backgroundColor="backgroundColor"
          :foregroundColor="foregroundColor">
        </CloudPlaylist>
    </div>
</template>

<script>
 import { mapState } from "vuex";
 import CloudLogin from './CloudLogin.vue';
 import CloudPlaylist from './CloudPlaylist.vue';
 export default {
   name: 'CloudPanel',
   components: {
     CloudLogin,
     CloudPlaylist
   },

   data() {
     return {
     }
   },
   mounted() {
   },
   computed: {
     ...mapState([
       "cloudLoginState",
     ]),
   },
   methods: {
     playItem(index) {
       this.$refs.playlist.playItem(index);
     },

     scrollUp() {
       this.$refs.playlist.scrollUp();
     },

     scrollDown() {
       this.$refs.playlist.scrollDown();
     },

     scrollUpPage() {
       this.$refs.playlist.scrollUpPage();
     },

     scrollDownPage() {
       this.$refs.playlist.scrollDownPage();
     },

     scrollToBegin() {
       this.$refs.playlist.scrollToBegin();
     },

     scrollToBottom() {
       this.$refs.playlist.scrollToBottom();
     },

     playlistPrev() {
       this.$refs.playlist.playlistPrev();
     },

     playlistNext() {
       this.$refs.playlist.playlistNext();
     }
   },
   props: {
     backgroundColor: String,
     foregroundColor: String
   }
 }

</script>

<style scoped>
 .cloud-panel {
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
