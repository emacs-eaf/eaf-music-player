<template>
  <div class="login">
    <div class="container">
      <div class="main">
        <h3>扫码登录</h3>
        <canvas ref="canvas"></canvas>
      </div>
    </div>
  </div>
</template>

<script>
import QRCode from 'qrcode'
import { mapState } from 'vuex'
export default {
  name: 'CloudLogin',
  data() {
    return {
    }
  },
  methods: {
    // 生成二维码
    makeQrCode(url) {
      let opts = {
        errorCorrectionLevel: 'H',
        type: 'image/png',
        quality: 0.3,
        width: 165,
        height: 165,
        text: 'xxx',
        color: {
          dark: '#333333',
          light: '#fff'
        }
      }
      QRCode.toCanvas(this.$refs.canvas, url, opts)
    }
  },
  computed: mapState([
    "cloudLoginQr"
  ]),
  watch: {
    cloudLoginQr: {
      // eslint-disable-next-line no-unused-vars
      handler: function (val, oldVal) {
        console.log(val.qrcode);
        this.makeQrCode(val.qrcode);
      }
    }
  }
}
</script>

<style>
* {
  margin: 0 auto;
  padding: 0;
}

.login {
  width: 100%;
  height: 100vh;
}

.container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.main {
  position: relative;
  width: 280px;
  height: 250px;
  margin: 0 auto;
  border-radius: 5px;
  background-color: #fff;
  box-shadow: 2px 2px 2px #bbb;
}

h3 {
  padding: 10px;
  text-align: center;
}

canvas {
  display: flex;
  align-items: center;
  justify-content: center;
}

.invalid {
  position: absolute;
  top: 50%;
  left: 50%;
  margin-top: -68px;
  margin-left: -70px;
  width: 143px;
  height: 143px;
  background: rgba(255, 255, 255, 0.9);
  text-align: center;
}

p {
  font-size: 14px;
  margin-top: 40px;
  margin-bottom: 5px;
}

button {
  color: #fff;
  padding: 3px 10px;
  background: #71c771;
  border: 1px solid #5baf5b;
  border-radius: 5px;
  cursor: pointer;
}</style>

