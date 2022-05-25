<template>
  <div id="app">
    <Main />
  </div>
</template>

<script>
 import Main from './components/Main.vue'

 export default {
   name: 'App',
   components: {
     Main
   },
   data() {
     return {
     }
   },
   props: {
   },
   mounted() {
   }
 }
</script>

<style>
 #app {
   width: 100%;
   height: 100%;
 }

 html, body {
   width: 100%;
   height: 100%;
   margin: 0;
   padding: 0;
 }

 ::-webkit-scrollbar {
   display: none;
 }
</style>
