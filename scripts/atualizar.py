"""
Notícias de Portugal — recolha e análise diária.

1. Lê os feeds RSS listados em fontes.json
2. Vai buscar as capas dos jornais (vercapas.com)
3. Classifica as notícias em política / economia / sociedade e cultura
4. Agrupa notícias de jornais diferentes que falam do mesmo assunto
5. Ordena os temas pela cobertura (quantos jornais falam deles)
6. Gera os ficheiros JSON que a página web (pasta docs/) mostra

Não usa nenhuma IA paga: tudo corre com Python + scikit-learn, de graça.
"""

import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import requests
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"            # histórico bruto (artigos e temas por dia)
SITE = RAIZ / "docs" / "data"     # o que a página web lê
LISBOA = ZoneInfo("Europe/Lisbon")
CABECALHOS = {"User-Agent": "Mozilla/5.0 (compatible; NoticiasPT/1.0; uso pessoal)"}

CATEGORIAS = ["politica", "economia", "sociedade"]

# --------------------------------------------------------------------------
# Texto
# --------------------------------------------------------------------------

STOPWORDS = set("""
a à ao aos as às até com como contra da das de del dela dele deles do dos e é em entre era eram essa esse esta está
estão este eu foi foram há isso isto já la lhe lhes mais mas me mesmo meu minha muito na nas nem no nos nós num numa
o os ou para pela pelas pelo pelos por qual quando que quem se sem ser será seu seus sua suas são só também te tem têm
ter um uma umas uns vai vão foi sobre após diz dizem disse ainda pode podem vez anos ano hoje ontem amanhã dia dias
novo nova novos novas sua seu há ser está estar sido sendo tinha todo toda todos todas outro outra outros outras
portugal português portuguesa portugueses portuguesas país vídeo veja fotos foto galeria direto live ao-vivo notícias
""".split())


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def limpar_html(texto: str) -> str:
    texto = re.sub(r"<[^>]+>", " ", unescape(texto or ""))
    return re.sub(r"\s+", " ", texto).strip()


STOP_NORM = {normalizar(p) for p in STOPWORDS}

# --------------------------------------------------------------------------
# Classificação por palavras-chave
# --------------------------------------------------------------------------

EXCLUIR = [
    "desporto", "futebol", "modalidades", "benfica", "sporting", "fc porto", "liga", "mundial de futebol",
    "mundo", "internacional", "globo", "europa", "eua", "estados unidos", "medio oriente", "ucrania", "russia",
    "opiniao", "podcast", "video", "radio", "palavras cruzadas", "meteorologia", "tempo", "horoscopo",
    "lifestyle", "gastronomia", "moda", "famosos", "televisao", "tv", "auto", "motores", "tecnologia",
    "jogos", "passatempos", "boa cama boa mesa", "inimigo publico",
]

PALAVRAS = {
    "politica": [
        "politica", "governo", "parlamento", "assembleia da republica", "deputado", "deputada", "deputados",
        "ministro", "ministra", "primeiro-ministro", "presidente da republica", "belem", "sao bento",
        "eleicoes", "eleitoral", "autarquicas", "legislativas", "presidenciais", "partido", "partidos",
        "oposicao", "coligacao", "moção", "mocao de censura", "votacao", "lei", "decreto", "promulga", "veto",
        "socialista", "social-democrata", "montenegro", "marcelo", "seguro", "ventura", "autarca", "camara municipal",
        "entre politicos", "politica nacional",
    ],
    "economia": [
        "economia", "economico", "economica", "mercados", "bolsa", "empresas", "empresa", "inflacao", "bce",
        "banco", "bancos", "juros", "euribor", "pib", "crescimento", "exportacoes", "impostos", "irs", "irc",
        "iva", "orcamento", "oe20", "defice", "divida", "salario", "salarios", "emprego", "desemprego",
        "trabalho", "greve", "pensoes", "reformas", "precos", "combustiveis", "energia", "tap", "habitacao",
        "rendas", "credito", "investimento", "financas", "fiscal", "negocios", "turismo", "industria",
        "mercados", "seguros", "imobiliario", "startup",
    ],
    "sociedade": [
        "sociedade", "pais", "cultura", "saude", "sns", "hospital", "hospitais", "medicos", "enfermeiros",
        "educacao", "escola", "escolas", "professores", "universidade", "ensino", "justica", "tribunal",
        "ministerio publico", "acusacao", "arguidos", "arguido", "acusados", "detido", "detidos", "policia", "psp", "gnr", "crime", "incendio", "incendios", "ambiente", "clima",
        "ciencia", "artes", "cinema", "musica", "livros", "literatura", "teatro", "museu", "exposicao",
        "festival", "patrimonio", "religiao", "igreja", "imigracao", "imigrantes", "aima", "seguranca social",
        "transportes", "comboios", "cp", "metro", "aeroporto", "local", "lisboa", "porto",
    ],
}

