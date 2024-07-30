<template>
    <div class="ping-list">
      <div class="grid-container">
        <div
          v-for="(endpoint, index) in sortedEndpoints"
          :key="endpoint.endpoint"
          :class="['endpoint', theme]"
          @mousedown="startDrag($event, index)"
        >
          <h2>{{ endpoint.display_name || endpoint.endpoint }}</h2>
          <div :class="['status-indicator', statusIndicatorType]">
            <template v-if="statusIndicatorType === 'original'">
              <ul>
                <li v-for="ping in endpoint.pings.slice(0, 5)" :key="ping.sent_time" 
                    :class="{ success: ping.successful, failure: !ping.successful }">
                  {{ formatTime(ping.sent_time) }} - 
                  {{ ping.successful ? 'Online' : 'Offline' }}
                </li>
              </ul>
            </template>
            <template v-else-if="statusIndicatorType === 'pulse'">
              <div :class="['pulse', { active: isActive(endpoint) }]"></div>
            </template>
            <template v-else-if="statusIndicatorType === 'wave'">
              <div class="wave-container">
                <div v-for="n in 5" :key="n" :class="['wave', { active: isActive(endpoint) }]" :style="{ animationDelay: `${n * 0.1}s` }"></div>
              </div>
            </template>
            <template v-else-if="statusIndicatorType === 'meter'">
              <div class="meter-container">
                <div class="meter-bar" :style="{ width: `${getSuccessRate(endpoint)}%` }"></div>
                <span class="meter-text">{{ Math.round(getSuccessRate(endpoint)) }}%</span>
              </div>
            </template>
            <template v-else-if="statusIndicatorType === 'matrix'">
              <div class="matrix-container">
                <div v-for="(ping, index) in endpoint.pings.slice(0, 25)" :key="index" 
                     :class="['matrix-cell', { active: ping.successful }]"></div>
              </div>
            </template>
            <template v-else-if="statusIndicatorType === 'heartbeat'">
              <svg class="heartbeat" viewBox="0 0 100 30" xmlns="http://www.w3.org/2000/svg">
                <polyline :class="{ active: isActive(endpoint) }" points="0,15 20,15 25,5 30,25 35,10 40,20 45,15 100,15" fill="none" stroke-width="2" />
              </svg>
            </template>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'PingList',
    props: {
      endpoints: Array,
      theme: String,
      statusIndicatorType: String
    },
    data() {
      return {
        isDragging: false,
        draggedIndex: null,
        draggedOver: null
      }
    },
    computed: {
      sortedEndpoints() {
        return [...this.endpoints].sort((a, b) => a.order - b.order);
      }
    },
    methods: {
      isActive(endpoint) {
        return endpoint.pings.length > 0 && endpoint.pings[0].successful;
      },
      formatTime(timeString) {
        const date = new Date(timeString);
        return date.toLocaleTimeString();
      },
      getSuccessRate(endpoint) {
        if (endpoint.pings.length === 0) return 0;
        const successCount = endpoint.pings.filter(ping => ping.successful).length;
        return (successCount / endpoint.pings.length) * 100;
      },
      startDrag(event, index) {
        this.isDragging = true;
        this.draggedIndex = index;
        event.dataTransfer.effectAllowed = 'move';
        event.dataTransfer.setData('text/plain', index);
        event.target.style.opacity = '0.5';
      },
      onDragOver(event, index) {
        event.preventDefault();
        this.draggedOver = index;
      },
      onDrop(event, index) {
        event.preventDefault();
        const fromIndex = event.dataTransfer.getData('text/plain');
        const toIndex = index;
        const endpoint = this.endpoints[fromIndex];
        this.$emit('update:position', endpoint, toIndex);
        this.isDragging = false;
        this.draggedIndex = null;
        this.draggedOver = null;
      },
      onDragEnd(event) {
        event.target.style.opacity = '1';
        this.isDragging = false;
        this.draggedIndex = null;
        this.draggedOver = null;
      }
    }
  };
  </script>
  
  <style scoped>
  .ping-list {
    height: calc(100vh - 90px);
    overflow-y: auto;
    padding: 20px;
  }
  
  .grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
  }
  
  .endpoint {
    border-radius: 10px;
    padding: 15px;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 120px;
  }
  
  .endpoint:hover {
    transform: translateY(-5px);
  }
  
  h2 {
    font-size: 1em;
    margin-bottom: 10px;
  }
  
  .status-indicator {
    flex-grow: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  /* Original indicator styles */
  .status-indicator.original ul {
    list-style-type: none;
    padding: 0;
    margin: 0;
    width: 100%;
  }
  
  .status-indicator.original li {
    margin: 5px 0;
    padding: 5px;
    border-radius: 4px;
    font-size: 0.8em;
  }
  
  /* Pulse indicator styles */
  .status-indicator.pulse {
    justify-content: center;
  }
  
  .status-indicator.pulse .pulse {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background-color: #ff0000;
    box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7);
    animation: pulse 1.5s infinite;
  }
  
  .status-indicator.pulse .pulse.active {
    background-color: #00ff00;
    box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7);
  }
  
  @keyframes pulse {
    0% {
      transform: scale(0.95);
      box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7);
    }
    
    70% {
      transform: scale(1);
      box-shadow: 0 0 0 10px rgba(255, 0, 0, 0);
    }
    
    100% {
      transform: scale(0.95);
      box-shadow: 0 0 0 0 rgba(255, 0, 0, 0);
    }
  }
  
  /* Wave indicator styles */
  .status-indicator.wave {
    justify-content: center;
  }
  
  .status-indicator.wave .wave-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 40px;
  }
  
  .status-indicator.wave .wave {
    width: 4px;
    height: 20px;
    background-color: #ff0000;
    margin: 0 2px;
    animation: wave 1s infinite ease-in-out;
  }
  
  .status-indicator.wave .wave.active {
    background-color: #00ff00;
  }
  
  @keyframes wave {
    0%, 100% {
      transform: scaleY(0.5);
    }
    50% {
      transform: scaleY(1);
    }
  }
  
  /* Meter indicator styles */
  .status-indicator.meter {
    justify-content: center;
  }
  
  .status-indicator.meter .meter-container {
    width: 100%;
    height: 20px;
    background-color: #f0f0f0;
    border-radius: 10px;
    overflow: hidden;
    position: relative;
  }
  
  .status-indicator.meter .meter-bar {
    height: 100%;
    background-color: #00ff00;
    transition: width 0.5s ease-in-out;
  }
  
  .status-indicator.meter .meter-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #000;
    font-weight: bold;
  }
  
  /* Matrix indicator styles */
  .status-indicator.matrix {
    justify-content: center;
  }
  
  .status-indicator.matrix .matrix-container {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 2px;
    width: 100%;
    max-width: 150px;
  }
  
  .status-indicator.matrix .matrix-cell {
    width: 100%;
    padding-bottom: 100%; /* Creates a square */
    background-color: #ff0000;
    border-radius: 2px;
    transition: background-color 0.3s ease;
  }
  
  .status-indicator.matrix .matrix-cell.active {
    background-color: #00ff00;
  }
  
  /* Heartbeat indicator styles */
  .status-indicator.heartbeat {
    justify-content: center;
  }
  
  .status-indicator.heartbeat .heartbeat {
    width: 100%;
    height: 40px;
  }
  
  .status-indicator.heartbeat polyline {
    stroke: #ff0000;
    stroke-width: 2;
    fill: none;
    stroke-linecap: round;
    stroke-linejoin: round;
    animation: heartbeat 1.5s ease-in-out infinite;
  }
  
  .status-indicator.heartbeat polyline.active {
    stroke: #00ff00;
  }
  
  @keyframes heartbeat {
    0%, 100% {
      stroke-width: 2;
    }
    50% {
      stroke-width: 3;
    }
  }
  
  /* Theme-specific styles */
  .endpoint.cyberpunk {
    background-color: rgba(0, 0, 0, 0.7);
    border: 2px solid #00ffff;
    box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
  }
  
  .endpoint.cyberpunk .success { background-color: rgba(0, 255, 0, 0.2); color: #00ff00; }
  .endpoint.cyberpunk .failure { background-color: rgba(255, 0, 0, 0.2); color: #ff0000; }
  
  .endpoint.modern {
    background-color: #ffffff;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  .endpoint.modern .success { background-color: #e8f5e9; color: #4caf50; }
  .endpoint.modern .failure { background-color: #ffebee; color: #f44336; }
  
  .endpoint.retro {
    background-color: #fdf6e3;
    border: 2px solid #002b36;
    box-shadow: 5px 5px 0px #002b36;
  }
  
  .endpoint.retro .success { background-color: #859900; color: #fdf6e3; }
  .endpoint.retro .failure { background-color: #dc322f; color: #fdf6e3; }
  
  .endpoint.minimalist {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
  }
  
  .endpoint.minimalist .success { background-color: #f0f0f0; color: #333333; }
  .endpoint.minimalist .failure { background-color: #f0f0f0; color: #333333; }
  
  .endpoint.dark {
    background-color: #2c2c2c;
    border: 1px solid #444444;
  }
  
  .endpoint.dark .success { background-color: #1b5e20; color: #ffffff; }
  .endpoint.dark .failure { background-color: #b71c1c; color: #ffffff; }
  
  .endpoint.light {
    background-color: #f5f5f5;
    border: 1px solid #e0e0e0;
  }
  
  .endpoint.light .success { background-color: #c8e6c9; color: #1b5e20; }
  .endpoint.light .failure { background-color: #ffcdd2; color: #b71c1c; }
  
  .endpoint.neon {
    background-color: rgba(12, 12, 29, 0.8);
    border: 2px solid #ff00ff;
    box-shadow: 0 0 20px #ff00ff, 0 0 40px #00ffff;
  }
  
  .endpoint.neon .success { background-color: rgba(0, 255, 255, 0.2); color: #00ffff; }
  .endpoint.neon .failure { background-color: rgba(255, 0, 255, 0.2); color: #ff00ff; }
  
  .endpoint.pastel {
    background-color: #ffffff;
    border: 1px solid #d4e3fc;
  }
  
  .endpoint.pastel .success { background-color: #d4e3fc; color: #5a8dee; }
  .endpoint.pastel .failure { background-color: #ffd4d4; color: #ff6b6b; }
  
  .endpoint.brutalist {
    background-color: #ffffff;
    border: 3px solid #000000;
    box-shadow: 10px 10px 0px #000000;
  }
  
  .endpoint.brutalist .success { background-color: #ffffff; color: #000000; border: 2px solid #000000; }
  .endpoint.brutalist .failure { background-color: #000000; color: #ffffff; }
  
  .endpoint.glassmorphism {
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  }
  
  .endpoint.glassmorphism .success { background: rgba(0, 255, 0, 0.2); color: #00ff00; }
  .endpoint.glassmorphism .failure { background: rgba(255, 0, 0, 0.2); color: #ff0000; }
  </style>