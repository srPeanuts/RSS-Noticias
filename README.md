# Notícias de Portugal

**Custos:** zero. O GitHub Actions e o GitHub Pages são gratuitos para repositórios públicos, e todas as fontes de dados são públicas e gratuitas.

App pessoal para acompanhar a atualidade portuguesa (política, governo, economia, sociedade e cultura) num só sítio: as capas dos jornais do dia, os temas mais falados, as histórias da semana e do mês, indicadores económicos oficiais e um resumo diário por email.

Corre sozinha no GitHub e **não tem custos**: não usa inteligência artificial paga, só Python e dados públicos (RSS dos jornais, VerCapas e Eurostat).

---

## O que a app faz

Seis vezes por dia (por volta das 7h, 10h, 13h, 16h, 19h e 22h), a app:

1. **Lê as notícias** dos feeds RSS de 15 órgãos de comunicação portugueses.
2. **Vai buscar as capas** dos jornais e revistas ao VerCapas.
3. **Classifica cada notícia** numa categoria: Política, Governo, Economia, Sociedade e Cultura ou Opinião. Desporto, meteorologia, entretenimento e notícias sobre outros países sem ligação a Portugal ficam de fora.
4. **Agrupa as notícias sobre o mesmo assunto.** Quando vários jornais falam do mesmo tema, as notícias juntam-se num só cartão.
5. **Ordena os temas por importância,** medida pelo número de jornais diferentes que falam de cada um.
6. **Atualiza a página web** e guarda o histórico, que alimenta as vistas Semana e Mês.

Uma vez por dia recolhe também os **indicadores económicos** do Eurostat e, **depois da primeira atualização da manhã**, envia o **resumo por email**. Se essa atualização falhar, tenta outra vez por volta das 9h30.

---

## Como usar a app

### Separadores

| Separador | O que mostra |
|---|---|
| **Hoje** | Capas do dia, temas em alta e os temas de cada categoria. As setas ‹ › mostram os dias anteriores. |
| **Semana** | As histórias dos últimos 7 dias, quem está nas notícias e os temas em alta. |
| **Mês** | O mesmo que a Semana, para os últimos 30 dias. |
| **Indicadores** | Inflação, desemprego, crescimento do PIB, Euribor a 12 meses e juros da dívida a 10 anos. |

### Categorias

Os botões no topo (**Todas, Política, Governo, Economia, Sociedade e Cultura, Opinião**) filtram o que aparece. Com **Todas**, cada categoria mostra os 5 temas principais (6 na Opinião); ao escolher uma categoria, mostra até 15. A escolha fica memorizada.

- **Governo:** notícias sobre a ação do Governo (ministros, Conselho de Ministros, decretos).
- **Política:** partidos, Parlamento, eleições e Presidente da República.
- **Opinião:** os artigos de opinião mais recentes, com o nome do autor.

### Os cartões de cada tema

- **Número à esquerda:** a posição do tema no ranking da categoria. O **nº 1** aparece em destaque, com o dobro da altura e os títulos de outras notícias sobre o mesmo assunto.
- **Barras cinzentas e "X fontes · Y notícias":** quantos jornais diferentes falam do tema. Quanto mais barras, mais importante.
- **Palavras-chave:** os termos que mais se repetem nas notícias do tema.
- **"Ler resumo completo":** mostra o resumo inteiro quando está cortado.
- **"Ver as N notícias":** abre a lista de todas as notícias do tema, com o jornal e a hora; cada título é um link para o artigo original.
- **"▲ em alta":** o tema está a ganhar cobertura face aos dias anteriores.

### Capas

Na vista **Hoje**, desliza as capas para o lado e toca numa para a ver em tamanho grande. Se a capa não for de hoje (é o caso dos semanários), aparece a data a vermelho por baixo.

### Menu "Fontes"

O botão **Fontes ▾** abre a lista de jornais, em dois grupos:

- **Notícias:** desmarca um jornal para deixares de ver as notícias dele. Os temas são reordenados só com as fontes escolhidas.
- **Capas:** desmarca as capas que não te interessam.

Quando há fontes ocultas, o botão mostra "Fontes · N ocultas" e aparece um aviso no topo. **Mostrar todas** repõe tudo. A escolha fica guardada no browser, por isso no telemóvel e no computador escolhes separadamente.

### Em alta

Temas cuja cobertura hoje é pelo menos o dobro da média dos três dias anteriores. O gráfico de barras mostra a cobertura dia a dia. Fica mais útil ao fim de uma semana de histórico.

### Quem está nas notícias (Semana e Mês)

As pessoas, partidos e instituições mencionados em mais notícias no período. Passa o dedo ou o rato por cima de uma barra para ver a contagem por dia.

