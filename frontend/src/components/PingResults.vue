<template>
  <div class="ping-results">
    <ul>
      <li v-for="ping in pings.slice(0, 5)" :key="ping.sent_time" :class="{ success: ping.successful, failure: !ping.successful }">
        {{ new Date(ping.sent_time).toLocaleString() }} - {{ ping.successful ? 'Success' : 'Failure' }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'PingResults',
  props: {
    pings: Array,
  },
};
</script>

<style scoped>
.success {
  color: green;
}
.failure {
  color: red;
}
</style>