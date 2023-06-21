<template>
  <div id="page">
    <div class="content">
      <ContentPanel
        v-if="currentPanel === 'ContentPanel'"
        :backgroundColor="backgroundColor"
        :foregroundColor="foregroundColor"
        :style="{ 'margin-bottom': panelHeight }">
      </ContentPanel>
      <LyricPanel
        v-if="currentPanel === 'LyricPanel'"
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
 import ContentPanel from '@/components/ContentPanel.vue'
 import Panel from '@/components/Panel.vue'
 import LyricPanel from '@/components/LyricPanel.vue'
 import { QWebChannel } from "qwebchannel";
 export default {
   name: 'App',
   components: {
     ContentPanel,
     Panel,
     LyricPanel
   },
   data() {
     return {
       panelHeight: "90px",
       currentPanel: "ContentPanel",
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
     window.initPlaylist = this.initPlaylist;
     window.changePanel = this.changePanel;

     // cloud
     window.cloudUpdateTrackInfos = this.cloudUpdateTrackInfos;
     window.cloudUpdateLoginState = this.cloudUpdateLoginState;
     window.cloudUpdateLoginQr = this.cloudUpdateLoginQr;
     window.cloudUpdateTrackAudioSource = this.cloudUpdateTrackAudioSource;
   },
   methods: {
     initPlaylist(backgroundColor, foregroundColor) {
       this.backgroundColor = backgroundColor;
       this.foregroundColor = foregroundColor;
     },

     changePanel() {
       if (this.currentPanel === "ContentPanel") {
         this.currentPanel = "LyricPanel";
       } else {
         this.currentPanel = "ContentPanel";
       }
     },

     getCurrentTime(time) {
       this.currentTime = time;
     },

     cloudUpdateTrackInfos(track_infos) {
       this.$store.commit("updateCloudTrackInfos", track_infos);
     },

     cloudUpdateLoginQr(val) {
       this.$store.commit("updateCloudLoginQr", val);
     },

     cloudUpdateLoginState(val) {
       this.$store.commit("updateCloudLoginState", val);
     },

     cloudUpdateTrackAudioSource(val) {
       this.$store.commit("updateAudioSource", val);
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
</style>
