Frontend dos Sub-19 do **CCDR Vila Cortez do Mondego**. Consultar o [README do projeto](../README.md) para configurar PostgreSQL, backend, variáveis de ambiente e executar os dois servidores no Windows.

A interface partilha a paleta clara vermelha, azul e amarela de `app/globals.css`, inspirada no emblema real do CCDR, e os componentes de `components/`. `app/players/page.tsx` gere o Plantel através do cliente tipado `lib/api.ts`; `app/manifest.ts` prepara os metadados PWA. Ver [layout e imagens](../LAYOUT_VALIDACAO.md) para consultar os tokens finais, associar fotos e emblemas e executar os testes.

`app/matches/page.tsx` lista e cria jogos; `app/matches/[match_id]` permite editar o jogo e guardar titulares/suplentes. Ver [validação de Jogos](../JOGOS_VALIDACAO.md). `npm run test:e2e` usa Microsoft Edge e um servidor de produção próprio na porta 3100 (executar o build primeiro).

`app/matches/[match_id]/live` controla o Jogo ao Vivo através de `lib/live.ts`: relógio reconstruído do backend, transições, eventos e timeline. Ver [validação do Jogo ao Vivo](../LIVE_VALIDACAO.md).

`app/statistics` apresenta resumo da época, comparação, rankings e fichas por jogador; `app/matches/[match_id]/stats` mostra comparação e timeline do jogo. Ambas usam `lib/statistics.ts`, sem bibliotecas de gráficos. Ver [validação de Estatísticas](../ESTATISTICAS_VALIDACAO.md).

As notas abaixo são as referências originais do template Next.js.

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
