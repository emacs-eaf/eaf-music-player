<template>
    <div>
        <CloudLogin
          v-if="currentPanel === 'Login'">
        </CloudLogin>
        <CloudPlaylist
          v-if="currentPanel === 'Playlist'"
          ref="playlist"
          :backgroundColor="backgroundColor"
          :foregroundColor="foregroundColor">
        </CloudPlaylist>
    </div>
</template>

<script>
 import { mapState } from 'vuex';
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
       currentPanel: ""
     }
   },
   mounted() {
     window.cloudUpdateSongInfos = this.cloudUpdateSongInfos;
     window.cloudUpdateLoginState = this.cloudUpdateLoginState;
     window.cloudUpdateLoginQr = this.cloudUpdateLoginQr;
   },
   methods: {
     cloudUpdateSongInfos(song_infos) {
       this.$store.commit("updateCloudSongInfos", song_infos);
     },
     cloudUpdateLoginState(val) {
       this.$store.commit("updateCloudLoginState", val);
     },
     cloudUpdateLoginQr(val) {
       this.$store.commit("updateCloudLoginQr", val);
     },
   },
   computed: mapState([
     "cloudLoginState"
   ]),

   watch: {
     cloudLoginState: {
       // eslint-disable-next-line no-unused-vars
       handler: function (val, oldVal) {
         if (val) {
           this.currentPanel = "Playlist";
         } else {
           this.currentPanel = "Login";
         }
       }
     }
   },
   props: {
     backgroundColor: String,
     foregroundColor: String
   }
 }

</script>
