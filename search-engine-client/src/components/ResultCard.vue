<template>
  <v-card class="ma-2" @click.prevent="goToURL" flat>
    <a :href="url" style="font-size: '8px'">{{ url }}</a>
    <h2>{{ title }}</h2>
    <p>{{ description.substring(0, 250)}}...</p>
  </v-card>
</template>
<script lang="ts">
  import { defineComponent } from 'vue';
  import axios from 'axios'

  export default defineComponent({
    name: 'ResultCard',
    props: {
      id: String,
      url: String,
      title: String,
      description: String
    },
    data: () => ({
    }),
    methods: {
      async goToURL(){
        if (this.url){
          window.location.href = this.url
        }
      }
    }
  });
</script>