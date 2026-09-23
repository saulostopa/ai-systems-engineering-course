<script setup lang="ts">
/**
 * HarnessGate — hero visual for the Harness Foundation Course.
 *
 * States the thesis of the course in one image: a raw model on its own is an
 * entropy field — scattered, flickering, unpredictable. The harness is the gate
 * it passes through. What comes out the other side runs on rails: same lanes,
 * same speed, every time.
 *
 * Canvas 2D, DPR-aware, pauses off-screen, and degrades to a single static
 * frame when the visitor asks for reduced motion.
 */
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useData } from 'vitepress'

const { isDark, lang } = useData()

const host = ref<HTMLDivElement | null>(null)
const surface = ref<HTMLCanvasElement | null>(null)

const isPt = computed(() => lang.value.toLowerCase().startsWith('pt'))
const copy = computed(() =>
  isPt.value
    ? { left: 'modelo sozinho', gate: 'harness', right: 'trabalho confiável' }
    : { left: 'model alone', gate: 'harness', right: 'reliable work' }
)

/* ── Geometry, in normalized units (0..1 of the square side) ── */
const GATE_X = 0.5
const GATE_Y = 0.5
const TILE = 0.185
const ABSORB_R = 0.108
const LANES = 6
const LANE_GAP = 0.108
const CHAOS_COUNT = 72

/* Webmotors monogram, straight from /wm-mark.svg (32-unit viewBox space). */
const WM_D =
  'm74.872 63.939c0 2.2646-1.8947 4.0833-4.187 3.9623-2.1506-0.11064-3.7617-2.0399-3.7617-4.1836v-8.7682a2.9803 2.9803 0 0 0-2.9838-2.9803h-8.9549a2.9803 2.9803 0 0 0-2.9838 2.9803v11.97c0 2.2646-1.8982 4.0798-4.1905 3.9623-2.1471-0.1141-3.7583-2.0399-3.7583-4.187v-11.745a2.9838 2.9838 0 0 0-2.9873-2.9803h-8.948a2.9838 2.9838 0 0 0-2.9838 2.9803v8.9894c0 2.2646-1.8982 4.0833-4.1905 3.9623-2.1506-0.11064-3.7617-2.0399-3.7617-4.1836v-31.66c0-2.2612 1.8947-4.0833 4.187-3.9623 2.154 0.11064 3.7687 2.0399 3.7687 4.187v8.7647c0 1.6458 1.3311 2.9803 2.9803 2.9803h8.9549a2.9838 2.9838 0 0 0 2.9838-2.9803v-11.966c0-2.2612 1.8947-4.0798 4.1836-3.9623 2.154 0.11064 3.7687 2.0399 3.7687 4.187v11.745c0 1.6458 1.3311 2.9803 2.9803 2.9803h8.9549a2.9838 2.9838 0 0 0 2.9838-2.9803v-8.7647c0-2.1506 1.6112-4.0764 3.7617-4.187a3.9726 3.9726 0 0 1 4.187 3.9623v31.878z'

type Pt = { x: number; y: number }

type Palette = {
  dot: string
  chaos: [number, number, number]
  railLit: string
  flow: [number, number, number]
  ring: string
  glow0: string
  glow1: string
  tileTop: string
  tileBottom: string
}

const LIGHT: Palette = {
  dot: 'rgba(114,114,122,0.20)',
  chaos: [114, 114, 122],
  railLit: 'rgba(216,31,65,0.32)',
  flow: [216, 31, 65],
  ring: 'rgba(216,31,65,0.30)',
  glow0: 'rgba(216,31,65,0.11)',
  glow1: 'rgba(216,31,65,0)',
  tileTop: '#e53858',
  tileBottom: '#c4143a'
}

const DARK: Palette = {
  dot: 'rgba(162,162,169,0.17)',
  chaos: [162, 162, 169],
  railLit: 'rgba(229,56,88,0.34)',
  flow: [229, 56, 88],
  ring: 'rgba(229,56,88,0.34)',
  glow0: 'rgba(229,56,88,0.18)',
  glow1: 'rgba(229,56,88,0)',
  tileTop: '#e8455f',
  tileBottom: '#c4143a'
}

