<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import type { Artifact } from '@/data/museumData'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

const props = defineProps<{
  artifact: Artifact
}>()

const emit = defineEmits<{
  close: []
}>()

const canvasContainer = ref<HTMLElement>()
const isLoading = ref(true)
const isAutoRotating = ref(true)
const isFullscreen = ref(false)

// Three.js variables
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let controls: OrbitControls
let mesh: THREE.Mesh | THREE.Group
let animationId: number

// Geometry Generators
const createCabbageGeometry = () => {
  const group = new THREE.Group()

  // Stalk/Base
  const stalkGeo = new THREE.CylinderGeometry(0.4, 0.6, 1.5, 16, 4)
  const positions = stalkGeo.attributes.position

  if (positions) {
    for (let i = 0; i < positions.count; i++) {
      const x = positions.getX(i)
      const y = positions.getY(i)
      const z = positions.getZ(i)
      // Add organic noise/distortion
      const noise = Math.sin(y * 3) * 0.1 + Math.cos(x * 5) * 0.05
      positions.setX(i, x + noise)
      positions.setZ(i, z + noise)
    }
  }
  stalkGeo.computeVertexNormals()
  const stalkMat = new THREE.MeshPhysicalMaterial({
    color: 0xffffff,
    transmission: 0.2, // Subsurface scattering feel
    opacity: 0.9,
    roughness: 0.2,
    metalness: 0.1,
    clearcoat: 0.5,
  })
  const stalk = new THREE.Mesh(stalkGeo, stalkMat)
  stalk.position.y = -0.5
  group.add(stalk)

  // Leaves
  const leafCount = 12
  for (let i = 0; i < leafCount; i++) {
    const leafGeo = new THREE.PlaneGeometry(1.2, 2.5, 12, 12)
    const pos = leafGeo.attributes.position

    if (pos) {
      for (let j = 0; j < pos.count; j++) {
        const x = pos.getX(j)
        const y = pos.getY(j)
        const z = pos.getZ(j)

        // Curl the leaf
        const curl = Math.pow(y + 1.25, 2) * 0.15
        pos.setZ(j, z + curl)

        // Wavy edges
        const wave = Math.sin(y * 5 + x * 3) * 0.1
        pos.setX(j, x + wave)
      }
    }
    leafGeo.computeVertexNormals()

    const leafMat = new THREE.MeshPhysicalMaterial({
      color: i < 4 ? 0xe8f5e9 : 0x43a047, // White to Green gradient approximation
      side: THREE.DoubleSide,
      roughness: 0.3,
      metalness: 0.0,
      transmission: 0.1,
      clearcoat: 0.3,
    })

    const leaf = new THREE.Mesh(leafGeo, leafMat)

    const angle = (i / leafCount) * Math.PI * 2
    leaf.rotation.y = angle
    leaf.rotation.x = 0.2 // Tilt out
    leaf.position.y = 0.2
    leaf.position.x = Math.sin(angle) * 0.3
    leaf.position.z = Math.cos(angle) * 0.3

    group.add(leaf)
  }

  // Insects (Simplified)
  const insectGeo = new THREE.SphereGeometry(0.08, 8, 8)
  const insectMat = new THREE.MeshStandardMaterial({ color: 0x5d4037 })
  const insect1 = new THREE.Mesh(insectGeo, insectMat)
  insect1.position.set(0.4, 0.8, 0.4)
  group.add(insect1)

  return group
}

const createDragonWallGeometry = () => {
  const group = new THREE.Group()

  // Wall Base
  const wallGeo = new THREE.BoxGeometry(6, 2.5, 0.5)
  const wallMat = new THREE.MeshStandardMaterial({
    color: 0x8d6e63,
    roughness: 0.9,
  })
  const wall = new THREE.Mesh(wallGeo, wallMat)
  group.add(wall)

  // Relief Panel
  const panelGeo = new THREE.PlaneGeometry(5.5, 2, 64, 32)
  const pos = panelGeo.attributes.position

  if (pos) {
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i)
      const y = pos.getY(i)

      // Create dragon-like waves
      const z = Math.sin(x * 3) * Math.cos(y * 2) * 0.15 + Math.sin(x * 10 + y * 5) * 0.05
      pos.setZ(i, z + 0.26) // Slightly in front of wall
    }
  }
  panelGeo.computeVertexNormals()

  const panelMat = new THREE.MeshPhysicalMaterial({
    color: 0x1565c0, // Blue glaze
    roughness: 0.2,
    metalness: 0.3,
    clearcoat: 0.8,
    clearcoatRoughness: 0.1,
  })
  const panel = new THREE.Mesh(panelGeo, panelMat)
  group.add(panel)

  // Roof
  const roofGeo = new THREE.CylinderGeometry(0.1, 0.1, 6.2, 3) // Triangular prism-ish
  const roofMat = new THREE.MeshStandardMaterial({ color: 0xffb300 })
  const roof = new THREE.Mesh(roofGeo, roofMat)
  roof.rotation.z = Math.PI / 2
  roof.rotation.y = Math.PI / 4 // Rotate to show edge
  roof.scale.set(1, 4, 4) // Flatten
  roof.position.y = 1.4
  group.add(roof)

  return group
}

