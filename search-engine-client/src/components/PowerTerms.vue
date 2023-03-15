<template>
  <div class="PowerTerms">
    <p>Each word in your query has power. This is the power percentage for each word in your query: </p>
    <br> 
    <div v-for="term in queryTerms" :key="term._id">
      <p> {{ term.name }}: {{ calculateIDFPercentage(term.idf) }}%</p>
    </div>
  </div>
</template>
<script lang="ts">
  import { defineComponent } from 'vue';

  export default defineComponent({
    name: 'PowerTerms',
    props: {
      queryTerms: Array
    },
    data: () => ({
    }),
    computed:{
      iDFTotal(){
        if(this.queryTerms && this.queryTerms.length > 0){
          return this.queryTerms.map((term: any) => term.idf).reduce((acc, cV) => acc + cV, 0)
        }
        return 0
      }
    },
    methods: {
      calculateIDFPercentage(idfScore: number){
        return ((100 / this.iDFTotal) * idfScore).toFixed(2)
      }
    }
  });
</script>