/* ── Path helpers ── */
function resample(pts: Pt[], n: number): Pt[] {
  const acc = [0]
  for (let i = 1; i < pts.length; i++) {
    acc.push(acc[i - 1] + Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y))
  }
  const total = acc[acc.length - 1] || 1
  const out: Pt[] = []
  let j = 0
  for (let i = 0; i < n; i++) {
    const target = (i / (n - 1)) * total
    while (j < acc.length - 2 && acc[j + 1] < target) j++
    const span = acc[j + 1] - acc[j] || 1
    const t = (target - acc[j]) / span
    out.push({
      x: pts[j].x + (pts[j + 1].x - pts[j].x) * t,
      y: pts[j].y + (pts[j + 1].y - pts[j].y) * t
    })
  }
  return out
}

/** The rails: a quadratic fan out of the gate, then dead-straight to the edge. */
function buildRails(): Pt[][] {
  const rails: Pt[][] = []
  for (let i = 0; i < LANES; i++) {
    const y = GATE_Y + (i - (LANES - 1) / 2) * LANE_GAP
    const p0 = { x: GATE_X + TILE / 2 + 0.004, y: GATE_Y }
    const c = { x: GATE_X + 0.12, y: GATE_Y }
    const p1 = { x: GATE_X + 0.19, y }
    const pts: Pt[] = []
    for (let s = 0; s <= 26; s++) {
      const t = s / 26
      const m = 1 - t
      pts.push({
        x: m * m * p0.x + 2 * m * t * c.x + t * t * p1.x,
        y: m * m * p0.y + 2 * m * t * c.y + t * t * p1.y
      })
    }
    pts.push({ x: 0.98, y })
    rails.push(resample(pts, 150))
  }
  return rails
}

function roundRectPath(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number
) {
  if (typeof (ctx as any).roundRect === 'function') {
    ctx.beginPath()
    ;(ctx as any).roundRect(x, y, w, h, r)
    return
  }
  ctx.beginPath()
  ctx.moveTo(x + r, y)
  ctx.arcTo(x + w, y, x + w, y + h, r)
  ctx.arcTo(x + w, y + h, x, y + h, r)
  ctx.arcTo(x, y + h, x, y, r)
  ctx.arcTo(x, y, x + w, y, r)
  ctx.closePath()
}

/** Soft round sprite, so a glow costs one drawImage instead of a shadowBlur. */
function makeSprite(rgb: [number, number, number]) {
  const size = 64
  const c = document.createElement('canvas')
  c.width = c.height = size
  const g = c.getContext('2d')!
  const grad = g.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2)
  const [r, gg, b] = rgb
  grad.addColorStop(0, `rgba(${r},${gg},${b},1)`)
  grad.addColorStop(0.16, `rgba(${r},${gg},${b},0.8)`)
  grad.addColorStop(0.46, `rgba(${r},${gg},${b},0.22)`)
  grad.addColorStop(1, `rgba(${r},${gg},${b},0)`)
  g.fillStyle = grad
  g.fillRect(0, 0, size, size)
  return c
}

type Chaos = {
  x: number
  y: number
  vx: number
  vy: number
  ang: number
  pull: number
  size: number
  flick: number
  phase: number
}
type Flow = { lane: number; u: number; speed: number; size: number; born: number }
type Ripple = { x: number; y: number; t: number }