# Notícias sobre outros países: descartadas, a não ser que mencionem Portugal
ESTRANGEIRO = [
    "eua", "estados unidos", "trump", "casa branca", "washington", "biden", "china", "chines", "chinesa", "chineses", "chinesas", "americano", "americana", "norte-americano", "norte-americana", "pequim",
    "russia", "russo", "russa", "putin", "moscovo", "kremlin", "ucrania", "ucraniano", "kiev", "zelensky",
    "israel", "israelita", "gaza", "hamas", "netanyahu", "irao", "iraniano", "libano", "siria", "medio oriente",
    "brasil", "brasileiro", "brasileira", "brasileiros", "brasileiras", "lula", "bolsonaro", "venezuela", "colombia", "argentina", "mexico",
    "angola", "angolano", "mocambique", "mocambicano", "sao tome", "cabo verde", "guine-bissau", "timor",
    "espanha", "espanhol", "madrid", "sanchez", "franca", "frances", "francesa", "paris", "macron",
    "alemanha", "alemao", "berlim", "italia", "italiano", "reino unido", "londres", "britanico", "india", "japao",
    "coreia", "africa do sul", "turquia", "nato", "onu", "papa", "vaticano",
]
PORTUGAL = [
    "portugal", "portugues", "portuguesa", "portugueses", "portuguesas", "lisboa", "porto", "coimbra", "braga",
    "faro", "algarve", "acores", "madeira", "funchal", "governo portugues", "montenegro", "marcelo", "seguro",
    "assembleia da republica", "sns", "psp", "gnr", "luso", "lusa", "nacional", "tap", "cgd", "bcp",
]
# Títulos a ignorar (entretenimento, meteorologia, desporto que escapa às categorias)
EXCLUIR_TITULO = [
    "mtv", "video music awards", "taylor swift", "formula 1", "cartoon", "horoscopo", "aviso amarelo",
    "aviso laranja", "condicoes meteorologicas", "chuva e trovoada", "bola de ouro", "futebol", "benfica",
    "sporting", "fc porto", "selecao nacional", "liga dos campeoes",
]


def e_estrangeira(titulo: str, resumo: str) -> bool:
    t = normalizar(titulo)
    if not any(_contem(t, e) for e in ESTRANGEIRO):
        return False
    contexto = normalizar(f"{titulo} {resumo[:300]}")
    return not any(_contem(contexto, p) for p in PORTUGAL)


SIGLAS_POLITICA = {"PS", "PSD", "CDS", "IL", "BE", "PCP", "PAN", "JPP", "Livre", "Chega", "AD", "OE"}


def _contem(texto_norm: str, termo: str) -> bool:
    return re.search(r"(?<![a-z0-9])" + re.escape(normalizar(termo)) + r"(?![a-z0-9])", texto_norm) is not None


