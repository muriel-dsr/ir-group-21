<template>
    <div class="query-view">
        <div class="test">
            <v-card width="500" flat>
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
            </v-card>
        </div>
    </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import axios from "axios";


export default defineComponent({
    name: 'QueryView',
    data: () => ({
        valid: true,
        query: "",
        queries: []
    }),
    methods: {
        sendQuery(){
            if(this.query){
                this.$router.push({name: "results", params: {query: this.query}})
                return
            }
        },
        getQueries(){
            return axios.get(`http://127.0.0.1:5000/queries`).then(response => {
                this.queries = response.data
            }).catch(err => console.error(err))
        }
    },
    created(){
        this.getQueries()
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
