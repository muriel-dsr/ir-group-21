<template>
  <div class="results">
    <v-row justify="center" align="center" class="mt-4">
      <custom-query :original-query="queryLimited" />
      <p class="ml-2 mr-2">OR</p>
      <clinical-query-dialog />
    </v-row>
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
  import ClinicalQueryDialog from "@/components/ClinicalQueryDialog.vue";
  import CustomQuery from "@/components/CustomQuery.vue";

  export default defineComponent({
    name: 'ResultsView',
    components: {CustomQuery, ClinicalQueryDialog, ResultCard },
    data: () => ({
      query: "",
      results: [],
      queryTerms: [],
      iDFTotal: 0
    }),
    computed:{
      queryLimited(){
        if(!this.query){
          return ""
        }
        return this.query.length < 120 ? this.query : this.query.slice(0, 120) + '...'
      }
    },
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
