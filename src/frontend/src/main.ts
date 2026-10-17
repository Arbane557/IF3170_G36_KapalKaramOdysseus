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
  orientation: number
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
const boardFileInput = document.querySelector<HTMLInputElement>('#board-file')!
const solveButton = document.querySelector<HTMLButtonElement>('#solve')!

// three js parts 
const packageGroup = new THREE.Group()
const truckGroup = new THREE.Group()
const scene = new THREE.Scene()
scene.background = new THREE.Color(0x676767)
scene.add(packageGroup)
scene.add(truckGroup)

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

function get_dim_on_rot(pos: Package): Dimensions {
  const { w, l, h } = pos.dimensions

        // {"w" : w, "l" : l, "h" : h},
        // {"w" : w, "l" : h, "h" : l},
        // {"w" : h, "l" : w, "h" : l},
        // {"w" : h, "l" : l, "h" : w},
        // {"w" : l, "l" : w, "h" : h},
        // {"w" : l, "l" : h, "h" : w}
  const orientations: Dimensions[] = [
    { w, l, h },
    { w, l: h, h: l },
    { w: h, l: w, h: l },
    { w: h, l, h: w },
    { w: l, l: w, h },
    { w: l, l: h, h: w }
  ]

  return orientations[pos.orientation]
}


// use ts to spawn the boxes
function addBox(pkg: Package, color: number): void {
  const { w, l, h } = get_dim_on_rot(pkg)

  const geometry = new THREE.BoxGeometry(w, h, l)
  const material = new THREE.MeshBasicMaterial({ color })
  const mesh = new THREE.Mesh(geometry, material)
  const outline = new THREE.LineSegments(
    new THREE.EdgesGeometry(geometry),
    new THREE.LineBasicMaterial({ color: 0x111827 }),
  )
  mesh.add(outline)
  mesh.position.set(pkg["position"].x + w / 2, pkg["position"].y + h / 2, pkg["position"].z + l / 2)
  packageGroup.add(mesh)
}

function renderTruck(board: Board): void {
  truckGroup.clear()
  const { w, l, h } = board.truck.dimensions

  const truck = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(w, h, l)),
    new THREE.LineBasicMaterial({ color: 0xffffff }),
  )
  truck.position.set(w / 2, h / 2, l / 2)
  truckGroup.add(truck)

  controls.target.set(w / 2, h / 2, l / 2)
  controls.update()
}

function renderPackages(board: Board): void {
  packageGroup.clear()
  board.packages.forEach((pkg, index) => {
    if (!pkg.inTruck) return
    const color = packageColors[index % packageColors.length]
    addBox(pkg, color)
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

let frames: Replay[] = []
let currentFrame = 0
let playbackTimer: number | undefined
let selectedBoard: Board | undefined

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
  playButton.disabled = frames.length <= 1
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

function runSolver(board: Board): void {
  stopPlayback()
  solveButton.disabled = true
  status.textContent = 'Solving...'

  fetch('http://localhost:6969/api/solve', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(board),
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
  .finally(() => {
    solveButton.disabled = false
  })
}

solveButton.addEventListener('click', () => {
  if (selectedBoard) runSolver(selectedBoard)
})

boardFileInput.addEventListener('change', async () => {
  const file = boardFileInput.files?.[0]
  if (!file) return

  try {
    selectedBoard = JSON.parse(await file.text()) as Board
    status.textContent = `${file.name} ready`
    solveButton.disabled = false
    previousButton.disabled = true
    playButton.disabled = true
    nextButton.disabled = true
  } catch {
    selectedBoard = undefined
    solveButton.disabled = true
    status.textContent = 'Invalid JSON file'
  }
})
