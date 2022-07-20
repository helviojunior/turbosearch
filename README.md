[![ReadTheDocs](https://readthedocs.org/projects/turbosearch/badge/?version=latest)](https://turbosearch.readthedocs.io/en/latest/) [![Python 3](https://img.shields.io/badge/Python-3-green.svg)](https://github.com/helviojunior/turbosearch) [![GitHub contributors](https://img.shields.io/github/contributors/helviojunior/turbosearch)](https://github.com/helviojunior/turbosearch/graphs/contributors/)

# Turbo Search (PT-BR)

Esta é uma ferramenta de busca (estilo brute-force) baseada em uma lista de palavras.

A Ferramenta foi desenvolvida em Python, tem seu código fonte aberto e suporta multi-threading, ou seja, diversas conexões simultâneas, agilizando o processo de busca.

## Instalação

Você pode instalar (ou atualizar para) a última versão do TurboSearch diretamente do repositório do GitHub

```
pip3 install --upgrade git+https://github.com/helviojunior/turbosearch.git#egg=turbosearch
```

## Documentação

O TurboSearch detém uma extensiva e atualizada [documentação](https://turbosearch.readthedocs.io/en/latest/pt/). Recomendamos a leitura para entendimento das opções e variedades de utilização do TurboSearch.


# Turbo Search (EN)

An python application to look for URL based on word list.

This application supports multi-threading requests.

## Installation

You can install the latest version of TurboSearch by using the GitHub repository:

```
pip3 install git+https://github.com/helviojunior/turbosearch.git#egg=turbosearch
```

## Documentation


O TurboSearch  has an extensive and up-to-date [documentation](https://turbosearch.readthedocs.io/en/latest/en/). Users are recommended to refer to it as it may help them in their attempts to use TurboSearch. In particular, new users should navigate through it (see the FAQ for common installation problems).


# Utilization samples/exemplos de utilização
```
./turbosearch.py -t http://10.10.10.10/ -w /usr/share/dirb/wordlists/big.txt
./turbosearch.py -t http://10.10.10.10/ -w /usr/share/dirb/wordlists/big.txt -x .html,.xml,.php,.txt
./turbosearch.py -t http://10.10.10.10/ -w /usr/share/dirb/wordlists/big.txt -x .html,.xml,.php,.txt -o /path/to/output/file.txt

```


```

HHHHHH           →→HHH
HHHHHH           →→→→HH
HHHHHH           →→→→→→
→→-→→→→→→→→→→→→→→→→→→→→→→          Turbo Search v0.1.22 by Helvio Junior
→→|→→→→→→→→→→→→→→→→→→→→→→→→        automated url finder
→→-→→→→→→→→→→→→→→→→→→→→→→          https://github.com/helviojunior/turbosearch
HHHHHH           →→→→→→
HHHHHH           →→→→HH
HHHHHH           →→HHH


optional arguments:
  -h, --help                  show this help message and exit

General Setting:
  -t [target url]             target url (ex: http://10.10.10.10/path)
  -w [word list]              word list to be tested
  -T [tasks]                  number of connects in parallel (per host, default: 16)
  -o [output file]            save output to disk (default: none)
  -x [extensions]             Append each request with this extensions (comma-separated values)

Custom Settings:
  -R, --restore               restore a previous aborted/crashed session
  -I, --ignore                ignore an existing restore file (don't wait 10 seconds)
  --proxy [target proxy]      target proxy URL (ex: http://127.0.0.1:8080)
  --report-to [target proxy]  target proxy URL to report only successful requests (ex: http://127.0.0.1:8080)
  --deep                      Deep Search: Look for URLs inside of HTML results
  -v, --verbose               Shows more options (-h -v). Prints commands and outputs. (default: quiet)
  --full-log                  Print full requested URLs (default: no)
  --no-forward-location       Disable forward to Location response address (default: no)
  --ignore-result [filter]    ignore resuts by result code or/and size (ex1: 302 or ex2: 302:172 or ex3: 405,302:172 )
  --find [text to find]       Text to find in content or header (comma-separated values)
  --method [http method]      Specify request method (default: GET). Available methods: GET, POST,
                              PUT, OPTIONS, all
  --random-agent              Use randomly selected HTTP User-Agent header value (default: no)
  --header [text to find]     JSON-formatted header key/value
  --ci, --case-insensitive    Case Insensitive search: put all wordlist in lower case
  --stats-db                  Save reported URI at SQLite local database called stats.db (default: no)
  --no-robots                 Not look for robots.txt (default: no)

Word List Options:
  --md5-search                Search for a MD5 Hash version of each word (default: no)
  --sha1-search               Search for a SHA1 Hash version of each word (default: no)
  --sha256-search             Search for a SHA256 Hash version of each word (default: no)
  --hash-upper                In case of Hash Search be enabled, also search by Uppercase of Hash Hex Text (default: no)
  --no-dupcheck               Do not check duplicate words in wordlist. Use in case of big wordlists (default: False)


```

# Ferramentas relacionadas

O Luiz Carmo criou uma ferramenta (Web Hunter Screen) que realiza o acesso automatizado as URLs e cria um ScreenShoot de cada página. A ferramenta está preparada para ler o arquivo de dados gerado pelo ```TurboSearch``` com a opção **--stats-db** e realizar os ScreenShoots de todas as URLs apontadas pelo TurboSearch.

URL: https://github.com/lgcarmo/WebHunterScreen