<template>
  <div class="home">
    <div class="test">
      <custom-query />
      <p class="ml-2 mr-2">OR</p>
      <clinical-query-dialog />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import ClinicalQueryDialog from "@/components/ClinicalQueryDialog.vue";
import CustomQuery from "@/components/CustomQuery.vue";


export default defineComponent({
  name: 'HomeView',
  components: {CustomQuery, ClinicalQueryDialog },
  data: () => ({
    valid: true,
    query: ""
  }),
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
