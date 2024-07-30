<template>
  <div id="app" :class="['theme', currentTheme]">
    <header>
      <h1 class="logo">knockNOC</h1>
      <div class="controls">
        <button @click="cycleTheme">Change Theme</button>
        <button @click="toggleStatusIndicator">Toggle Status</button>
      </div>
    </header>
    <ping-list 
      :endpoints="endpoints" 
      :theme="currentTheme"
      :statusIndicatorType="statusIndicatorType"
      @update:position="updateEndpointPosition" 
    />
  </div>
</template>

<script>
import axios from 'axios';
import PingList from './components/PingList.vue';

export default {
  name: 'App',
  components: {
    PingList,
  },
  data() {
    return {
      endpoints: [],
      currentTheme: 'cyberpunk',
      statusIndicatorType: 'original',
      savedPositions: {}
    };
  },
  methods: {
    cycleTheme() {
      const themes = ['cyberpunk', 'modern', 'retro', 'minimalist', 'dark', 'light', 'neon', 'pastel', 'brutalist', 'glassmorphism'];
      const currentIndex = themes.indexOf(this.currentTheme);
      this.currentTheme = themes[(currentIndex + 1) % themes.length];
    },
    toggleStatusIndicator() {
      const types = ['original', 'pulse', 'wave', 'meter', 'matrix', 'heartbeat'];
      const currentIndex = types.indexOf(this.statusIndicatorType);
      this.statusIndicatorType = types[(currentIndex + 1) % types.length];
    },
    fetchData() {
      axios.get('/api/pings')
        .then(response => {
          const newEndpoints = response.data.map((endpoint, index) => {
            const savedPosition = this.savedPositions[endpoint.endpoint];
            return {
              ...endpoint,
              order: savedPosition ? savedPosition.order : index
            };
          });
          this.endpoints = newEndpoints.sort((a, b) => a.order - b.order);
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        });
    },
    updateEndpointPosition(endpoint, newOrder) {
      this.savedPositions[endpoint.endpoint] = { order: newOrder };
      this.endpoints = this.endpoints.map(e => {
        if (e.endpoint === endpoint.endpoint) {
          return { ...e, order: newOrder };
        }
        return e;
      }).sort((a, b) => a.order - b.order);
    }
  },
  mounted() {
    this.fetchData();
    setInterval(this.fetchData, 10000); // Fetch data every 10 seconds
  },
};
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&family=VT323&family=Press+Start+2P&family=Courier+Prime&family=Quicksand&family=Orbitron&family=Playfair+Display&family=Montserrat&family=Fira+Sans&display=swap');

body, html {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
}

#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  transition: all 0.5s ease;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}

.controls {
  display: flex;
  gap: 10px;
}

button {
  padding: 10px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

/* Cyberpunk Theme */
.theme.cyberpunk {
  background-color: #0a0a2e;
  color: #00ff00;
  font-family: 'Orbitron', sans-serif;
}

.theme.cyberpunk button {
  background-color: #ff00ff;
  color: #000;
  border: none;
  text-transform: uppercase;
}

/* Modern Theme */
.theme.modern {
  background-color: #ffffff;
  color: #333333;
  font-family: 'Roboto', sans-serif;
}

.theme.modern button {
  background-color: #007bff;
  color: #ffffff;
  border: none;
  border-radius: 5px;
}

/* Retro Theme */
.theme.retro {
  background-color: #fdf6e3;
  color: #002b36;
  font-family: 'VT323', monospace;
}

.theme.retro button {
  background-color: #cb4b16;
  color: #fdf6e3;
  border: 2px solid #002b36;
}

/* Minimalist Theme */
.theme.minimalist {
  background-color: #f8f8f8;
  color: #333;
  font-family: 'Quicksand', sans-serif;
}

.theme.minimalist button {
  background-color: #f8f8f8;
  color: #333;
  border: 1px solid #333;
}

/* Dark Theme */
.theme.dark {
  background-color: #1a1a1a;
  color: #ffffff;
  font-family: 'Fira Sans', sans-serif;
}

.theme.dark button {
  background-color: #333333;
  color: #ffffff;
  border: none;
}

/* Light Theme */
.theme.light {
  background-color: #ffffff;
  color: #333333;
  font-family: 'Montserrat', sans-serif;
}

.theme.light button {
  background-color: #f0f0f0;
  color: #333333;
  border: 1px solid #dddddd;
}

/* Neon Theme */
.theme.neon {
  background-color: #0c0c1d;
  color: #ff00ff;
  font-family: 'Press Start 2P', cursive;
}

.theme.neon button {
  background-color: #00ffff;
  color: #0c0c1d;
  border: none;
  box-shadow: 0 0 10px #00ffff;
}

/* Pastel Theme */
.theme.pastel {
  background-color: #f0e6ef;
  color: #7c6f7c;
  font-family: 'Playfair Display', serif;
}

.theme.pastel button {
  background-color: #c3aed6;
  color: #ffffff;
  border: none;
  border-radius: 20px;
}

/* Brutalist Theme */
.theme.brutalist {
  background-color: #cccccc;
  color: #000000;
  font-family: 'Courier Prime', monospace;
}

.theme.brutalist button {
  background-color: #000000;
  color: #cccccc;
  border: 3px solid #000000;
  text-transform: uppercase;
}

/* Glassmorphism Theme */
.theme.glassmorphism {
  background: linear-gradient(45deg, #ff9a9e 0%, #fad0c4 99%, #fad0c4 100%);
  color: #333333;
  font-family: 'Roboto', sans-serif;
}

.theme.glassmorphism button {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #333333;
}

.theme.glassmorphism header {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}
</style>