const createGoldenCupGeometry = () => {
  const group = new THREE.Group()

  // Cup Body
  const points = []
  for (let i = 0; i < 20; i++) {
    const t = i / 19
    points.push(new THREE.Vector2(0.3 + t * 0.5, (t - 0.5) * 1.5))
  }
  const cupGeo = new THREE.LatheGeometry(points, 32)
  const cupMat = new THREE.MeshPhysicalMaterial({
    color: 0xffd700, // Gold
    metalness: 1.0,
    roughness: 0.15,
    clearcoat: 0.5,
  })
  const cup = new THREE.Mesh(cupGeo, cupMat)
  group.add(cup)

  // Gems (Simplified)
  const gemGeo = new THREE.SphereGeometry(0.08, 8, 8)
  const gemMatRed = new THREE.MeshPhysicalMaterial({
    color: 0xd50000,
    transmission: 0.5,
    roughness: 0,
  })
  const gemMatBlue = new THREE.MeshPhysicalMaterial({
    color: 0x2962ff,
    transmission: 0.5,
    roughness: 0,
  })

  for (let i = 0; i < 8; i++) {
    const angle = (i / 8) * Math.PI * 2
    const gem = new THREE.Mesh(gemGeo, i % 2 === 0 ? gemMatRed : gemMatBlue)
    gem.position.set(Math.cos(angle) * 0.6, 0.2, Math.sin(angle) * 0.6)
    group.add(gem)
  }

  // Handles
  const handleGeo = new THREE.TorusGeometry(0.25, 0.05, 8, 16, Math.PI)
  for (let i = 0; i < 2; i++) {
    const handle = new THREE.Mesh(handleGeo, cupMat)
    handle.rotation.z = Math.PI / 2
    handle.rotation.y = i * Math.PI
    handle.position.set(i === 0 ? 0.7 : -0.7, 0, 0)
    group.add(handle)
  }

  return group
}

const createVaseGeometry = () => {
  const points = []
  for (let i = 0; i <= 40; i++) {
    const t = i / 40
    const y = (t - 0.5) * 3
    // Complex vase profile
    let r = 0.5
    if (t < 0.1)
      r = 0.4 + t // Base
    else if (t < 0.3)
      r = 0.8 // Belly
    else if (t < 0.6)
      r = 0.4 // Neck
    else if (t < 0.8)
      r = 0.6 // Flare
    else r = 0.5 // Rim
    points.push(new THREE.Vector2(r, y))
  }

  const geo = new THREE.LatheGeometry(points, 64)

  // Create a colorful texture procedurally (simple way)
  const canvas = document.createElement('canvas')
  canvas.width = 512
  canvas.height = 512
  const ctx = canvas.getContext('2d')
  if (ctx) {
    // Background
    ctx.fillStyle = '#fff'
    ctx.fillRect(0, 0, 512, 512)

    // Bands
    const colors = ['#1a237e', '#b71c1c', '#fdd835', '#004d40']
    for (let i = 0; i < 8; i++) {
      const color = colors[i % colors.length]
      if (color) {
        ctx.fillStyle = color
        ctx.fillRect(0, i * 64, 512, 64)
      }

      // Patterns
      ctx.fillStyle = 'rgba(255,255,255,0.3)'
      for (let j = 0; j < 10; j++) {
        ctx.beginPath()
        ctx.arc(j * 50 + 25, i * 64 + 32, 10, 0, Math.PI * 2)
        ctx.fill()
      }
    }
  }
  const texture = new THREE.CanvasTexture(canvas)

  const mat = new THREE.MeshPhysicalMaterial({
    map: texture,
    roughness: 0.2,
    metalness: 0.1,
    clearcoat: 0.5,
  })

  return new THREE.Mesh(geo, mat)
}