def classificar(titulo: str, resumo: str, cats_feed: list, categoria_forcada: str) -> str | None:
    """Devolve 'politica', 'economia', 'sociedade' ou None (descartar)."""
    cats_norm = normalizar(" | ".join(cats_feed))
    # Descartar desporto, internacional, opinião, etc. (pelas categorias do próprio jornal)
    if cats_feed and any(_contem(cats_norm, e) for e in EXCLUIR):
        tem_nacional = any(_contem(cats_norm, t) for t in ["politica", "economia", "sociedade", "pais", "cultura"])
        if not tem_nacional:
            return None
    titulo_norm = normalizar(titulo)
    if any(_contem(titulo_norm, e) for e in EXCLUIR_TITULO):
        return None
    if e_estrangeira(titulo, resumo):
        return None

    texto_norm = normalizar(f"{titulo} {resumo}")
    pontos = Counter()
    if categoria_forcada:
        pontos[categoria_forcada] += 2   # a secção do feed ajuda, mas o conteúdo pode vencer
    for cat, termos in PALAVRAS.items():
        for t in termos:
            if cats_feed and _contem(cats_norm, t):
                pontos[cat] += 3
            if _contem(texto_norm, t):
                pontos[cat] += 1
    tokens = set(re.findall(r"[A-Za-zÀ-ÿ]+", titulo))
    if tokens & SIGLAS_POLITICA:
        pontos["politica"] += 2
    if not pontos:
        return None
    return pontos.most_common(1)[0][0]

# --------------------------------------------------------------------------
# Recolha RSS
# --------------------------------------------------------------------------


def _texto(el, *nomes):
    for n in nomes:
        f = el.find(n)
        if f is not None and (f.text or "").strip():
            return f.text.strip()
    return ""


def _data(valor: str):
    if not valor:
        return None
    try:
        d = parsedate_to_datetime(valor)
    except Exception:
        try:
            d = datetime.fromisoformat(valor.replace("Z", "+00:00"))
        except Exception:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d


def ler_feed(feed: dict) -> list:
    r = requests.get(feed["url"], headers=CABECALHOS, timeout=25)
    r.raise_for_status()
    raiz = ET.fromstring(r.content)
    atom = "{http://www.w3.org/2005/Atom}"
    itens = raiz.findall(".//item") or raiz.findall(f".//{atom}entry")
    artigos = []
    for it in itens:
        titulo = limpar_html(_texto(it, "title", f"{atom}title"))
        link = _texto(it, "link")
        if not link:
            l = it.find(f"{atom}link")
            link = l.get("href", "") if l is not None else ""
        resumo = limpar_html(_texto(it, "description", f"{atom}summary", f"{atom}content"))[:3000]
        data = _data(_texto(it, "pubDate", f"{atom}published", f"{atom}updated",
                            "{http://purl.org/dc/elements/1.1/}date"))
        cats = [limpar_html(c.text or "") for c in it.findall("category")]
        cats += [c.get("term", "") for c in it.findall(f"{atom}category")]
        fonte = feed["fonte"]
        # Google Notícias: o título vem como "Título - Jornal"
        src = it.find("source")
        if src is not None and (src.text or "").strip():
            fonte = src.text.strip()
            titulo = re.sub(r"\s+-\s+" + re.escape(fonte) + r"$", "", titulo)
            resumo = ""
        if not titulo or not link:
            continue
        artigos.append({
            "titulo": titulo, "link": link, "resumo": resumo, "fonte": fonte,
            "data": (data or datetime.now(timezone.utc)).isoformat(),
            "cats_feed": [c for c in cats if c], "categoria_forcada": feed.get("categoria", ""),
        })
    return artigos


def recolher_artigos(config: dict) -> tuple[list, dict]:
    todos, estado = [], {}
    for feed in config["feeds"]:
        try:
            a = ler_feed(feed)
            todos += a
            estado[feed["url"]] = len(a)
            print(f"  ✓ {feed['fonte']:<22} {len(a):>3} artigos  {feed['url']}")
        except Exception as e:
            codigo = getattr(getattr(e, "response", None), "status_code", None)
            estado[feed["url"]] = f"erro HTTP {codigo}" if codigo else f"erro: {e.__class__.__name__}"
            print(f"  ✗ {feed['fonte']:<22} ERRO {e.__class__.__name__}: {str(e)[:80]}")
    return todos, estado

