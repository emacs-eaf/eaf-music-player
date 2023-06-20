<template>
  <div ref="playlist" class="playlist">
    <div class="item eaf-music-player-item" v-for="(item, index) in cloudSongInfos" :key="item.id"
      :style="{ 'background': itemBackgroundColor(), 'color': itemForegroundColor() }">
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
</template>
  
<script>
import { mapState } from "vuex";

export default {
  name: 'CloudPlaylist',
  data() {
    return {

    }
  },
  computed: mapState([
    "cloudNumberWidth",
    "cloudSongInfos",
  ]),
  watch: {
  },
  props: {
    backgroundColor: String,
    foregroundColor: String,
    pyobject: Object,
  },
  created() {
  },
  methods: {
    padNumber(num, size) {
      var s = num + "";
      while (s.length < size) s = "0" + s;
      return s;
    },

    itemBackgroundColor() {
      return this.backgroundColor;
    },

    itemForegroundColor() {
      return this.foregroundColor;
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