const createArtifactGeometry = () => {
  const id = props.artifact.id
  if (id === 'artifact-4-4') return createCabbageGeometry()
  if (id === 'artifact-4-5') return createDragonWallGeometry()
  if (id === 'artifact-4-6') return createGoldenCupGeometry()
  if (id === 'artifact-4-7') return createVaseGeometry()
  return createVaseGeometry()
}

const init3DScene = () => {
  if (!canvasContainer.value) return

  // Scene setup
  scene = new THREE.Scene()
  // Use a dark radial gradient-like background or just dark gray
  scene.background = new THREE.Color(0x111111)

  // Fog for depth
  scene.fog = new THREE.Fog(0x111111, 5, 15)

  // Camera
  camera = new THREE.PerspectiveCamera(
    45,
    canvasContainer.value.clientWidth / canvasContainer.value.clientHeight,
    0.1,
    100,
  )
  camera.position.set(0, 0, 5)

  // Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(canvasContainer.value.clientWidth, canvasContainer.value.clientHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.2
  canvasContainer.value.appendChild(renderer.domElement)

  // Controls
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.minDistance = 2
  controls.maxDistance = 10
  controls.autoRotate = isAutoRotating.value
  controls.autoRotateSpeed = 2.0

  // Lighting - Studio Setup
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.4)
  scene.add(ambientLight)

  const mainLight = new THREE.SpotLight(0xffffff, 1.5)
  mainLight.position.set(5, 5, 5)
  mainLight.castShadow = true
  mainLight.shadow.mapSize.width = 2048
  mainLight.shadow.mapSize.height = 2048
  scene.add(mainLight)

  const rimLight = new THREE.SpotLight(0x4488ff, 1.0)
  rimLight.position.set(-5, 2, -5)
  scene.add(rimLight)

  const fillLight = new THREE.PointLight(0xffaa00, 0.5)
  fillLight.position.set(-3, -2, 3)
  scene.add(fillLight)

  // Floor (Shadow catcher)
  const planeGeo = new THREE.PlaneGeometry(20, 20)
  const planeMat = new THREE.ShadowMaterial({ opacity: 0.3 })
  const plane = new THREE.Mesh(planeGeo, planeMat)
  plane.rotation.x = -Math.PI / 2
  plane.position.y = -1.5
  plane.receiveShadow = true
  scene.add(plane)

  // Artifact
  const geometry = createArtifactGeometry()
  mesh = geometry as THREE.Mesh | THREE.Group

  // Center the mesh
  const box = new THREE.Box3().setFromObject(mesh)
  const center = box.getCenter(new THREE.Vector3())
  mesh.position.sub(center) // Center at origin

  // Enable shadows for all meshes in group
  mesh.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      child.castShadow = true
      child.receiveShadow = true
    }
  })

  scene.add(mesh)

  // Animation Loop
  const animate = () => {
    animationId = requestAnimationFrame(animate)
    controls.update()
    renderer.render(scene, camera)
  }
  animate()

  // Resize handler
  const handleResize = () => {
    if (!canvasContainer.value) return
    camera.aspect = canvasContainer.value.clientWidth / canvasContainer.value.clientHeight
    camera.updateProjectionMatrix()
    renderer.setSize(canvasContainer.value.clientWidth, canvasContainer.value.clientHeight)
  }
  window.addEventListener('resize', handleResize)

  // Done loading
  setTimeout(() => {
    isLoading.value = false
  }, 800)
}

// Watchers for controls
watch(isAutoRotating, (val) => {
  if (controls) controls.autoRotate = val
})

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    canvasContainer.value?.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

const resetView = () => {
  controls.reset()
  camera.position.set(0, 0, 5)
}

const zoomIn = () => {
  camera.position.multiplyScalar(0.9)
}

const zoomOut = () => {
  camera.position.multiplyScalar(1.1)
}

onMounted(() => {
  init3DScene()
})

