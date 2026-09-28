# Notícias de Portugal — guia de instalação

A app corre sozinha no GitHub, de graça. Seis vezes por dia, lê os feeds RSS dos jornais, vai buscar as capas, agrupa as notícias por tema e atualiza uma página web que abres no telemóvel ou no computador.

## O que vais ver

- **Hoje:** as capas dos jornais (toca numa para a ver em grande) e os temas do dia em Política, Economia e Sociedade e Cultura. Os temas estão ordenados pelo número de jornais que falam deles. As setas ‹ › mostram os dias anteriores.
- **Semana e Mês:** as histórias que se repetiram ao longo dos dias, com uma barra que mostra em que dias apareceram. Estas vistas ficam mais completas à medida que a app acumula dias.

## Personalizar

Tudo se muda no ficheiro `fontes.json`. No GitHub, abre o ficheiro, clica no lápis ✏️, altera e faz **Commit changes**.

- **Jornais (RSS):** acrescenta ou remove linhas em `feeds`.
- **Capas:** a lista `capas` usa o nome que aparece no endereço do VerCapas. Por exemplo, `https://www.vercapas.com/capa/visao.html` corresponde a `visao`.

## Se algo falhar

- No fundo da página aparece a lista das fontes que deram erro na última atualização. Um jornal pode mudar o endereço do RSS; nesse caso, basta atualizar o `fontes.json`.
- No separador **Actions**, uma execução com ✗ vermelho tem o detalhe do erro lá dentro. Copia esse texto e envia-mo, que eu ajudo a resolver.

**Custos:** zero. O GitHub Actions e o GitHub Pages são gratuitos para repositórios públicos.
