import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time
from datetime import datetime
from urllib.parse import quote

load_dotenv(override=True)


from urllib.parse import urlparse, parse_qs



set_protocolos = set() #guardar um mapa de protocolos para processar somente os novos...

session = requests.session() #Essa sessão depois do login, carregar nos cookies a JSESSIONID, THE_TOKEN e THE_REFRESH_TOKEN, necessários para as consultas ao eProtocolo.


def login():
    print('Iniciando login...')
    print('Enviando GET...')
    USER = os.getenv("USER")
    PASS = os.getenv("PASS")
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Sec-GPC': '1',
    'Priority': 'u=0, i',
}

    # 1. O request inicial trás alguns parâmetros necessários ao login, como THE_STATE, CS_AUTH e THE_CODE. Esse request passa por alguns redirects e alguns desses itens estão presentes no redirect.
    resp = session.get("https://www.eprotocolo.pr.gov.br", headers=headers)

    COOKIES = session.cookies.get_dict()
    THE_STATE = COOKIES['THE_STATE']
    location = resp.history[-1].headers.get("Location")
    outer_params = parse_qs(urlparse(location).query)
    THE_CODE = outer_params['acesso'][0]

    referer = f'https://auth-cs.identidadedigital.pr.gov.br/centralautenticacao/login.html?response_type=code&client_id=9188905e74c28e489b44e954ec0b9bca&redirect_uri=https%3A%2F%2Fwww.eprotocolo.pr.gov.br%2Fspiweb&scope=null&state={THE_STATE}&urlCert=https://certauth-cs.identidadedigital.pr.gov.br&dnsCidadao=https://cidadao-cs.identidadedigital.pr.gov.br/centralcidadao&loginPadrao=btnCentral&labelCentral=CPF&modulosDeAutenticacao=btnGovbr,btnCertificado,btnSms,btnCpf,btnEmailToken,btnSanepar,btnCentral&urlLogo=https%3A%2F%2Fwww.eprotocolo.pr.gov.br%2Fspiweb%2Fimages%2Flogo_eprotocolo.png&acesso={THE_CODE}&tokenFormat=jwt&exibirLinkAutoCadastro=true&exibirLinkRecuperarSenha=true&exibirLinkAutoCadastroCertificado=false&captcha=false'

    print(urlparse(referer).query)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': referer,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://auth-cs.identidadedigital.pr.gov.br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Sec-GPC': '1',
        'Priority': 'u=0, i',
    }


    data = f'paginaLogin=&provedorselecionado=tabCentral&origemRequisicao=&valorCPF=&urlLogo=https%253A%252F%252Fwww.eprotocolo.pr.gov.br%252Fspiweb%252Fimages%252Flogo_eprotocolo.png&loginPadrao=btnCentral&modulosDeAutenticacao=btnGovbr%2CbtnCertificado%2CbtnSms%2CbtnCpf%2CbtnEmailToken%2CbtnSanepar%2CbtnCentral&labelCentral=CPF&moduloAtual=&dataAcesso={THE_CODE}&exibirLinkAutoCadastro=true&exibirLinkAutoCadastroCertificado=false&exibirLinkRecuperarSenha=true&formaAutenticacao=btnCpf&response_type=code&client_id=9188905e74c28e489b44e954ec0b9bca&redirect_uri=https%253A%252F%252Fwww.eprotocolo.pr.gov.br%252Fspiweb&scope=null&state={THE_STATE}&mensagem=&dnsCidadao=https%3A%2F%2Fcidadao-cs.identidadedigital.pr.gov.br%2Fcentralcidadao&provedores=&provedor=tabCentral&tokenFormat=jwt&code_challenge=&code_challenge_method=&captcha=false&codCaptcha=&attribute={USER}&attribute_central={USER}&password={PASS}&captchaCentral=&attribute_Sms=&celular=&captchaSms=&codigoSeguranca=&attribute_token=&codigoOTP=&attribute_expresso=&password_expresso=&captchaExpresso=&attribute_emailToken=&email=&captchaEmailToken=&codigoSegurancaEmail='

 
    req=requests.Request(method="POST", url='https://auth-cs.identidadedigital.pr.gov.br/centralautenticacao/api/v1/authorize/jwt',
        
        headers=headers,
        data=data)
    prepared = session.prepare_request(req)


    print('Enviando POST...')
    response = session.send(prepared)



    print('Done!')


    return response