onMounted(() => {
  const el = surface.value
  const box = host.value
  if (!el || !box) return

  const ctx = el.getContext('2d')
  if (!ctx) return

  const reduced = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false

  const rails = buildRails()
  const wmPath = typeof Path2D !== 'undefined' ? new Path2D(WM_D) : null

  let palette: Palette = LIGHT
  let chaosSprite = makeSprite(LIGHT.chaos)
  let flowSprite = makeSprite(LIGHT.flow)

  const syncPalette = () => {
    palette = isDark.value ? DARK : LIGHT
    chaosSprite = makeSprite(palette.chaos)
    flowSprite = makeSprite(palette.flow)
  }
  syncPalette()

  /* The scattered field: a loose grid, jittered so it never reads as a grid. */
  const dots: Pt[] = []
  for (let gx = 0; gx < 9; gx++) {
    for (let gy = 0; gy < 12; gy++) {
      dots.push({
        x: 0.035 + gx * 0.048 + (Math.random() - 0.5) * 0.028,
        y: 0.07 + gy * 0.076 + (Math.random() - 0.5) * 0.03
      })
    }
  }

  const spawnChaos = (fresh = false): Chaos => ({
    x: fresh ? Math.random() * 0.36 + 0.04 : 0.04 + Math.random() * 0.1,
    y: 0.12 + Math.random() * 0.76,
    vx: 0,
    vy: 0,
    ang: Math.random() * Math.PI * 2,
    pull: 0.7 + Math.random() * 0.8,
    size: 2.6 + Math.random() * 3.0,
    flick: 0.35 + Math.random() * 0.45,
    phase: Math.random() * Math.PI * 2
  })

  const chaos: Chaos[] = Array.from({ length: CHAOS_COUNT }, () => spawnChaos(true))
  const flow: Flow[] = []
  const ripples: Ripple[] = []
  let laneCursor = Math.floor(Math.random() * LANES)

  // Seed the rails so the very first frame is already alive.
  for (let i = 0; i < 14; i++) {
    flow.push({
      lane: i % LANES,
      u: Math.random(),
      speed: 0.0085 + Math.random() * 0.0035,
      size: 3.0 + Math.random() * 1.6,
      born: 1
    })
  }

  let side = 1
  let dpr = 1

  const resize = () => {
    const rect = box.getBoundingClientRect()
    side = Math.max(1, Math.min(rect.width, rect.height))
    dpr = Math.min(window.devicePixelRatio || 1, 2)
    el.width = Math.round(side * dpr)
    el.height = Math.round(side * dpr)
    el.style.width = `${side}px`
    el.style.height = `${side}px`
  }

  const emit = () => {
    laneCursor = (laneCursor + 1 + (Math.random() < 0.25 ? 1 : 0)) % LANES
    flow.push({
      lane: laneCursor,
      u: 0,
      speed: 0.0085 + Math.random() * 0.0035,
      size: 3.0 + Math.random() * 1.6,
      born: 0
    })
  }

  const step = (k: number) => {
    for (let i = 0; i < chaos.length; i++) {
      const p = chaos[i]
      p.ang += (Math.random() - 0.5) * 0.9 * k
      p.vx += Math.cos(p.ang) * 0.00024 * k
      p.vy += Math.sin(p.ang) * 0.00024 * k

      const dx = GATE_X - p.x
      const dy = GATE_Y - p.y
      const d = Math.hypot(dx, dy) || 1
      // The closer to the gate, the harder it pulls — a funnel, not a drift.
      const grip = 0.000085 * p.pull * (1 + 1.9 * Math.max(0, 1 - d / 0.42))
      p.vx += (dx / d) * grip * k
      p.vy += (dy / d) * grip * k

      if (p.x < 0.035) p.vx += 0.00035 * k
      if (p.y < 0.09) p.vy += 0.00035 * k
      if (p.y > 0.91) p.vy -= 0.00035 * k

      const damp = Math.pow(0.942, k)
      p.vx *= damp
      p.vy *= damp
      p.x += p.vx * k
      p.y += p.vy * k
      p.phase += 0.09 * k

      if (d < ABSORB_R) {
        ripples.push({ x: p.x, y: p.y, t: 0 })
        emit()
        chaos[i] = spawnChaos()
      }
    }

    for (let i = flow.length - 1; i >= 0; i--) {
      const f = flow[i]
      f.u += f.speed * k
      f.born = Math.min(1, f.born + 0.09 * k)
      if (f.u >= 1) flow.splice(i, 1)
    }

    for (let i = ripples.length - 1; i >= 0; i--) {
      ripples[i].t += 0.055 * k
      if (ripples[i].t >= 1) ripples.splice(i, 1)
    }
  }

  const halo = (img: HTMLCanvasElement, x: number, y: number, size: number, alpha: number) => {
    ctx.globalAlpha = alpha
    ctx.drawImage(img, x - size / 2, y - size / 2, size, size)
  }

  const core = (x: number, y: number, r: number, rgb: [number, number, number], alpha: number) => {
    ctx.globalAlpha = 1
    ctx.fillStyle = `rgba(${rgb[0]},${rgb[1]},${rgb[2]},${alpha})`
    ctx.beginPath()
    ctx.arc(x, y, r, 0, Math.PI * 2)
    ctx.fill()
  }

  const draw = (time: number) => {
    const S = side
    const scale = S / 440
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    ctx.clearRect(0, 0, S, S)

    const beat = (Math.sin(time / 1400) + 1) / 2

    /* 1 — entropy field */
    ctx.globalAlpha = 1
    ctx.fillStyle = palette.dot
    for (const d of dots) {
      ctx.beginPath()
      ctx.arc(d.x * S, d.y * S, 1.05, 0, Math.PI * 2)
      ctx.fill()
    }

    /* 2 — the rails */
    ctx.lineCap = 'round'
    const railGrad = ctx.createLinearGradient(GATE_X * S, 0, S, 0)
    railGrad.addColorStop(0, palette.railLit)
    railGrad.addColorStop(0.84, palette.railLit)
    railGrad.addColorStop(1, 'rgba(0,0,0,0)')
    ctx.strokeStyle = railGrad
    ctx.lineWidth = 1
    for (const rail of rails) {
      ctx.beginPath()
      ctx.moveTo(rail[0].x * S, rail[0].y * S)
      for (let j = 1; j < rail.length; j += 3) ctx.lineTo(rail[j].x * S, rail[j].y * S)
      ctx.stroke()
    }

    /* 3 — chaos particles: flickering, never settling */
    for (const p of chaos) {
      const flick = Math.max(0.12, 0.42 + Math.sin(p.phase) * 0.24 + p.flick * 0.28)
      const px = p.x * S
      const py = p.y * S
      halo(chaosSprite, px, py, p.size * scale * 3.4, flick * 0.34)
      core(px, py, Math.max(0.8, p.size * 0.38 * scale), palette.chaos, Math.min(1, flick * 1.15))
    }

    /* 4 — gate glow + sonar rings */
    const T = TILE * S
    const gx = GATE_X * S
    const gy = GATE_Y * S
    const glow = ctx.createRadialGradient(gx, gy, T * 0.25, gx, gy, T * (1.85 + beat * 0.3))
    glow.addColorStop(0, palette.glow0)
    glow.addColorStop(1, palette.glow1)
    ctx.globalAlpha = 1
    ctx.fillStyle = glow
    ctx.fillRect(gx - T * 2.6, gy - T * 2.6, T * 5.2, T * 5.2)

    ctx.strokeStyle = palette.ring
    ctx.lineWidth = 1
    for (let i = 0; i < 3; i++) {
      const r = (time / 2600 + i / 3) % 1
      const size = T * (1.08 + r * 1.65)
      ctx.globalAlpha = (1 - r) * (1 - r) * 0.5
      roundRectPath(ctx, gx - size / 2, gy - size / 2, size, size, (size / 32) * 8)
      ctx.stroke()
    }

    /* 5 — absorption ripples */
    ctx.lineWidth = 1.1
    for (const rp of ripples) {
      ctx.globalAlpha = (1 - rp.t) * 0.55
      ctx.beginPath()
      ctx.arc(rp.x * S, rp.y * S, rp.t * 0.05 * S, 0, Math.PI * 2)
      ctx.stroke()
    }
    ctx.globalAlpha = 1

    /* 6 — the tile: the brand mark *is* the gate */
    ctx.save()
    ctx.translate(gx - T / 2, gy - T / 2)
    ctx.scale(T / 32, T / 32)
    const tileFill = ctx.createLinearGradient(0, 0, 0, 32)
    tileFill.addColorStop(0, palette.tileTop)
    tileFill.addColorStop(1, palette.tileBottom)
    roundRectPath(ctx, 0, 0, 32, 32, 8)
    ctx.fillStyle = tileFill
    ctx.fill()
    if (wmPath) {
      ctx.translate(0.15, 0.16)
      ctx.scale(0.33, 0.33)
      ctx.fillStyle = '#ffffff'
      ctx.fill(wmPath)
    }
    ctx.restore()

    /* 7 — ordered output: heads with motion-blur tails, locked to their lane */
    const [fr, fg, fb] = palette.flow
    for (const f of flow) {
      const rail = rails[f.lane]
      const last = rail.length - 1
      const idx = Math.min(last, Math.max(0, Math.round(f.u * last)))
      const head = rail[idx]
      const fade = f.u > 0.82 ? 1 - (f.u - 0.82) / 0.18 : 1
      const alpha = Math.max(0, fade) * f.born

      for (let t = 1; t <= 5; t++) {
        const ti = idx - t * 4
        if (ti < 0) break
        ctx.globalAlpha = 1
        ctx.strokeStyle = `rgba(${fr},${fg},${fb},${alpha * (1 - t / 6) * 0.5})`
        ctx.lineWidth = 1.8 * (1 - t / 8) * scale
        ctx.beginPath()
        ctx.moveTo(rail[ti].x * S, rail[ti].y * S)
        const tj = Math.min(last, ti + 4)
        ctx.lineTo(rail[tj].x * S, rail[tj].y * S)
        ctx.stroke()
      }

      const hx = head.x * S
      const hy = head.y * S
      halo(flowSprite, hx, hy, f.size * scale * 4.4, alpha * 0.55)
      core(hx, hy, Math.max(0.9, f.size * 0.42 * scale), palette.flow, alpha)
    }
    ctx.globalAlpha = 1
  }

  let raf = 0
  let last = 0
  let visible = true

  const frame = (time: number) => {
    const dt = last ? time - last : 16.7
    last = time
    step(Math.min(dt / 16.667, 2.6))
    draw(time)
    raf = requestAnimationFrame(frame)
  }

  const start = () => {
    if (raf || reduced) return
    last = 0
    raf = requestAnimationFrame(frame)
  }
  const stop = () => {
    if (!raf) return
    cancelAnimationFrame(raf)
    raf = 0
  }

  const stopWatch = watch(isDark, () => {
    syncPalette()
    if (reduced) draw(0)
  })

  const ro = new ResizeObserver(() => {
    resize()
    if (!raf) draw(performance.now())
  })
  ro.observe(box)

  const io = new IntersectionObserver(
    ([entry]) => {
      visible = entry.isIntersecting
      if (visible) start()
      else stop()
    },
    { threshold: 0.02 }
  )
  io.observe(box)

  const onVisibility = () => {
    if (document.hidden || !visible) stop()
    else start()
  }
  document.addEventListener('visibilitychange', onVisibility)

  resize()
  if (reduced) {
    // One composed frame: the story still reads, nothing moves.
    for (let i = 0; i < 140; i++) step(1)
    draw(0)
  } else {
    start()
  }

  onBeforeUnmount(() => {
    stop()
    ro.disconnect()
    io.disconnect()
    document.removeEventListener('visibilitychange', onVisibility)
    stopWatch()
  })
})
</script>

