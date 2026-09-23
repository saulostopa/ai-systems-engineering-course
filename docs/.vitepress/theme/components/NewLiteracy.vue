<script setup lang="ts">
/**
 * NewLiteracy — the argument for taking the course, stated once, without hedging.
 * Rendered under the feature grid on the home page.
 */
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useData } from 'vitepress'

const { lang } = useData()
const isPt = computed(() => lang.value.toLowerCase().startsWith('pt'))

const t = computed(() =>
  isPt.value
    ? {
        eyebrow: '2026 · a linha divisória',
        headLead: 'Não aprender a trabalhar com IA é',
        headAccent: 'o novo analfabetismo técnico.',
        lead: 'Os modelos já são bons o suficiente. O que separa quem entrega de quem só demonstra é o harness em volta deles — os arquivos, os trilhos e as verificações que transformam um modelo capaz em um trabalhador confiável. Isso é engenharia. Dá para aprender. Está aqui.',
        badLabel: 'Sem harness',
        goodLabel: 'Com harness',
        bad: [
          'Prompt, reza, remenda.',
          'O agente para em 60% e declara vitória.',
          'Ninguém reproduz o resultado de ontem.'
        ],
        good: [
          'O repositório é o sistema de registro.',
          'Feature lists fecham o ciclo — não o feeling.',
          'Mesma tarefa, mesmo resultado, toda execução.'
        ],
        stats: [
          { n: '14', l: 'aulas' },
          { n: '05', l: 'projetos práticos' },
          { n: '06', l: 'designs de harness' },
          { n: '08', l: 'skills prontas' }
        ],
        primary: 'Começar pela aula 01',
        primaryHref: '/pt-BR/lectures/lecture-01',
        secondary: 'Montar meu primeiro harness',
        secondaryHref: '/pt-BR/projects/project-01',
        footnote: 'Do zero ao primeiro harness rodando na sua máquina.'
      }
    : {
        eyebrow: '2026 · the dividing line',
        headLead: 'Not learning to work with AI is',
        headAccent: 'the new technical illiteracy.',
        lead: 'The models are already good enough. What separates the people who ship from the people who demo is the harness around them — the files, the rails and the checks that turn a capable model into a reliable worker. That is engineering. It is teachable. It is here.',
        badLabel: 'Without a harness',
        goodLabel: 'With a harness',
        bad: [
          'Prompt, pray, patch.',
          'The agent stops at 60% and declares victory.',
          'Nobody can reproduce yesterday’s result.'
        ],
        good: [
          'The repository is the system of record.',
          'Feature lists close the loop — not vibes.',
          'Same task, same result, every run.'
        ],
        stats: [
          { n: '14', l: 'lessons' },
          { n: '05', l: 'hands-on projects' },
          { n: '06', l: 'harness blueprints' },
          { n: '08', l: 'ready-made skills' }
        ],
        primary: 'Start with lesson 01',
        primaryHref: '/lectures/lecture-01',
        secondary: 'Build my first harness',
        secondaryHref: '/projects/project-01',
        footnote: 'From zero to a harness running on your own machine.'
      }
)

const root = ref<HTMLElement | null>(null)
const shown = ref(false)
let io: IntersectionObserver | null = null

onMounted(() => {
  if (!root.value) return
  if (!('IntersectionObserver' in window)) {
    shown.value = true
    return
  }
  io = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        shown.value = true
        io?.disconnect()
      }
    },
    { threshold: 0.12 }
  )
  io.observe(root.value)
})

onBeforeUnmount(() => io?.disconnect())
</script>

<template>
  <section ref="root" class="literacy" :class="{ 'is-shown': shown }">
    <div class="literacy-inner">
      <div class="slab">
        <span class="eyebrow">{{ t.eyebrow }}</span>

        <h2 class="head">
          <span>{{ t.headLead }}</span>
          <em>{{ t.headAccent }}</em>
        </h2>

        <p class="lead">{{ t.lead }}</p>

        <div class="split">
          <div class="col col-bad">
            <span class="col-label">{{ t.badLabel }}</span>
            <ul>
              <li v-for="line in t.bad" :key="line">{{ line }}</li>
            </ul>
          </div>
          <div class="col col-good">
            <span class="col-label">{{ t.goodLabel }}</span>
            <ul>
              <li v-for="line in t.good" :key="line">{{ line }}</li>
            </ul>
          </div>
        </div>

        <dl class="stats">
          <div v-for="s in t.stats" :key="s.l" class="stat">
            <dt>{{ s.n }}</dt>
            <dd>{{ s.l }}</dd>
          </div>
        </dl>

        <div class="cta">
          <a class="btn btn-primary" :href="t.primaryHref">{{ t.primary }}</a>
          <a class="btn btn-ghost" :href="t.secondaryHref">{{ t.secondary }}</a>
        </div>

        <p class="footnote">{{ t.footnote }}</p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.literacy {
  padding: 8px 24px 64px;
}

.literacy-inner {
  max-width: 1152px;
  margin: 0 auto;
}

/* Deliberately dark in both color modes — this block is a statement, not a card. */
.slab {
  position: relative;
  overflow: hidden;
  border-radius: 20px;
  padding: 56px 40px 48px;
  background:
    radial-gradient(120% 140% at 82% 0%, rgba(216, 31, 65, 0.28) 0%, rgba(216, 31, 65, 0) 58%),
    radial-gradient(90% 120% at 0% 100%, rgba(76, 76, 160, 0.22) 0%, rgba(76, 76, 160, 0) 55%),
    var(--ds-gray-950);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--ds-gray-100);
}