onUnmounted(() => {
  cancelAnimationFrame(animationId)
  renderer?.dispose()
  controls?.dispose()
  // Clean up geometries/materials if needed
})
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/95 backdrop-blur-md">
    <div class="relative w-full h-full flex flex-col">
      <!-- Top Bar -->
      <div
        class="absolute top-0 left-0 right-0 z-20 p-6 flex justify-between items-start bg-gradient-to-b from-black/80 to-transparent pointer-events-none"
      >
        <div class="pointer-events-auto">
          <h2 class="text-4xl font-serif text-white mb-2 tracking-wide">{{ artifact.name }}</h2>
          <p class="text-gray-300 font-light text-lg">{{ artifact.nameEn }}</p>
          <div class="mt-4 flex gap-4 text-sm text-gray-400">
            <span class="px-3 py-1 border border-gray-600 rounded-full">{{ artifact.period }}</span>
            <span class="px-3 py-1 border border-gray-600 rounded-full">{{
              artifact.material
            }}</span>
          </div>
        </div>

        <button
          @click="emit('close')"
          class="pointer-events-auto w-12 h-12 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-all duration-300 group"
        >
          <span class="text-white text-2xl group-hover:rotate-90 transition-transform">×</span>
        </button>
      </div>

      <!-- Main Canvas -->
      <div ref="canvasContainer" class="flex-1 w-full h-full bg-[#111] cursor-move relative">
        <!-- Loading Overlay -->
        <div
          v-if="isLoading"
          class="absolute inset-0 flex items-center justify-center bg-black z-30"
        >
          <div class="flex flex-col items-center gap-4">
            <div
              class="w-12 h-12 border-4 border-gray-600 border-t-white rounded-full animate-spin"
            ></div>
            <p class="text-gray-400 tracking-widest text-sm">LOADING 3D MODEL</p>
          </div>
        </div>
      </div>

      <!-- Bottom Controls Bar -->
      <div
        class="absolute bottom-0 left-0 right-0 z-20 p-8 bg-gradient-to-t from-black/90 via-black/50 to-transparent pointer-events-none"
      >
        <div
          class="max-w-4xl mx-auto flex items-center justify-center gap-6 pointer-events-auto bg-black/40 backdrop-blur-md px-8 py-4 rounded-2xl border border-white/10"
        >
          <!-- Auto Rotate -->
          <button
            @click="isAutoRotating = !isAutoRotating"
            class="flex flex-col items-center gap-1 group min-w-[60px]"
            :class="isAutoRotating ? 'text-green-400' : 'text-white/70'"
          >
            <div
              class="w-10 h-10 rounded-full bg-white/5 group-hover:bg-white/10 flex items-center justify-center transition-colors"
            >
              <span class="text-xl">↻</span>
            </div>
            <span class="text-[10px] uppercase tracking-wider font-medium">Rotate</span>
          </button>

          <div class="w-px h-8 bg-white/10"></div>

          <!-- Zoom Controls -->
          <div class="flex gap-2">
            <button
              @click="zoomOut"
              class="w-10 h-10 rounded-full bg-white/5 hover:bg-white/10 text-white flex items-center justify-center transition-colors"
              title="Zoom Out"
            >
              <span class="text-xl">−</span>
            </button>
            <button
              @click="zoomIn"
              class="w-10 h-10 rounded-full bg-white/5 hover:bg-white/10 text-white flex items-center justify-center transition-colors"
              title="Zoom In"
            >
              <span class="text-xl">+</span>
            </button>
          </div>

          <div class="w-px h-8 bg-white/10"></div>

          <!-- Reset -->
          <button
            @click="resetView"
            class="flex flex-col items-center gap-1 group min-w-[60px] text-white/70 hover:text-white"
          >
            <div
              class="w-10 h-10 rounded-full bg-white/5 group-hover:bg-white/10 flex items-center justify-center transition-colors"
            >
              <span class="text-xl">⌖</span>
            </div>
            <span class="text-[10px] uppercase tracking-wider font-medium">Reset</span>
          </button>

          <!-- Fullscreen -->
          <button
            @click="toggleFullscreen"
            class="flex flex-col items-center gap-1 group min-w-[60px] text-white/70 hover:text-white"
          >
            <div
              class="w-10 h-10 rounded-full bg-white/5 group-hover:bg-white/10 flex items-center justify-center transition-colors"
            >
              <span class="text-xl">⛶</span>
            </div>
            <span class="text-[10px] uppercase tracking-wider font-medium">Full</span>
          </button>
        </div>

        <p class="text-center text-white/20 text-xs mt-4 tracking-widest uppercase">
          Interactive 3D Museum Viewer • Powered by Three.js
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Custom scrollbar for webkit if needed */
::-webkit-scrollbar {
  width: 0px;
}
</style>
