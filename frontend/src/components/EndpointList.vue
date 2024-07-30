<template>
    <div class="endpoint-list">
      <div v-for="endpoint in endpoints" :key="endpoint.endpoint" class="endpoint">
        <h2>{{ endpoint.display_name || endpoint.endpoint }}</h2>
        <ul>
          <li v-for="ping in endpoint.pings.slice(0, 5)" :key="ping.sent_time">
            {{ ping.sent_time }} - {{ ping.successful ? 'Success' : 'Failure' }}
          </li>
        </ul>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'EndpointList',
    props: {
      endpoints: Array,
    },
  };
  </script>
  
  <style scoped>
  .endpoint {
    margin-bottom: 20px;
  }
  </style>