def extrair_parametros_download(html: str):
    # Regex para capturar os 4 argumentos da função downloadVolumeParticionado
    padrao = r"downloadVolumeParticionado\('([^']*)',\s*'([^']*)',\s*'([^']*)',\s*'([^']*)'\)"
    match = re.search(padrao, html)

    if not match:
        return None

    protocolo = match.group(1)  # Ex: 240263866
    lista_docs = match.group(2) # Ex: [97939228, 97936513, ...]
    volume = match.group(3)     # Ex: 1
    flag = match.group(4)       # Ex: false

    # Converte a lista de documentos para lista Python
    #docs = [doc.strip() for doc in lista_docs.strip("[]").split(",")]
    docs = [int(doc.strip()) for doc in lista_docs.strip("[]").split(",") if doc.strip().isdigit()]

    return {
        "protocolo": protocolo,
        "documentos": docs,
        "volume": volume,
        "flag": flag
    }


def download_pdf(html, protocolo):
    LOCAL = os.getenv("LOCAL")
    dados = extrair_parametros_download(html)


    body = """
        acao=exibir&codLocal=REPR%2FIGF%2FAIF&numeroProtocolo=23.026.386-6&consultaPublica=false&consultaPorCpfCnpj=false&notificaRequerente=false&dataAtualizacaoUltimoTramiteView=11%2F07%2F2025&codigoOrgaoPara=REPR&codigoArquivoDocumentador=
    """
    body = quote(f'acao=exibir&codLocal={LOCAL}&numeroProtocolo={protocolo}&consultaPublica=false&consultaPorCpfCnpj=false&notificaRequerente=false&dataAtualizacaoUltimoTramiteView=11%2F07%2F2025&codigoOrgaoPara=REPR&codigoArquivoDocumentador=')
    params={
            "action":"downloadVolume",
            "numeroProtocolo":dados["protocolo"],
            "codigoOrgaoPara":"REPR",
            "arquivosDocumentadores":  "[" + ", ".join(map(str, dados["documentos"])) + "]" ,
            "particao":dados["volume"],
            "volumeFechado":dados["flag"]
    }
    
    headers={
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language":"en-US,en;q=0.5",
            "Accept-Encoding":"gzip, deflate, br, zstd",
            "Referer":"https://www.eprotocolo.pr.gov.br/",
            "Content-Type":"application/x-www-form-urlencoded",
            "Origin":"https://www.eprotocolo.pr.gov.br",
            "Connection":"keep-alive",
            "Upgrade-Insecure-Requests":"1",
            "Sec-Fetch-Dest":"document",
            "Sec-Fetch-Mode":"navigate",
            "Sec-Fetch-Site":"same-origin",
            "Sec-Fetch-User":"?1",
            "Priority":"u=0, i",
            "TE":"trailers"
    }


    with session.post(
        url='https://www.eprotocolo.pr.gov.br/spiweb/exibirProtocoloDigital.do',
        params=params,
        headers=headers,
        data=body
        
    ) as r:
   
        with open(f"{dados["protocolo"]}.pdf", "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)



def extrair_detalhes(html):

    soup = BeautifulSoup(html, "html.parser")
    container = soup.find("div", id="Protocolo_menos")
    if not container:
        return None

    dados = {}

    # Função auxiliar para pegar o texto do valor baseado na label
    def get_valor_por_label(label):
        td_label = container.find("td", string=lambda text: text and label in text)
        if td_label:
            td_value = td_label.find_next_sibling("td")
            if td_value:
                return td_value.get_text(strip=True)
        return None

    # Extrai os campos desejados
    dados["orgao"] = get_valor_por_label("Órgão:")
    dados["cadastrado_em"] = get_valor_por_label("Cadastrado em:")
    dados["detalhamento"] = get_valor_por_label("Detalhamento:")
    
    return dados


def exibe_protocolo(sid):


    body = """
        numeroProtocolo=&codSitProcessoFisico=&codLocal=REPR%2FIGF%2FAIF&tipoProcessoLocal=D&indProcesso=T&codTipoPendenciaFiltro=0&anoFiltro=
    """

    response = session.post(
        url='https://www.eprotocolo.pr.gov.br/spiweb/consultarProtocoloDigital.do',
        params={
            "action":"pesquisar",
            "origemChamada":"abaProtocolo",
            "numeroProtocolo": f"{sid}",
            "codLocal":"REPR/IGF/AIF"
        },
        headers={
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language":"en-US,en;q=0.5",
            "Accept-Encoding":"gzip, deflate, br, zstd",
            "Referer":"https://www.eprotocolo.pr.gov.br/",
            "Content-Type":"application/x-www-form-urlencoded",
            "Origin":"https://www.eprotocolo.pr.gov.br",
            "Connection":"keep-alive",
            "Upgrade-Insecure-Requests":"1",
            "Sec-Fetch-Dest":"document",
            "Sec-Fetch-Mode":"navigate",
            "Sec-Fetch-Site":"same-origin",
            "Sec-Fetch-User":"?1",
            "Priority":"u=0, i"
        },

        data=body
    
    )
    return response.text
    



def lista_processos():
    uri = 'https://www.eprotocolo.pr.gov.br/spiweb/telaInicial.do'
    LOCAL = os.getenv("LOCAL")
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0',
    'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://www.eprotocolo.pr.gov.br/',
    'X-Requested-With': 'XMLHttpRequest',
    'X-Prototype-Version': '1.7',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Priority': 'u=0',
    'TE': 'trailers',
    }
    
    params = (
    ('action', 'ajaxListarProtocolosNoLocal'),
    ('pesquisar', 'true'),
    ('indice', '1'),
    ('totalRegistros', '0'),
    ('colunaOrdenacao', '99'),
    ('direcaoOrdenacao', 'ASC'),
    ('codLocal', f'{LOCAL}'),
    ('codTipoPendenciaFiltro', '0'),
    ('tipoProcesso', 'D'),
    ('indProcesso', 'T'),
    ('anoFiltro', ''),
    ('dummy', '957495234544859000_1753461754011'),
    )

    response = session.get('https://www.eprotocolo.pr.gov.br/spiweb/telaInicial.do', headers=headers, params=params)

   
    soup = BeautifulSoup(response.text, "html.parser")

    # Selecionar a tabela pelo id
    tabela = soup.find("table", id="tabela_protocolos_local")
    if not tabela:
        return []

    protocolos = []

    # Iterar sobre as linhas da tabela (ignorando cabeçalho)
    for tr in tabela.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if not tds:
            continue

        primeira_coluna = tds[0].get_text(strip=True)

        # Verifica se segue o padrão XX.XXX.XXX-X
        if primeira_coluna and "." in primeira_coluna and "-" in primeira_coluna:
            protocolos.append(primeira_coluna)

    return protocolos


def loop_protocolos():
    protocolos = lista_processos()

    print(protocolos)
    for protocolo in protocolos:
        p = re.sub(r"\D", "", protocolo)

        if(p in set_protocolos):
            print(datetime.now(), f': O protocolo {p} já foi processado.')
        else:
            print(datetime.now(), f': Processando protocolo {p}')
            html = exibe_protocolo(p)
            dados = extrair_detalhes(html)
            download_pdf(html, protocolo)
            print(dados)
            set_protocolos.add(p)

login()
while True:
    loop_protocolos()
    time.sleep(60)  # wait 5 seconds

