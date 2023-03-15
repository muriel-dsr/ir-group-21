<template>
  <div class="home">
    <div class="test">
      <v-card width="500" flat>
        <v-form @submit.prevent="sendQuery"
                v-model="valid" class="searchForm" >
          <v-row align="center">
            <v-text-field v-model="query"></v-text-field>
            <v-btn type="submit"
                   color="primary"
                   variant="text"
            :disabled="!query">Go</v-btn>
          </v-row>
        </v-form>
      </v-card>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';


export default defineComponent({
  name: 'HomeView',
  data: () => ({
    valid: true,
    query: ""
  }),
  methods: {
    sendQuery(){
      if(this.query){
        this.$router.push({name: "results", params: {query: this.query}})
        return
      }
    }
  }
});
</script>
<style>
  .test {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
  }
</style>
