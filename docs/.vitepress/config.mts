import { defineConfig } from 'vitepress'

const LOCALE_KEYS = ['root', 'pt-BR']

function localeKeyFor(relativePath: string): string {
  return LOCALE_KEYS.find((key) => key !== 'root' && relativePath.startsWith(`${key}/`)) ?? 'root'
}

function pathForLocale(relativePath: string, localeKey: string): string {
  const localeKeyIdx = LOCALE_KEYS.find((key) => key !== 'root' && relativePath.startsWith(`${key}/`))
  const base = localeKeyIdx ? relativePath.slice(localeKeyIdx.length + 1) : relativePath
  const path = base
    .replace(/(^|\/)index\.md$/, '$1')
    .replace(/\.md$/, '')
  return `${localeKey === 'root' ? '' : `/${localeKey}`}/${path}`.replace(/\/$/, '') || '/'
}

export default defineConfig({
  lang: 'en',
  title: 'Harness Foundation Course',
  description:
    'Webmotors Harness Engineering course — build reliable harnesses for any team: dev, QA, games, finance and commercial.',
  cleanUrls: true,
  lastUpdated: true,
  head: [
    ['meta', { name: 'theme-color', content: '#d81f41' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
    [
      'link',
      {
        rel: 'stylesheet',
        href: 'https://fonts.googleapis.com/css2?family=Figtree:ital,wght@0,300..900;1,300..900&display=swap',
      },
    ],
  ],
  locales: {
    root: {
      label: 'English',
      lang: 'en',
      link: '/',
      description:
        'Webmotors Harness Engineering course — build reliable harnesses for any team: dev, QA, games, finance and commercial.',
    },
    'pt-BR': {
      label: 'Português',
      lang: 'pt-BR',
      link: '/pt-BR/',
      description:
        'Curso de Harness Engineering para a Webmotors — construa harnesses confiáveis para qualquer time: dev, QA, games, finanças e comercial.',
      themeConfig: {
        nav: [
          { text: 'Aulas', link: '/pt-BR/lectures/' },
          { text: 'Projetos', link: '/pt-BR/projects/' },
          { text: 'Biblioteca', link: '/pt-BR/resources/' },
          { text: 'Skills', link: '/pt-BR/skills/' },
          { text: 'Design de Harnesses', link: '/pt-BR/harness-designs/' },
          { text: 'Referência', link: '/pt-BR/reference/' },
        ],
        sidebar: {
          '/pt-BR/lectures/': [
            {
              text: 'Aulas',
              items: [
                { text: 'Visão geral', link: '/pt-BR/lectures/' },
                { text: '01 · Por que agentes capazes ainda falham', link: '/pt-BR/lectures/lecture-01' },
                { text: '02 · O que é um harness, de fato', link: '/pt-BR/lectures/lecture-02' },
                { text: '03 · O repositório como sistema de registro', link: '/pt-BR/lectures/lecture-03' },
                { text: '04 · Por que um único arquivo de instruções falha', link: '/pt-BR/lectures/lecture-04' },
                { text: '05 · Continuidade em tarefas longas', link: '/pt-BR/lectures/lecture-05' },
                { text: '06 · Inicialização como fase própria', link: '/pt-BR/lectures/lecture-06' },
                { text: '07 · Excesso de autonomia e entrega incompleta', link: '/pt-BR/lectures/lecture-07' },
                { text: '08 · Feature lists como primitivas de harness', link: '/pt-BR/lectures/lecture-08' },
                { text: '09 · Declarar vitória cedo demais', link: '/pt-BR/lectures/lecture-09' },
                { text: '10 · Testes de ponta a ponta mudam o resultado', link: '/pt-BR/lectures/lecture-10' },
                { text: '11 · Observabilidade dentro do harness', link: '/pt-BR/lectures/lecture-11' },
                { text: '12 · Sessões terminam com estado limpo', link: '/pt-BR/lectures/lecture-12' },
                { text: '13 · De prompts manuais a loops autônomos', link: '/pt-BR/lectures/lecture-13' },
                { text: '14 · De loops únicos a engenharia de grafos', link: '/pt-BR/lectures/lecture-14' },
                { text: '15 · Do Markdown ao runtime executável', link: '/pt-BR/lectures/lecture-15' },
                { text: '16 · ADK 2 e os três padrões de orquestração', link: '/pt-BR/lectures/lecture-16' },
                { text: '17 · Construindo um Hard Harness', link: '/pt-BR/lectures/lecture-17' },
                { text: '18 · Executando o harness ADK com Ollama', link: '/pt-BR/lectures/lecture-18' },
              ],
            },
          ],
          '/pt-BR/projects/': [
            {
              text: 'Projetos',
              items: [
                { text: 'Visão geral', link: '/pt-BR/projects/' },
                { text: 'Projeto 01 · Baseline vs. harness mínimo', link: '/pt-BR/projects/project-01' },
                { text: 'Projeto 02 · Harness básico instalável', link: '/pt-BR/projects/project-02' },
                { text: 'Projeto 03 · Harness de App com QA', link: '/pt-BR/projects/project-03' },
                { text: 'Projeto 04 · Harness de domínio (finanças/games/comercial)', link: '/pt-BR/projects/project-04' },
                { text: 'Projeto 05 · Area Copilot com RAG', link: '/pt-BR/projects/project-05' },
                { text: 'Projeto 06 · Harness ADK + RAG + Jev', link: '/pt-BR/projects/project-06' },
                { text: 'Projeto 06B · ADK RAG com PostgreSQL', link: '/pt-BR/projects/project-06-postgres' },
                { text: 'Projeto 07 · Harness enterprise (multi-time)', link: '/pt-BR/projects/project-07' },
              ],
            },
          ],
          '/pt-BR/resources/': [
            {
              text: 'Biblioteca',
              items: [
                { text: 'Visão geral', link: '/pt-BR/resources/' },
                { text: 'Templates', link: '/pt-BR/resources/templates' },
                { text: 'Referências externas', link: '/pt-BR/resources/references' },
              ],
            },
          ],
          '/pt-BR/skills/': [
            {
              text: 'Skills',
              items: [
                { text: 'Visão geral', link: '/pt-BR/skills/' },
                { text: 'feature-report', link: '/pt-BR/skills/feature-report' },
                { text: 'feature-quiz', link: '/pt-BR/skills/feature-quiz' },
                { text: 'feature-flowchart', link: '/pt-BR/skills/feature-flowchart' },
                { text: 'feature-animation', link: '/pt-BR/skills/feature-animation' },
                { text: 'qa-playwright-e2e', link: '/pt-BR/skills/qa-playwright-e2e' },
                { text: 'qa-perf-triage', link: '/pt-BR/skills/qa-perf-triage' },
                { text: 'feature-archify', link: '/pt-BR/skills/feature-archify' },
                { text: 'skill-guard', link: '/pt-BR/skills/skill-guard' },
                { text: 'Criar uma skill nova', link: '/pt-BR/skills/how-to-create' },
              ],
            },
          ],
          '/pt-BR/harness-designs/': [
            {
              text: 'Design de Harnesses',
              items: [
                { text: 'Visão geral', link: '/pt-BR/harness-designs/' },
                { text: 'Harness básico (download)', link: '/pt-BR/harness-designs/basic-harness' },
                { text: 'Harness grande (multi-time)', link: '/pt-BR/harness-designs/enterprise-harness' },
                { text: 'App Harness (QA + navegação agêntica)', link: '/pt-BR/harness-designs/app-harness' },
                { text: 'RAG Harness & Area Copilots', link: '/pt-BR/harness-designs/rag-harness' },
                { text: 'Harness ADK + RAG + Jev', link: '/pt-BR/harness-designs/adk-rag-jev-harness' },
                { text: 'Harness ADK RAG com PostgreSQL', link: '/pt-BR/harness-designs/adk-rag-postgres-harness' },
                { text: 'Harnesses de domínio', link: '/pt-BR/harness-designs/domain-harnesses' },
                { text: 'Hard Harness (orquestração executável)', link: '/pt-BR/harness-designs/hard-harness' },
              ],
            },
          ],
          '/pt-BR/reference/': [
            {
              text: 'Referência',
              items: [
                { text: 'Plano original', link: '/pt-BR/reference/plan' },
                { text: 'Repositórios do ecossistema', link: '/pt-BR/reference/repositories' },
              ],
            },
          ],
        },
        outline: {
          level: [2, 3],
          label: 'Nesta página',
        },
        langMenuLabel: 'Trocar idioma',
        docFooter: {
          prev: 'Anterior',
          next: 'Próximo',
        },
        darkModeSwitchLabel: 'Tema',
        lightModeSwitchTitle: 'Alternar para o tema claro',
        darkModeSwitchTitle: 'Alternar para o tema escuro',
        footer: {
          message: 'Harness Foundation Course — Webmotors',
          copyright: 'Construído com VitePress e o design system Eleanor.',
        },
      },
    },
  },
  themeConfig: {
    logo: '/wm-mark.svg',
    nav: [
      { text: 'Lessons', link: '/lectures/' },
      { text: 'Projects', link: '/projects/' },
      { text: 'Library', link: '/resources/' },
      { text: 'Skills', link: '/skills/' },
      { text: 'Harness Designs', link: '/harness-designs/' },
      { text: 'Reference', link: '/reference/' },
    ],
    sidebar: {
      '/lectures/': [
        {
          text: 'Lessons',
          items: [
            { text: 'Overview', link: '/lectures/' },
            { text: '01 · Why capable agents still fail', link: '/lectures/lecture-01' },
            { text: '02 · What a harness actually is', link: '/lectures/lecture-02' },
            { text: '03 · The repository as system of record', link: '/lectures/lecture-03' },
            { text: '04 · Why a single instruction file fails', link: '/lectures/lecture-04' },
            { text: '05 · Continuity in long tasks', link: '/lectures/lecture-05' },
            { text: '06 · Initialization as its own phase', link: '/lectures/lecture-06' },
            { text: '07 · Too much autonomy and incomplete delivery', link: '/lectures/lecture-07' },
            { text: '08 · Feature lists as harness primitives', link: '/lectures/lecture-08' },
            { text: '09 · Declaring victory too early', link: '/lectures/lecture-09' },
            { text: '10 · End-to-end tests change the outcome', link: '/lectures/lecture-10' },
            { text: '11 · Observability inside the harness', link: '/lectures/lecture-11' },
            { text: '12 · Sessions end with clean state', link: '/lectures/lecture-12' },
            { text: '13 · From manual prompts to autonomous loops', link: '/lectures/lecture-13' },
            { text: '14 · From single loops to graph engineering', link: '/lectures/lecture-14' },
            { text: '15 · From Markdown to an executable runtime', link: '/lectures/lecture-15' },
            { text: '16 · ADK 2 and the three orchestration patterns', link: '/lectures/lecture-16' },
            { text: '17 · Building a Hard Harness', link: '/lectures/lecture-17' },
            { text: '18 · Running the ADK harness with Ollama', link: '/lectures/lecture-18' },
          ],
        },
      ],
      '/projects/': [
        {
          text: 'Projects',
          items: [
            { text: 'Overview', link: '/projects/' },
            { text: 'Project 01 · Baseline vs. minimal harness', link: '/projects/project-01' },
            { text: 'Project 02 · Installable basic harness', link: '/projects/project-02' },
            { text: 'Project 03 · App harness with QA', link: '/projects/project-03' },
            { text: 'Project 04 · Domain harness (finance/games/commercial)', link: '/projects/project-04' },
            { text: 'Project 05 · Area Copilot with RAG', link: '/projects/project-05' },
            { text: 'Project 06 · ADK + RAG + Jev harness', link: '/projects/project-06' },
            { text: 'Project 06B · ADK RAG with PostgreSQL', link: '/projects/project-06-postgres' },
            { text: 'Project 07 · Enterprise harness (multi-team)', link: '/projects/project-07' },
          ],
        },
      ],
      '/resources/': [
        {
          text: 'Library',
          items: [
            { text: 'Overview', link: '/resources/' },
            { text: 'Templates', link: '/resources/templates' },
            { text: 'External references', link: '/resources/references' },
          ],
        },
      ],
      '/skills/': [
        {
          text: 'Skills',
          items: [
            { text: 'Overview', link: '/skills/' },
            { text: 'feature-report', link: '/skills/feature-report' },
            { text: 'feature-quiz', link: '/skills/feature-quiz' },
            { text: 'feature-flowchart', link: '/skills/feature-flowchart' },
            { text: 'feature-animation', link: '/skills/feature-animation' },
            { text: 'qa-playwright-e2e', link: '/skills/qa-playwright-e2e' },
            { text: 'qa-perf-triage', link: '/skills/qa-perf-triage' },
            { text: 'feature-archify', link: '/skills/feature-archify' },
            { text: 'skill-guard', link: '/skills/skill-guard' },
            { text: 'Create a new skill', link: '/skills/how-to-create' },
          ],
        },
      ],
      '/harness-designs/': [
        {
          text: 'Harness Designs',
          items: [
            { text: 'Overview', link: '/harness-designs/' },
            { text: 'Basic harness (download)', link: '/harness-designs/basic-harness' },
            { text: 'Enterprise harness (multi-team)', link: '/harness-designs/enterprise-harness' },
            { text: 'App Harness (QA + agentic navigation)', link: '/harness-designs/app-harness' },
            { text: 'RAG Harness & Area Copilots', link: '/harness-designs/rag-harness' },
            { text: 'ADK + RAG + Jev Harness', link: '/harness-designs/adk-rag-jev-harness' },
            { text: 'ADK RAG PostgreSQL Harness', link: '/harness-designs/adk-rag-postgres-harness' },
            { text: 'Domain harnesses', link: '/harness-designs/domain-harnesses' },
            { text: 'Hard Harness (executable orchestration)', link: '/harness-designs/hard-harness' },
          ],
        },
      ],
      '/reference/': [
        {
          text: 'Reference',
          items: [
            { text: 'Original plan', link: '/reference/plan' },
            { text: 'Ecosystem repositories', link: '/reference/repositories' },
          ],
        },
      ],
    },
    outline: {
      level: [2, 3],
      label: 'On this page',
    },
    langMenuLabel: 'Switch language',
    search: {
      provider: 'local',
      options: {
        locales: {
          'pt-BR': {
            placeholder: 'Buscar na documentação',
            translations: {
              button: {
                buttonText: 'Buscar',
                buttonAriaLabel: 'Buscar na documentação',
              },
            },
          },
        },
      },
    },
    docFooter: {
      prev: 'Previous',
      next: 'Next',
    },
    darkModeSwitchLabel: 'Theme',
    lightModeSwitchTitle: 'Switch to light theme',
    darkModeSwitchTitle: 'Switch to dark theme',
    footer: {
      message: 'Harness Foundation Course — Webmotors',
      copyright: 'Built with VitePress and the Eleanor design system.',
    },
  },
  transformHead({ pageData }) {
    const localeKey = localeKeyFor(pageData.relativePath)
    const alternates: HeadConfig[] = [
      ['link', { rel: 'alternate', hreflang: 'x-default', href: pathForLocale(pageData.relativePath, 'root') }],
      ...LOCALE_KEYS.map(
        (key) =>
          ['link', {
            rel: 'alternate',
            hreflang: key === 'root' ? 'en' : 'pt-BR',
            href: pathForLocale(pageData.relativePath, key),
          }] as HeadConfig,
      ),
    ]
    return alternates
  },
})

type HeadConfig = [string, Record<string, string>]