### Gráfico de cobertura (Semana e Mês)

Cada história tem um pequeno gráfico de barras com a cobertura em cada dia do período. Uma barra por dia; os dias sem cobertura aparecem como um traço.

### Indicadores económicos

Cada cartão mostra o último valor, a variação face ao período anterior, a comparação com a zona euro (quando existe) e um gráfico dos últimos 2 anos. Passa o dedo ou o rato por cima do gráfico para ver o valor de cada mês.

- **Seta verde:** variação boa para a economia (por exemplo, o desemprego a descer).
- **Seta vermelha:** variação má (por exemplo, os juros a subir).
- **Seta cinzenta:** na inflação, porque o ideal é ficar estável perto dos 2%.

Os dados são do Eurostat e são mensais ou trimestrais, por isso mudam poucas vezes por mês.

---

## Resumo diário por email

Todos os dias, depois da primeira recolha da manhã (por volta das **7h**), chega um email com os temas em alta, os 3 temas principais de cada categoria, 3 artigos de opinião e os indicadores económicos. Se essa recolha falhar, o email tenta outra vez por volta das **9h30**, mas só se os dados desse dia já estiverem publicados.

### Configurar

Em **Settings → Secrets and variables → Actions**, separador **Secrets**:

| Nome | Valor |
|---|---|
| `EMAIL_UTILIZADOR` | A conta Gmail que envia |
| `EMAIL_PASSWORD` | A **palavra-passe de aplicação** do Gmail (criada em myaccount.google.com/apppasswords, com a verificação em 2 passos ativa) |
| `EMAIL_PARA` | Para onde enviar. Para vários endereços, separa-os por vírgulas: `um@exemplo.pt, outro@exemplo.pt` |

Opcional, no separador **Variables**: `SITE_URL` com o endereço da app, para o email ter o botão "Abrir a app".

Para usar outro servidor de email que não o Gmail, acrescenta os secrets `EMAIL_SMTP` (servidor) e `EMAIL_PORTA` (porta, normalmente 465 ou 587).

Para enviar um email de teste fora de horas: **Actions → Resumo diario por email → Run workflow**.

---

## Personalizar as fontes

Tudo está no ficheiro `fontes.json`.

- **`feeds`:** os feeds RSS. Cada linha tem o nome do jornal (`fonte`), o endereço (`url`) e, opcionalmente, uma `categoria` que ajuda a classificar as notícias desse feed (`politica`, `governo`, `economia` ou `sociedade`). Deixa `""` para a classificação ser só automática.
- **`capas`:** os jornais cujas capas aparecem. O `slug` é o nome que aparece no endereço do VerCapas; por exemplo, `https://www.vercapas.com/capa/visao.html` corresponde a `visao`.

Depois de alterar, faz commit e push. As alterações contam a partir da atualização seguinte.

---

## Estrutura do projeto

| Ficheiro / pasta | Para que serve |
|---|---|
| `fontes.json` | Lista de feeds RSS e de capas |
| `scripts/atualizar.py` | Recolhe as notícias e as capas, classifica, agrupa e gera os dados da página |
| `scripts/rede.py` | Pedidos HTTP com retries quando um site falha temporariamente |
| `scripts/indicadores.py` | Vai buscar os indicadores económicos ao Eurostat |
| `scripts/tendencias.py` | Calcula os temas em alta e quem está nas notícias |
| `scripts/enviar_email.py` | Monta e envia o resumo por email |
| `docs/index.html` | A página web da app |
| `docs/data/` | Dados que a página mostra (gerados automaticamente) |
| `dados/` | Histórico de notícias, temas e capas de cada dia (gerado automaticamente) |
| `tests/` | Testes da classificação, dos retries e do horário do email |
| `.github/workflows/atualizar.yml` | Agenda a atualização 6 vezes por dia |
| `.github/workflows/resumo-email.yml` | Envia o email após a atualização da manhã (com fallback às 9h30) |

---

## Se algo falhar

- **Fontes com erro:** no fundo da página aparece a lista das fontes que falharam na última atualização, com o código do erro. Um jornal pode ter mudado o endereço do RSS ou bloquear pedidos automáticos (erro 403); nesse caso, corrige ou retira a linha no `fontes.json`.
- **Atualização ou email falhados:** no separador **Actions**, uma execução com ✗ vermelho tem o detalhe do erro. Clica nela e depois no passo que falhou.
- **A página não mostra as alterações:** espera 1 a 2 minutos depois do push e recarrega com **Ctrl+F5**.
- **O email não chega:** confirma os secrets (os nomes têm de estar exatamente como na tabela acima) e procura na pasta de spam.