# --------------------------------------------------------------------------
# Capas
# --------------------------------------------------------------------------


def recolher_capas(config: dict) -> list:
    capas = []
    for c in config["capas"]:
        pagina = f"https://www.vercapas.com/capa/{c['slug']}.html"
        try:
            html = requests.get(pagina, headers=CABECALHOS, timeout=25).text
            m = re.search(r'property=["\']og:image["\']\s+content=["\']([^"\']+)', html) or \
                re.search(r'content=["\']([^"\']+)["\']\s+property=["\']og:image', html)
            if not m:
                m = re.search(r'(https://imgs\.vercapas\.com/covers/[^"\']+\.jpe?g)', html)
            if not m:
                raise ValueError("imagem não encontrada")
            miniatura = m.group(1)
            imagem = re.sub(r"/thumbc/\d+/", "/", miniatura)
            d = re.search(r"(\d{4}-\d{2}-\d{2})", imagem)
            capas.append({"nome": c["nome"], "slug": c["slug"], "imagem": imagem, "miniatura": miniatura,
                          "pagina": pagina, "data": d.group(1) if d else None})
            print(f"  ✓ capa {c['nome']}")
        except Exception as e:
            print(f"  ✗ capa {c['nome']}: {e}")
    return capas

# --------------------------------------------------------------------------
# Agrupar em temas
# --------------------------------------------------------------------------


def _vetorizar(textos: list):
    vec = TfidfVectorizer(preprocessor=normalizar, stop_words=sorted(STOP_NORM), ngram_range=(1, 2),
                          sublinear_tf=True, token_pattern=r"(?u)\b[a-z0-9][a-z0-9\-]+\b")
    return vec, vec.fit_transform(textos)


def _agrupar(X, limiar: float) -> np.ndarray:
    n = X.shape[0]
    if n == 1:
        return np.array([0])
    dist = np.clip(1 - cosine_similarity(X), 0, 2)
    modelo = AgglomerativeClustering(n_clusters=None, metric="precomputed", linkage="average",
                                     distance_threshold=limiar)
    return modelo.fit_predict(dist)


def _palavras_chave(vec, X, idx, k=4) -> list:
    centro = np.asarray(X[idx].mean(axis=0)).ravel()
    nomes = vec.get_feature_names_out()
    top = [nomes[i] for i in centro.argsort()[::-1][:k * 2] if centro[i] > 0]
    escolhidas = []
    for t in top:  # evita repetir "orcamento" e "orcamento estado"
        if not any(t in e or e in t for e in escolhidas):
            escolhidas.append(t)
    return escolhidas[:k]


def _categoria_maioritaria(membros: list, peso: str | None = None) -> str:
    c = Counter()
    for m in membros:
        c[m["categoria"]] += m[peso] if peso else 1
    # em caso de empate, ordem de preferência: política, economia, sociedade
    return max(CATEGORIAS, key=lambda k: (c[k], -CATEGORIAS.index(k)))


