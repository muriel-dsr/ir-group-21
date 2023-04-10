<template>
  <div class="text-center">
    <v-btn
        color="primary"
    >
      Select / Update Clinical Dataset Query

      <v-dialog
          v-model="dialog"
          activator="parent"
          width="600"
      >
        <v-card>
          <v-card-text>
            Select Pre-defined Query:
          </v-card-text>
          <v-form @submit.prevent="sendQuery"
                  v-model="valid" class="searchForm" >
            <v-row align="center">
              <v-autocomplete v-model="query"
                              :items="queries">
              </v-autocomplete>
            </v-row>
            <v-card-actions class="justify-center">
              <v-btn type="submit"
                     color="primary"
                     variant="text"
                     :disabled="!query">Go</v-btn>
            </v-card-actions>
          </v-form>
<!--          <v-card-actions>-->
<!--            <v-btn color="primary" block @click="dialog = false">Close Dialog</v-btn>-->
<!--          </v-card-actions>-->
        </v-card>
      </v-dialog>
    </v-btn>
  </div>
</template>
<script lang="ts">
  import { defineComponent } from 'vue';
  import axios from "axios";

  export default defineComponent({
    name: 'ClinicalQueryDialog',
    data: () => ({
        dialog: false,
        query: "",
        queries: [],
        valid: false
    }),
    methods: {
      sendQuery(){
        if(this.query){
          this.$router.push({name: "results", params: {query: this.query}}).then(() => {
            this.dialog = false
          }).catch(() => {
            this.dialog = false
          })
          return
        }
      },
      getQueries(){
        return axios.get(`http://127.0.0.1:5000/queries`).then(response => {
          this.queries = response.data
        }).catch(err => console.error(err))
      }
    },
    created() {
      this.getQueries()
    }
  });
</script>