.slab::before {
  content: '';
  position: absolute;
  inset: 0 0 auto 0;
  height: 2px;
  background: linear-gradient(90deg, var(--ds-red-500), var(--ds-red-300) 45%, transparent 85%);
}

/* Reveal — each piece follows the one above it. */
.literacy .eyebrow,
.literacy .head,
.literacy .lead,
.literacy .split,
.literacy .stats,
.literacy .cta,
.literacy .footnote {
  opacity: 0;
  transform: translateY(14px);
  transition: opacity 0.6s ease, transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}

.literacy.is-shown .eyebrow { opacity: 1; transform: none; transition-delay: 0.02s; }
.literacy.is-shown .head { opacity: 1; transform: none; transition-delay: 0.08s; }
.literacy.is-shown .lead { opacity: 1; transform: none; transition-delay: 0.16s; }
.literacy.is-shown .split { opacity: 1; transform: none; transition-delay: 0.24s; }
.literacy.is-shown .stats { opacity: 1; transform: none; transition-delay: 0.32s; }
.literacy.is-shown .cta { opacity: 1; transform: none; transition-delay: 0.4s; }
.literacy.is-shown .footnote { opacity: 1; transform: none; transition-delay: 0.46s; }

.eyebrow {
  display: inline-block;
  font-family: var(--vp-font-family-mono);
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--ds-red-300);
  padding: 5px 10px;
  border: 1px solid rgba(228, 87, 112, 0.35);
  border-radius: 999px;
  margin-bottom: 26px;
}

.head {
  margin: 0;
  font-size: clamp(30px, 5.2vw, 56px);
  line-height: 1.06;
  letter-spacing: -0.035em;
  font-weight: 800;
  color: #fff;
  max-width: 30ch;
  text-wrap: balance;
}

/* Each half of the headline balances its own lines — no orphan words in
   either locale, whatever the string length turns out to be. */
.head span,
.head em {
  display: block;
  text-wrap: balance;
}

.head em {
  font-style: normal;
  color: var(--ds-red-400);
}

.lead {
  margin: 24px 0 0;
  max-width: 68ch;
  font-size: 17px;
  line-height: 1.65;
  color: var(--ds-gray-300);
}

.split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 40px;
}

.col {
  border-radius: 14px;
  padding: 22px 22px 20px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.07);
}

.col-good {
  background: rgba(216, 31, 65, 0.1);
  border-color: rgba(228, 87, 112, 0.28);
}

.col-label {
  display: block;
  font-family: var(--vp-font-family-mono);
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--ds-gray-400);
  margin-bottom: 14px;
}

.col-good .col-label {
  color: var(--ds-red-300);
}

.col ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.col li {
  position: relative;
  padding-left: 22px;
  font-size: 15px;
  line-height: 1.5;
  color: var(--ds-gray-400);
}

.col li + li {
  margin-top: 12px;
}

.col-bad li::before {
  content: '';
  position: absolute;
  left: 2px;
  top: 0.62em;
  width: 10px;
  height: 1.5px;
  background: var(--ds-gray-500);
}

.col-good li {
  color: var(--ds-gray-100);
}

.col-good li::before {
  content: '';
  position: absolute;
  left: 3px;
  top: 0.3em;
  width: 6px;
  height: 10px;
  border: solid var(--ds-red-300);
  border-width: 0 1.8px 1.8px 0;
  transform: rotate(42deg);
}

.stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin: 36px 0 0;
  padding: 24px 0 0;
  border-top: 1px solid rgba(255, 255, 255, 0.09);
}

.stat dt {
  font-size: 30px;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: #fff;
  font-variant-numeric: tabular-nums;
}

.stat dd {
  margin: 4px 0 0;
  font-size: 13px;
  line-height: 1.35;
  color: var(--ds-gray-400);
}

.cta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 36px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  padding: 0 24px;
  height: 46px;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  transition: transform 0.18s ease, background-color 0.18s ease, border-color 0.18s ease;
}

.btn-primary {
  background: var(--ds-red-500);
  color: #fff;
  box-shadow: 0 6px 24px rgba(216, 31, 65, 0.35);
}

.btn-primary:hover {
  background: var(--ds-red-400);
  transform: translateY(-1px);
}

.btn-ghost {
  color: var(--ds-gray-100);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.btn-ghost:hover {
  border-color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.06);
  transform: translateY(-1px);
}

.footnote {
  margin: 18px 0 0;
  font-size: 13px;
  color: var(--ds-gray-500);
}

@media (max-width: 860px) {
  .slab {
    padding: 40px 24px 36px;
    border-radius: 16px;
  }
  .split {
    grid-template-columns: 1fr;
  }
  .stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 20px 12px;
  }
  .btn {
    width: 100%;
  }
}

@media (max-width: 639px) {
  .literacy {
    padding: 0 24px 48px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .literacy .eyebrow,
  .literacy .head,
  .literacy .lead,
  .literacy .split,
  .literacy .stats,
  .literacy .cta,
  .literacy .footnote {
    opacity: 1;
    transform: none;
    transition: none;
  }
}
</style>
