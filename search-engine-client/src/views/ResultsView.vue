<template>
  <div class="results">
  <h1>Results</h1>
  <h2>{{ query }}</h2>
    <v-row>
      <v-col cols="11">
          <div v-for="result in results" :key="result._id">
            <result-card :id="result._id"
                         :title=result.title
                         :url=result.url
                         :description="result.description" />
<!--            <p>Clicks: {{ result.clicks }}</p>-->
          </div>
      </v-col>
    </v-row>
  </div>
</template>
<script lang="ts">
  import { defineComponent } from 'vue';
  import axios from 'axios'
  import ResultCard from "@/components/ResultCard.vue";

  export default defineComponent({
    name: 'ResultsView',
    components: { ResultCard },
    data: () => ({
      query: "",
      results: [],
      queryTerms: [],
      iDFTotal: 0
    }),
    created() {
      this.query = `${this.$route.params.query}`
      return axios.get(`http://127.0.0.1:5000/data?${this.query}`).then(response => {
        this.results = response.data
        // this.queryTerms = response.data[1]
        console.log(response.data)
      }).catch(err => console.error(err))
    }
  });
</script>
