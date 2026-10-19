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
  value: number
  weight: number
  isFragile: boolean
  eta: number
}
type Board = {
  truck: { dimensions: Dimensions; maxCapacity: number }
  packages: Package[]
}
type SearchStep = {
  iteration: number
  score?: number
  bestScore?: number
  averageScore?: number
  acceptanceProbability?: number
  state: Board
}
type SolveResult = {
  algorithm?: string
  implemented?: boolean
  message?: string
  init?: Board
  steps?: SearchStep[]
  final?: Board
  initScore?: number
  finalScore?: number
  iterations?: number
  duration?: number
  sidewaysMoves?: number
  maxSideways?: number
  restarts?: number
  maxRestart?: number
  iterationsPerRestart?: number[]
  stuckFrequency?: number
  populationSize?: number
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
const saveJsonButton = document.querySelector<HTMLButtonElement>('#save-json')!
const solveButton = document.querySelector<HTMLButtonElement>('#solve')!
const algorithmSelect = document.querySelector<HTMLSelectElement>('#algorithm')!
const maxIterInput = document.querySelector<HTMLInputElement>('#max-iter')!
const maxSidewaysInput = document.querySelector<HTMLInputElement>('#max-sideways')!
const maxRestartInput = document.querySelector<HTMLInputElement>('#max-restart')!
const temperatureInput = document.querySelector<HTMLInputElement>('#temperature')!
const coolingRateInput = document.querySelector<HTMLInputElement>('#cooling-rate')!
const populationSizeInput = document.querySelector<HTMLInputElement>('#population-size')!
const sidewaysField = document.querySelector<HTMLElement>('#sideways-field')!
const restartField = document.querySelector<HTMLElement>('#restart-field')!
const temperatureField = document.querySelector<HTMLElement>('#temperature-field')!
const coolingField = document.querySelector<HTMLElement>('#cooling-field')!
const populationField = document.querySelector<HTMLElement>('#population-field')!
const statsContent = document.querySelector<HTMLDivElement>('#stats-content')!
const scoreChart = document.querySelector<SVGSVGElement>('#score-chart')!
const probabilityChart = document.querySelector<SVGSVGElement>('#probability-chart')!
const seedInput = document.querySelector<HTMLInputElement>('#seed')!
const truckWInput = document.querySelector<HTMLInputElement>('#truck-w')!
const truckLInput = document.querySelector<HTMLInputElement>('#truck-l')!
const truckHInput = document.querySelector<HTMLInputElement>('#truck-h')!
const truckCapacityInput = document.querySelector<HTMLInputElement>('#truck-capacity')!
const packageList = document.querySelector<HTMLTableSectionElement>('#package-list')!
const packageCount = document.querySelector<HTMLSpanElement>('#package-count')!
const packageForm = document.querySelector<HTMLFormElement>('#package-form')!
const packageTooltip = document.querySelector<HTMLDivElement>('#package-tooltip')!
const pkgIdInput = document.querySelector<HTMLInputElement>('#pkg-id')!
const pkgWInput = document.querySelector<HTMLInputElement>('#pkg-w')!
const pkgLInput = document.querySelector<HTMLInputElement>('#pkg-l')!
const pkgHInput = document.querySelector<HTMLInputElement>('#pkg-h')!
const pkgValueInput = document.querySelector<HTMLInputElement>('#pkg-value')!
const pkgWeightInput = document.querySelector<HTMLInputElement>('#pkg-weight')!
const pkgEtaInput = document.querySelector<HTMLInputElement>('#pkg-eta')!
const pkgFragileInput = document.querySelector<HTMLInputElement>('#pkg-fragile')!

// three js parts 
const packageGroup = new THREE.Group()
const truckGroup = new THREE.Group()
const scene = new THREE.Scene()
scene.background = new THREE.Color(0xd4d4d4)
scene.add(packageGroup)
scene.add(truckGroup)

const camera = new THREE.PerspectiveCamera(55, 1, 0.1, 1000)
camera.position.set(10, 10, 10)

const renderer = new THREE.WebGLRenderer()
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
viewport.appendChild(renderer.domElement)

const controls = new OrbitControls(camera, renderer.domElement)
const raycaster = new THREE.Raycaster()
const pointer = new THREE.Vector2()

const packageColors = [
  0x4a90e2,
  0xe57373,
  0x66bb6a,
  0xffb74d,
  0x9575cd,
  0x78909c,
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
    new THREE.LineBasicMaterial({ color: 0x222222 }),
  )
  mesh.add(outline)
  mesh.userData.package = pkg
  mesh.position.set(pkg["position"].x + w / 2, pkg["position"].y + h / 2, pkg["position"].z + l / 2)
  packageGroup.add(mesh)
}

