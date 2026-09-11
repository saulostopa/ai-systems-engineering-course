import { defineConfig } from 'vitepress'

export default defineConfig({
  lang: 'pt-BR',
  title: 'Harness Foundation Course',
  description:
    'Curso de Harness Engineering para a Webmotors — construa harnesses confiáveis para qualquer time: dev, QA, games, finanças e comercial.',
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
  themeConfig: {
    logo: '/wm-mark.svg',
    nav: [
      { text: 'Aulas', link: '/lectures/' },
      { text: 'Projetos', link: '/projects/' },
      { text: 'Biblioteca', link: '/resources/' },
      { text: 'Skills', link: '/skills/' },
      { text: 'Design de Harnesses', link: '/harness-designs/' },
      { text: 'Referência', link: '/reference/' },
    ],
    sidebar: {
      '/lectures/': [
        {
          text: 'Aulas',
          items: [
            { text: 'Visão geral', link: '/lectures/' },
            { text: '01 · Por que agentes capazes ainda falham', link: '/lectures/lecture-01' },
            { text: '02 · O que é um harness, de fato', link: '/lectures/lecture-02' },
            { text: '03 · O repositório como sistema de registro', link: '/lectures/lecture-03' },
            { text: '04 · Por que um único arquivo de instruções falha', link: '/lectures/lecture-04' },
            { text: '05 · Continuidade em tarefas longas', link: '/lectures/lecture-05' },
            { text: '06 · Inicialização como fase própria', link: '/lectures/lecture-06' },
            { text: '07 · Excesso de autonomia e entrega incompleta', link: '/lectures/lecture-07' },
            { text: '08 · Feature lists como primitivas de harness', link: '/lectures/lecture-08' },
            { text: '09 · Declarar vitória cedo demais', link: '/lectures/lecture-09' },
            { text: '10 · Testes de ponta a ponta mudam o resultado', link: '/lectures/lecture-10' },
            { text: '11 · Observabilidade dentro do harness', link: '/lectures/lecture-11' },
            { text: '12 · Sessões terminam com estado limpo', link: '/lectures/lecture-12' },
            { text: '13 · De prompts manuais a loops autônomos', link: '/lectures/lecture-13' },
            { text: '14 · De loops únicos a engenharia de grafos', link: '/lectures/lecture-14' },
          ],
        },
      ],
      '/projects/': [
        {
          text: 'Projetos',
          items: [
            { text: 'Visão geral', link: '/projects/' },
            { text: 'Projeto 01 · Baseline vs. harness mínimo', link: '/projects/project-01' },
            { text: 'Projeto 02 · Harness básico instalável', link: '/projects/project-02' },
            { text: 'Projeto 03 · Harness de App com QA', link: '/projects/project-03' },
            { text: 'Projeto 04 · Harness de domínio (finanças/games/comercial)', link: '/projects/project-04' },
            { text: 'Projeto 05 · Area Copilot com RAG', link: '/projects/project-05' },
          ],
        },
      ],
      '/resources/': [
        {
          text: 'Biblioteca',
          items: [
            { text: 'Visão geral', link: '/resources/' },
            { text: 'Templates', link: '/resources/templates' },
            { text: 'Referências externas', link: '/resources/references' },
          ],
        },
      ],
      '/skills/': [
        {
          text: 'Skills',
          items: [
            { text: 'Visão geral', link: '/skills/' },
            { text: 'feature-report', link: '/skills/feature-report' },
            { text: 'feature-quiz', link: '/skills/feature-quiz' },
            { text: 'feature-flowchart', link: '/skills/feature-flowchart' },
            { text: 'feature-animation', link: '/skills/feature-animation' },
            { text: 'qa-playwright-e2e', link: '/skills/qa-playwright-e2e' },
            { text: 'qa-perf-triage', link: '/skills/qa-perf-triage' },
            { text: 'Criar uma skill nova', link: '/skills/how-to-create' },
          ],
        },
      ],
      '/harness-designs/': [
        {
          text: 'Design de Harnesses',
          items: [
            { text: 'Visão geral', link: '/harness-designs/' },
            { text: 'Harness básico (download)', link: '/harness-designs/basic-harness' },
            { text: 'Harness grande (multi-time)', link: '/harness-designs/enterprise-harness' },
            { text: 'App Harness (QA + navegação agêntica)', link: '/harness-designs/app-harness' },
            { text: 'RAG Harness & Area Copilots', link: '/harness-designs/rag-harness' },
            { text: 'Harnesses de domínio', link: '/harness-designs/domain-harnesses' },
          ],
        },
      ],
      '/reference/': [
        {
          text: 'Referência',
          items: [
            { text: 'Plano original', link: '/reference/plan' },
            { text: 'Repositórios do ecossistema', link: '/reference/repositories' },
          ],
        },
      ],
    },
    outline: {
      level: [2, 3],
      label: 'Nesta página',
    },
    search: {
      provider: 'local',
    },
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
})