<template>
  <div
    ref="host"
    class="harness-gate"
    role="img"
    :aria-label="`${copy.left} → ${copy.gate} → ${copy.right}`"
  >
    <canvas ref="surface" aria-hidden="true" />
    <span class="tag tag-left">{{ copy.left }}</span>
    <span class="tag tag-gate">{{ copy.gate }}</span>
    <span class="tag tag-right">{{ copy.right }}</span>
  </div>
</template>

<style scoped>
.harness-gate {
  position: relative;
  width: 100%;
  max-width: 540px;
  aspect-ratio: 1 / 1;
  margin: 0 auto;
  display: grid;
  place-items: center;
}

.harness-gate canvas {
  display: block;
}

.tag {
  position: absolute;
  font-family: var(--vp-font-family-mono);
  font-size: 10px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--vp-c-text-3);
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  animation: gate-tag-in 0.8s ease-out 0.5s forwards;
}

.tag-left {
  left: 5%;
  bottom: 11%;
}

.tag-right {
  right: 4%;
  bottom: 11%;
  color: var(--vp-c-brand-1);
}

.tag-gate {
  left: 50%;
  top: 61%;
  transform: translate(-50%, 6px);
  color: var(--vp-c-text-2);
  font-weight: 600;
  animation-name: gate-tag-in-center;
}

@keyframes gate-tag-in {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes gate-tag-in-center {
  from {
    opacity: 0;
    transform: translate(-50%, 6px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}

@media (max-width: 639px) {
  .tag {
    font-size: 9px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .tag {
    animation: none;
    opacity: 1;
    transform: translateY(0);
  }
  .tag-gate {
    transform: translate(-50%, 0);
  }
}
</style>
