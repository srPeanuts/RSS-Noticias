# Notícias de Portugal — guia de instalação

A app corre sozinha no GitHub, de graça. Seis vezes por dia, lê os feeds RSS dos jornais, vai buscar as capas, agrupa as notícias por tema e atualiza uma página web que abres no telemóvel ou no computador.

Só precisas de fazer isto uma vez (cerca de 15 minutos).

---

## Passo 1 — Criar conta no GitHub

1. Vai a **https://github.com/signup** e cria uma conta gratuita.
2. Confirma o email.

## Passo 2 — Criar o repositório (a "pasta" da app)

1. Depois de entrares, clica no **+** no canto superior direito e escolhe **New repository**.
2. Em **Repository name** escreve: `noticias`
3. Escolhe **Public**. O GitHub Pages gratuito só funciona com repositórios públicos. A página tem uma instrução para não aparecer no Google.
4. Marca a opção **Add a README file**.
5. Clica em **Create repository**.

## Passo 3 — Carregar os ficheiros

1. Descompacta o ficheiro `noticias-portugal.zip` no teu computador.
2. No repositório, clica em **Add file** → **Upload files**.
3. Abre a pasta descompactada, seleciona **tudo o que está lá dentro** (as pastas `.github`, `docs`, `scripts` e os ficheiros `fontes.json`, `requirements.txt`, `LEIA-ME.md`) e arrasta para a janela do browser.
4. Espera que termine e clica em **Commit changes** (botão verde, em baixo).

**Confirma:** na página do repositório tem de aparecer a pasta `.github`. Se não aparecer (há browsers que ignoram pastas começadas por ponto), faz assim:

- Clica em **Add file** → **Create new file**.
- No nome, escreve exatamente: `.github/workflows/atualizar.yml`
- Abre o ficheiro `atualizar.yml` do zip no Bloco de Notas, copia tudo e cola.
- Clica em **Commit changes**.

## Passo 4 — Dar permissão à app para guardar os dados

1. No repositório, vai a **Settings** (separador no topo) → **Actions** → **General** (menu à esquerda).
2. Desce até **Workflow permissions**.
3. Escolhe **Read and write permissions** e clica em **Save**.

## Passo 5 — Ligar a página web

1. Em **Settings**, clica em **Pages** (menu à esquerda).
2. Em **Source**, escolhe **Deploy from a branch**.
3. Em **Branch**, escolhe `main` e, ao lado, a pasta `/docs`. Clica em **Save**.
4. Passado 1 ou 2 minutos, aparece no topo o endereço da tua app. Vai ser algo como
   `https://O-TEU-UTILIZADOR.github.io/noticias/`

## Passo 6 — Primeira atualização

1. Vai ao separador **Actions**. Se aparecer um aviso a pedir para ativar os workflows, clica no botão verde para aceitar.
2. À esquerda, clica em **Atualizar notícias**.
3. À direita, clica em **Run workflow** → **Run workflow**.
4. Espera 1 a 2 minutos até aparecer um ✓ verde.
5. Abre o endereço da tua app. Já tens as notícias de hoje.

A partir daqui, a atualização é automática por volta das 7h, 10h, 13h, 16h, 19h e 22h.

**Dica:** no telemóvel, abre o endereço e escolhe "Adicionar ao ecrã principal". Fica com um ícone como se fosse uma app.

---

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