function renderTruck(board: Board): void {
  truckGroup.clear()
  const { w, l, h } = board.truck.dimensions

  const truck = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(w, h, l)),
    new THREE.LineBasicMaterial({ color: 0x333333 }),
  )
  truck.position.set(w / 2, h / 2, l / 2)
  truckGroup.add(truck)

  const points: THREE.Vector3[] = []
  for (let x = 0; x <= w; x++) {
    points.push(new THREE.Vector3(x, 0, 0), new THREE.Vector3(x, 0, l))
    points.push(new THREE.Vector3(x, 0, 0), new THREE.Vector3(x, h, 0))
  }
  for (let z = 0; z <= l; z++) {
    points.push(new THREE.Vector3(0, 0, z), new THREE.Vector3(w, 0, z))
    points.push(new THREE.Vector3(0, 0, z), new THREE.Vector3(0, h, z))
  }
  for (let y = 0; y <= h; y++) {
    points.push(new THREE.Vector3(0, y, 0), new THREE.Vector3(w, y, 0))
    points.push(new THREE.Vector3(0, y, 0), new THREE.Vector3(0, y, l))
  }
  truckGroup.add(new THREE.LineSegments(
    new THREE.BufferGeometry().setFromPoints(points),
    new THREE.LineBasicMaterial({ color: 0x4b5563, transparent: true, opacity: 0.75 }),
  ))

  const addNumber = (value: number, x: number, y: number, z: number): void => {
    const canvas = document.createElement('canvas')
    canvas.width = 64
    canvas.height = 64
    const context = canvas.getContext('2d')!
    context.fillStyle = '#222222'
    context.font = '32px Arial'
    context.textAlign = 'center'
    context.textBaseline = 'middle'
    context.fillText(String(value), 32, 32)
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
      map: new THREE.CanvasTexture(canvas),
      depthTest: false,
    }))
    sprite.position.set(x, y, z)
    sprite.scale.set(0.45, 0.45, 0.45)
    truckGroup.add(sprite)
  }

  for (let x = 0; x <= w; x++) addNumber(x, x, -0.18, -0.25)
  for (let z = 1; z <= l; z++) addNumber(z, -0.25, -0.18, z)
  for (let y = 1; y <= h; y++) addNumber(y, -0.25, y, 0)

  controls.target.set(w / 2, h / 2, l / 2)
  const distance = Math.max(w, l, h) * 1.6
  camera.position.set(distance, distance * 0.8, distance)
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

function inputNumber(input: HTMLInputElement): number {
  return Number(input.value)
}

function makeBoaord(): Board {
  if (!selectedBoard) {
    selectedBoard = {
      truck: {
        dimensions: {
          w: inputNumber(truckWInput),
          l: inputNumber(truckLInput),
          h: inputNumber(truckHInput),
        },
        maxCapacity: inputNumber(truckCapacityInput),
      },
      packages: [],
    }
  }
  return selectedBoard
}

function renderPackageList(): void {
  const packages = selectedBoard?.packages ?? []
  packageCount.textContent = `${packages.length} item${packages.length === 1 ? '' : 's'}`
  packageList.innerHTML = ''

  if (packages.length === 0) {
    const row = packageList.insertRow()
    const cell = row.insertCell()
    cell.colSpan = 10
    cell.className = 'empty'
    cell.textContent = 'No packages yet'
    return
  }

  packages.forEach((pkg, index) => {
    const row = packageList.insertRow()
    const values = [
      pkg.id,
      `${pkg.dimensions.w}×${pkg.dimensions.l}×${pkg.dimensions.h}`,
      `${pkg.position.x}, ${pkg.position.y}, ${pkg.position.z}`,
      String(pkg.orientation),
      String(pkg.value),
      String(pkg.weight),
      String(pkg.eta),
      pkg.inTruck ? 'Inside' : 'Outside',
      pkg.isFragile ? 'Yes' : 'No',
    ]
    values.forEach((value) => {
      const cell = row.insertCell()
      cell.textContent = value
    })
    const action = row.insertCell()
    const remove = document.createElement('button')
    remove.type = 'button'
    remove.textContent = '×'
    remove.title = `Remove ${pkg.id}`
    remove.addEventListener('click', () => {
      selectedBoard?.packages.splice(index, 1)
      renderPackageList()
      solveButton.disabled = !selectedBoard?.packages.length
    })
    action.appendChild(remove)
  })
}

function loadBoardIntoEditor(board: Board): void {
  selectedBoard = board
  truckWInput.value = String(board.truck.dimensions.w)
  truckLInput.value = String(board.truck.dimensions.l)
  truckHInput.value = String(board.truck.dimensions.h)
  truckCapacityInput.value = String(board.truck.maxCapacity)
  frames = []
  packageGroup.clear()
  renderTruck(board)
  renderPackageList()
  statsContent.textContent = 'No result yet'
  scoreChart.style.display = 'none'
  probabilityChart.style.display = 'none'
  previousButton.disabled = true
  playButton.disabled = true
  nextButton.disabled = true
  solveButton.disabled = board.packages.length === 0
}