def temas_do_dia(artigos: list) -> list:
    """Agrupa os artigos de um dia em temas e ordena por importância."""
    temas = []
    grupo = []
    for a in artigos:
        # reclassifica sempre, para que afinações às regras se apliquem também ao histórico
        cat = classificar(a["titulo"], a.get("resumo", ""), a.get("cats_feed", []),
                          a.get("categoria_forcada") if "categoria_forcada" in a else a.get("categoria", ""))
        if cat:
            grupo.append(dict(a, categoria=cat))
    if grupo:
        textos = [f"{a['titulo']} {a['titulo']} {a['resumo'][:200]}" for a in grupo]
        vec, X = _vetorizar(textos)
        rotulos = _agrupar(X, limiar=0.86)
        for r in set(rotulos):
            idx = [i for i, x in enumerate(rotulos) if x == r]
            membros = [grupo[i] for i in idx]
            fontes = sorted({m["fonte"] for m in membros})
            # título representativo: o mais parecido com os outros (preferindo jornais, não o Google)
            sim = cosine_similarity(X[idx]).mean(axis=1)
            ordem = sorted(range(len(idx)), key=lambda j: (membros[j]["fonte"].startswith("Google"), -sim[j]))
            principal = membros[ordem[0]]
            temas.append({
                "titulo": principal["titulo"],
                "resumo": principal["resumo"],
                "categoria": _categoria_maioritaria(membros),
                "palavras": _palavras_chave(vec, X, idx),
                "fontes": fontes,
                "n_fontes": len(fontes),
                "n_artigos": len(membros),
                "pontuacao": len(fontes) * 3 + len(membros),
                "artigos": sorted(
                    [{"titulo": m["titulo"], "link": m["link"], "fonte": m["fonte"], "data": m["data"]}
                     for m in membros], key=lambda m: m["data"], reverse=True)[:12],
            })
    temas.sort(key=lambda t: t["pontuacao"], reverse=True)
    return temas


def temas_do_periodo(dias: dict) -> list:
    """Junta os temas de vários dias em 'histórias' (semana / mês)."""
    lista = [dict(t, dia=d) for d, ts in dias.items() for t in ts if t["n_fontes"] >= 2 or t["n_artigos"] >= 3]
    if not lista:
        return []
    historias = []
    grupo = lista
    if grupo:
        textos = [" ".join([t["titulo"]] * 2 + [a["titulo"] for a in t["artigos"][:6]] + t["palavras"] * 2)
                  for t in grupo]
        vec, X = _vetorizar(textos)
        rotulos = _agrupar(X, limiar=0.80)
        for r in set(rotulos):
            membros = [grupo[i] for i, x in enumerate(rotulos) if x == r]
            idx = [i for i, x in enumerate(rotulos) if x == r]
            membros.sort(key=lambda t: t["pontuacao"], reverse=True)
            dias_presentes = sorted({m["dia"] for m in membros})
            fontes = sorted({f for m in membros for f in m["fontes"]})
            linha = {}
            for m in membros:
                if m["dia"] not in linha or m["pontuacao"] > linha[m["dia"]]["pontuacao"]:
                    linha[m["dia"]] = {"dia": m["dia"], "titulo": m["titulo"], "pontuacao": m["pontuacao"]}
            artigos, vistos = [], set()
            for m in membros:
                for a in m["artigos"]:
                    if a["link"] not in vistos:
                        vistos.add(a["link"])
                        artigos.append(a)
            historias.append({
                "titulo": membros[0]["titulo"],
                "resumo": membros[0].get("resumo", ""),
                "categoria": _categoria_maioritaria(membros, peso="pontuacao"),
                "palavras": _palavras_chave(vec, X, idx),
                "dias": dias_presentes,
                "n_dias": len(dias_presentes),
                "fontes": fontes,
                "n_fontes": len(fontes),
                "n_artigos": sum(m["n_artigos"] for m in membros),
                "pontuacao": sum(m["pontuacao"] for m in membros) + 5 * (len(dias_presentes) - 1),
                "cronologia": sorted(linha.values(), key=lambda x: x["dia"]),
                "artigos": sorted(artigos, key=lambda a: a["data"], reverse=True)[:15],
            })
    historias.sort(key=lambda h: h["pontuacao"], reverse=True)
    return historias

# --------------------------------------------------------------------------
# Guardar / carregar
# --------------------------------------------------------------------------


def ler_json(caminho: Path, padrao):
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def escrever_json(caminho: Path, dados, compacto=False):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=None if compacto else 1), encoding="utf-8")


def resumo_publico(temas: list, por_categoria: int) -> dict:
    return {cat: [t for t in temas if t["categoria"] == cat][:por_categoria] for cat in CATEGORIAS}


