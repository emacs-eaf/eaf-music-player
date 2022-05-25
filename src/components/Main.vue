<template>
  <div id="page">
    <div class="content">
      <Playlist
        v-if="currentPanel === 'Playlist'"
        class="playlist"
        :backgroundColor="backgroundColor"
        :foregroundColor="foregroundColor"
        :pyobject="pyobject"
        :style="{ 'margin-bottom': panelHeight }">
      </Playlist>
      <LyricPanel 
        v-if="currentPanel === 'LyricsPanel'"
        class="lyric-panel"
        :currentTime="currentTime"
        :foregroundColor="foregroundColor"
        :style="{ 'margin-bottom': panelHeight }">
      </LyricPanel>
      <Panel
        @getCurrentTime="getCurrentTime"
        :style="{ 'height': panelHeight }">
      </Panel>
    </div>
  </div>
</template>

<script>
 import Playlist from '@/components/Playlist.vue'
 import Panel from '@/components/Panel.vue'
 import LyricPanel from '@/components/LyricPanel.vue'
 import { QWebChannel } from "qwebchannel";

 export default {
   name: 'App',
   components: {
     Playlist,
     Panel,
     LyricPanel
   },
   data() {
     return {
       panelHeight: "90px",
       currentPanel: "Playlist",
       currentTime: "",
       backgroundColor: "",
       foregroundColor: "",
     }
   },
   props: {
   },
   created() {
     // eslint-disable-next-line no-undef
     new QWebChannel(qt.webChannelTransport, channel => {
       window.pyobject = channel.objects.pyobject;
     });
   },
   mounted() {
     window.initPlaylistColor = this.initPlaylistColor;
     window.changePanel = this.changePanel;
   },
   methods: {
     initPlaylistColor(backgroundColor, foregroundColor) {
       this.backgroundColor = backgroundColor;
       this.foregroundColor = foregroundColor;
     },

     changePanel() {
       if (this.currentPanel === "Playlist") {
         this.currentPanel = "LyricsPanel";
       } else {
         this.currentPanel = "Playlist";
       }
     },

     getCurrentTime(time) {
       this.currentTime = time;
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
 }

 ::-webkit-scrollbar {
   display: none;
 }

 .playlist {
   overflow: scroll;
 }

</style>