function updateParameterFields(): void {
  const algorithm = algorithmSelect.value
  sidewaysField.hidden = algorithm !== 'hill-climbing/sideways'
  restartField.hidden = algorithm !== 'hill-climbing/random-restart'
  temperatureField.hidden = algorithm !== 'simulated-annealing'
  coolingField.hidden = algorithm !== 'simulated-annealing'
  populationField.hidden = algorithm !== 'genetic-algorithm'
}

function renderStats(result: SolveResult): void {
  const lines = [
    `Algorithm: ${result.algorithm ?? algorithmSelect.options[algorithmSelect.selectedIndex].text}`,
    `Initial score: ${result.initScore ?? '-'}`,
    `Final score: ${result.finalScore ?? '-'}`,
    `Iterations: ${result.iterations ?? '-'}`,
    `Duration: ${result.duration === undefined ? '-' : `${result.duration.toFixed(4)} s`}`,
  ]

  if (result.sidewaysMoves !== undefined) lines.push(`Sideways moves: ${result.sidewaysMoves}`)
  if (result.maxSideways !== undefined) lines.push(`Maximum sideways: ${result.maxSideways}`)
  if (result.restarts !== undefined) lines.push(`Restarts: ${result.restarts}`)
  if (result.maxRestart !== undefined) lines.push(`Maximum restarts: ${result.maxRestart}`)
  if (result.iterationsPerRestart !== undefined) lines.push(`Iterations/restart: ${result.iterationsPerRestart.join(', ')}`)
  if (result.stuckFrequency !== undefined) lines.push(`Stuck frequency: ${result.stuckFrequency}`)
  if (result.populationSize !== undefined) lines.push(`Population: ${result.populationSize}`)
  statsContent.textContent = lines.join('\n')

  const scores = [
    result.initScore,
    ...(result.steps ?? []).map((step) => step.score ?? step.bestScore),
  ].filter((score): score is number => score !== undefined)
  const averageScores = (result.steps ?? [])
    .map((step) => step.averageScore)
    .filter((score): score is number => score !== undefined)

  if (scores.length < 2) {
    scoreChart.style.display = 'none'
    scoreChart.innerHTML = ''
  } else {
    const min = Math.min(...scores, ...averageScores)
    const max = Math.max(...scores, ...averageScores)
    const range = max - min || 1
    const points = scores.map((score, index) => {
      const x = 10 + index * 280 / (scores.length - 1)
      const y = 120 - (score - min) * 110 / range
      return `${x},${y}`
    }).join(' ')

    let chartLines = `<polyline points="${points}" fill="none" stroke="#4ade80" stroke-width="3" />`
    if (averageScores.length > 1) {
      const averagePoints = averageScores.map((score, index) => {
        const x = 10 + index * 280 / (averageScores.length - 1)
        const y = 120 - (score - min) * 110 / range
        return `${x},${y}`
      }).join(' ')
      chartLines += `<polyline points="${averagePoints}" fill="none" stroke="#facc15" stroke-width="3" />`
    }

    scoreChart.innerHTML = chartLines
    scoreChart.style.display = 'block'
  }

  const probabilities = (result.steps ?? [])
    .map((step) => step.acceptanceProbability)
    .filter((value): value is number => value !== undefined)
  if (probabilities.length > 1) {
    const points = probabilities.map((value, index) => {
      const x = 10 + index * 280 / (probabilities.length - 1)
      const y = 120 - value * 110
      return `${x},${y}`
    }).join(' ')
    probabilityChart.innerHTML = `<polyline points="${points}" fill="none" stroke="#38bdf8" stroke-width="3" />`
    probabilityChart.style.display = 'block'
  } else {
    probabilityChart.innerHTML = ''
    probabilityChart.style.display = 'none'
  }
}

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

  const params = new URLSearchParams({
    max_iter: maxIterInput.value,
    seed: seedInput.value,
  })
  if (algorithmSelect.value === 'hill-climbing/sideways') params.set('max_sideways', maxSidewaysInput.value)
  if (algorithmSelect.value === 'hill-climbing/random-restart') params.set('max_restart', maxRestartInput.value)
  if (algorithmSelect.value === 'simulated-annealing') {
    params.set('temperature', temperatureInput.value)
    params.set('cooling_rate', coolingRateInput.value)
  }
  if (algorithmSelect.value === 'genetic-algorithm') params.set('population_size', populationSizeInput.value)

  fetch(`http://localhost:6969/api/solve/${algorithmSelect.value}?${params}`, {
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
    if (result.implemented === false) {
      frames = []
      statsContent.textContent = result.message ?? 'Algorithm is not implemented yet.'
      scoreChart.style.display = 'none'
      probabilityChart.style.display = 'none'
      status.textContent = result.message ?? 'Not implemented yet'
      return
    }

    if (!result.init || !result.steps) throw new Error('Incomplete solver response')

    frames = [
      {
        iteration: 0,
        score: result.initScore ?? 0,
        state: result.init,
      },
      ...result.steps.map((step) => ({
        iteration: step.iteration,
        score: step.score ?? step.bestScore ?? 0,
        state: step.state,
      })),
    ]

    renderTruck(result.init)
    renderStats(result)
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

algorithmSelect.addEventListener('change', updateParameterFields)
updateParameterFields()

for (const input of [truckWInput, truckLInput, truckHInput, truckCapacityInput]) {
  input.addEventListener('change', () => {
    const board = makeBoaord()
    board.truck.dimensions = {
      w: inputNumber(truckWInput),
      l: inputNumber(truckLInput),
      h: inputNumber(truckHInput),
    }
    board.truck.maxCapacity = inputNumber(truckCapacityInput)
    renderTruck(board)
    status.textContent = 'Truck updated'
  })
}

packageForm.addEventListener('submit', (event) => {
  event.preventDefault()
  const board = makeBoaord()
  const id = pkgIdInput.value.trim()
  if (!id || board.packages.some((pkg) => pkg.id === id)) {
    status.textContent = 'Package ID must be unique'
    return
  }

  board.packages.push({
    id,
    dimensions: { w: inputNumber(pkgWInput), l: inputNumber(pkgLInput), h: inputNumber(pkgHInput) },
    position: { x: 0, y: 0, z: 0 },
    orientation: 0,
    value: inputNumber(pkgValueInput),
    weight: inputNumber(pkgWeightInput),
    isFragile: pkgFragileInput.checked,
    eta: inputNumber(pkgEtaInput),
    inTruck: false,
  })

  renderPackageList()
  solveButton.disabled = false
  pkgIdInput.value = `P${String(board.packages.length + 1).padStart(2, '0')}`
  status.textContent = `${id} added outside the truck`
})

renderer.domElement.addEventListener('pointermove', (event) => {
  const rect = renderer.domElement.getBoundingClientRect()
  pointer.x = (event.clientX - rect.left) / rect.width * 2 - 1
  pointer.y = -(event.clientY - rect.top) / rect.height * 2 + 1
  raycaster.setFromCamera(pointer, camera)
  const hit = raycaster.intersectObjects(packageGroup.children, true)[0]
  let object: THREE.Object3D | null = hit?.object ?? null
  while (object && !object.userData.package) object = object.parent

  const pkg = object?.userData.package as Package | undefined
  if (!pkg) {
    packageTooltip.style.display = 'none'
    return
  }

  packageTooltip.textContent = `${pkg.id}\nValue ${pkg.value} · Weight ${pkg.weight}\n${pkg.dimensions.w}×${pkg.dimensions.l}×${pkg.dimensions.h} · Orientation ${pkg.orientation}\nPosition ${pkg.position.x}, ${pkg.position.y}, ${pkg.position.z}${pkg.isFragile ? ' · Fragile' : ''}`
  packageTooltip.style.display = 'block'
  packageTooltip.style.left = `${event.clientX + 12}px`
  packageTooltip.style.top = `${event.clientY + 12}px`
})

renderer.domElement.addEventListener('pointerleave', () => {
  packageTooltip.style.display = 'none'
})

boardFileInput.addEventListener('change', async () => {
  const file = boardFileInput.files?.[0]
  if (!file) return

  try {
    const board = JSON.parse(await file.text()) as Board
    loadBoardIntoEditor(board)
    status.textContent = `${file.name} ready`
  } catch {
    selectedBoard = undefined
    solveButton.disabled = true
    status.textContent = 'Invalid JSON file'
  }
})

saveJsonButton.addEventListener('click', () => {
  const board = makeBoaord()
  board.truck.dimensions = {
    w: inputNumber(truckWInput),
    l: inputNumber(truckLInput),
    h: inputNumber(truckHInput),
  }
  board.truck.maxCapacity = inputNumber(truckCapacityInput)

  const url = URL.createObjectURL(new Blob(
    [JSON.stringify(board, null, 2)],
    { type: 'application/json' },
  ))
  const link = document.createElement('a')
  link.href = url
  link.download = 'truck-config.json'
  link.click()
  URL.revokeObjectURL(url)
  status.textContent = 'Configuration saved'
})

renderTruck(makeBoaord())
renderPackageList()
