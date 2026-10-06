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
}
type Board = {
  truck: { dimensions: Dimensions }
  packages: Package[]
}

const viewport = document.querySelector<HTMLDivElement>('#viewport')!
const status = document.querySelector<HTMLDivElement>('#status')!

// three js parts 
const scene = new THREE.Scene()
scene.background = new THREE.Color(0x676767)

const camera = new THREE.PerspectiveCamera(55, 1, 0.1, 1000)
camera.position.set(10, 10, 10)

const renderer = new THREE.WebGLRenderer()
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
viewport.appendChild(renderer.domElement)

const controls = new OrbitControls(camera, renderer.domElement)

const packageMaterial = new THREE.MeshBasicMaterial({ color: 0x38bdf8 })

// use ts to spawn the boxes
function addBox(dimensions: Dimensions, position: Package['position']): void {
  const { w, l, h } = dimensions
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, l), packageMaterial)
  mesh.position.set(position.x + w / 2, position.y + h / 2, position.z + l / 2)
  scene.add(mesh)
}

function renderBoard(board: Board): void {
  const { w, l, h } = board.truck.dimensions
  const truck = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(w, h, l)),
    new THREE.LineBasicMaterial({ color: 0xffffff }),
  )
  truck.position.set(w / 2, h / 2, l / 2)
  scene.add(truck)

  board.packages.forEach((item) => addBox(item.dimensions, item.position))
  controls.target.set(w / 2, h / 2, l / 2)
  controls.update()
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

fetch(`http://localhost:6969/api/board`)
  .then((response) => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    return response.json() as Promise<Board>
  })
  .then((board) => {
    renderBoard(board)
    status.textContent = 'Board loaded'
  })
  .catch((error: unknown) => {
    status.textContent = `Backend error: ${error instanceof Error ? error.message : String(error)}`
  })
