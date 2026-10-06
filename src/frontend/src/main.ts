import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import './style.css'

type Dimensions = { 
  w: number; 
  l: number; 
  h: number 
}
type Package = {
  dimensions: Dimensions
  position: { x: number; y: number; z: number }
  id: string
  inTruck: boolean
}
type Board = {
  truck: { dimensions: Dimensions }
  packages: Package[]
}
type SearchStep = {
  iteration: number
  score: number
  state: Board
}
type SolveResult = {
  init: Board
  steps: SearchStep[]
  final: Board
  initScore: number
  finalScore: number
  iterations: number
}
type Replay = {
  iteration: number
  score: number
  state: Board
}

const viewport = document.querySelector<HTMLDivElement>('#viewport')!
const status = document.querySelector<HTMLDivElement>('#status')!
const previousButton = document.querySelector<HTMLButtonElement>('#previous')!
const playButton = document.querySelector<HTMLButtonElement>('#play')!
const nextButton = document.querySelector<HTMLButtonElement>('#next')!

// three js parts 
const packageGroup = new THREE.Group()
const scene = new THREE.Scene()
scene.background = new THREE.Color(0x676767)
scene.add(packageGroup)

const camera = new THREE.PerspectiveCamera(55, 1, 0.1, 1000)
camera.position.set(10, 10, 10)

const renderer = new THREE.WebGLRenderer()
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
viewport.appendChild(renderer.domElement)

const controls = new OrbitControls(camera, renderer.domElement)

const packageColors = [
  0x38bdf8,
  0xfb7185,
  0x4ade80,
  0xfacc15,
  0xc084fc,
  0xfb923c,
]

// use ts to spawn the boxes
function addBox(dimensions: Dimensions, position: Package['position'], color: number): void {
  const { w, l, h } = dimensions
  const material = new THREE.MeshBasicMaterial({ color })
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, l), material)
  mesh.position.set(position.x + w / 2, position.y + h / 2, position.z + l / 2)
  packageGroup.add(mesh)
}

function renderTruck(board: Board): void {
  const { w, l, h } = board.truck.dimensions

  const truck = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(w, h, l)),
    new THREE.LineBasicMaterial({ color: 0xffffff }),
  )
  truck.position.set(w / 2, h / 2, l / 2)
  scene.add(truck)

  controls.target.set(w / 2, h / 2, l / 2)
  controls.update()
}

function renderPackages(board: Board): void {
  packageGroup.clear()
  board.packages.forEach((pkg, index) => {
    if (!pkg.inTruck) return
    const color = packageColors[index % packageColors.length]
    addBox(pkg.dimensions, pkg.position, color)
  })
}

function resize(): void {
  const width = viewport.clientWidth
  const height = viewport.clientHeight
  renderer.setSize(width, height, false)
  camera.aspect = width / height
  camera.updateProjectionMatrix()
}

window.addEventListener('resize', resize)
resize()
renderer.setAnimationLoop(() => {
  controls.update()
  renderer.render(scene, camera)
})

// fetch(`http://localhost:6969/api/board`)
//   .then((response) => {
//     if (!response.ok) throw new Error(`HTTP ${response.status}`)
//     return response.json() as Promise<Board>
//   })
//   .then((board) => {
//     renderBoard(board)
//     status.textContent = 'Board loaded'
//   })
//   .catch((error: unknown) => {
//     status.textContent = `Backend error: ${error instanceof Error ? error.message : String(error)}`
//   })

let frames: Replay[] = []
let currentFrame = 0
let playbackTimer: number | undefined

function showFrame(index: number): void {
  if (index < 0 || index >= frames.length) {
    return
  }

  currentFrame = index
  const frame = frames[currentFrame]

  renderPackages(frame.state)

  status.textContent =
    `Iteration ${frame.iteration} / ${frames.length - 1} | ` +
    `Score: ${frame.score}`

  previousButton.disabled = currentFrame === 0
  nextButton.disabled = currentFrame === frames.length - 1
}

function stopPlayback(): void {
  if (playbackTimer !== undefined) {
    window.clearInterval(playbackTimer)
    playbackTimer = undefined
  }

  playButton.textContent = 'Play'
}

function startPlayback(): void {
  if (currentFrame >= frames.length - 1) {
    showFrame(0)
  }

  playButton.textContent = 'Pause'

  playbackTimer = window.setInterval(() => {
    if (currentFrame >= frames.length - 1) {
      stopPlayback()
      return
    }

    showFrame(currentFrame + 1)
  }, 700)
}

previousButton.addEventListener('click', () => {
  stopPlayback()
  showFrame(currentFrame - 1)
})

nextButton.addEventListener('click', () => {
  stopPlayback()
  showFrame(currentFrame + 1)
})

playButton.addEventListener('click', () => {
  if (playbackTimer !== undefined) {
    stopPlayback()
  } else {
    startPlayback()
  }
})

fetch('http://localhost:6969/api/solve', {
  method: 'POST',
})
  .then((response) => {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    return response.json() as Promise<SolveResult>
  })
  .then((result) => {
    frames = [
      {
        iteration: 0,
        score: result.initScore,
        state: result.init,
      },
      ...result.steps.map((step) => ({
        iteration: step.iteration,
        score: step.score,
        state: step.state,
      })),
    ]

    renderTruck(result.init)
    showFrame(0)
  })
  .catch((error: unknown) => {
    status.textContent =
      `Backend error: ${
        error instanceof Error
          ? error.message
          : String(error)
      }`
  })