def main(artigos_teste: list | None = None, capas_teste: list | None = None):
    config = ler_json(RAIZ / "fontes.json", None)
    agora = datetime.now(LISBOA)
    hoje = agora.date().isoformat()
    print(f"== Atualização {agora:%Y-%m-%d %H:%M} (Lisboa) ==")

    # 1. Recolher
    if artigos_teste is not None:
        novos, estado = artigos_teste, {"teste": len(artigos_teste)}
    else:
        print("Feeds RSS:")
        novos, estado = recolher_artigos(config)
    print("Capas:")
    capas = capas_teste if capas_teste is not None else recolher_capas(config)

    # 2. Classificar e juntar ao histórico de cada dia (os feeds só guardam as últimas horas,
    #    por isso o script corre várias vezes por dia e vai acumulando)
    limite = agora - timedelta(days=2)
    por_dia = {}
    for a in novos:
        d = datetime.fromisoformat(a["data"]).astimezone(LISBOA)
        if d < limite:
            continue
        cat = classificar(a["titulo"], a["resumo"], a["cats_feed"], a["categoria_forcada"])
        if not cat:
            continue
        a = dict(a, categoria=cat)
        por_dia.setdefault(d.date().isoformat(), []).append(a)

    dias_tocados = set(por_dia) | {hoje}
    for dia in dias_tocados:
        f = DADOS / "artigos" / f"{dia}.json"
        existentes = {a["link"]: a for a in ler_json(f, [])}
        for a in por_dia.get(dia, []):
            existentes.setdefault(a["link"], a)
        artigos_dia = list(existentes.values())
        escrever_json(f, artigos_dia)
        temas = temas_do_dia(artigos_dia)
        escrever_json(DADOS / "temas" / f"{dia}.json", temas)
        print(f"Dia {dia}: {len(artigos_dia)} artigos → {len(temas)} temas")

    # 3. Capas do dia
    f_capas = DADOS / "capas" / f"{hoje}.json"
    if capas:
        escrever_json(f_capas, capas)
    capas_hoje = ler_json(f_capas, [])
    recente = (agora.date() - timedelta(days=8)).isoformat()
    capas_validas = [c for c in capas_hoje if not c.get("data") or c["data"] >= recente]
    if len(capas_validas) != len(capas_hoje):
        escrever_json(f_capas, capas_validas)
        capas_hoje = capas_validas

    # 4. Ficheiros para o site
    todos_dias = sorted(p.stem for p in (DADOS / "temas").glob("*.json"))
    for dia in dias_tocados:
        temas = ler_json(DADOS / "temas" / f"{dia}.json", [])
        escrever_json(SITE / "dias" / f"{dia}.json", {
            "dia": dia,
            "capas": ler_json(DADOS / "capas" / f"{dia}.json", []),
            "temas": resumo_publico(temas, 15),
            "n_artigos": sum(t["n_artigos"] for t in temas),
        }, compacto=True)

    for nome, n in (("semana", 7), ("mes", 30)):
        janela = [d for d in todos_dias if d > (agora.date() - timedelta(days=n)).isoformat()]
        dias = {d: ler_json(DADOS / "temas" / f"{d}.json", []) for d in janela}
        historias = temas_do_periodo(dias)
        escrever_json(SITE / f"{nome}.json", {
            "de": janela[0] if janela else hoje, "ate": hoje, "n_dias": len(janela),
            "temas": resumo_publico(historias, 15),
        }, compacto=True)
        print(f"{nome}: {len(janela)} dias → {len(historias)} histórias")

    escrever_json(SITE / "indice.json", {
        "atualizado": agora.isoformat(timespec="minutes"),
        "hoje": hoje,
        "dias": sorted(p.stem for p in (SITE / "dias").glob("*.json")),
        "fontes": estado,
        "n_capas": len(capas_hoje),
    })
    print("Concluído.")


if __name__ == "__main__":
    sys.exit(main())
