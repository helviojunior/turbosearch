# Turbo Search (PT-BR)

Esta é uma ferramenta de busca (estilo brute-force) baseada em uma lista de palavras.

A Ferramenta foi desenvolvida em Python, tem seu código fonte aberto e suporta multi-threading, ou seja, diversas conexões simultâneas, agilizando o processo de busca.

## Informações gerais

Quando NÃO utilizado o parâmetro **-x** a ferramenta realizará a busca com base na lista de palavras, mas não colocando nenhuma extensão as requisições.

Porém quando utilizado o parâmetro **-x** a ferramenta irá realizar a busca padrão, ou seja, sem extensão e adicionalmente irá realizar a busca com as extensões informadas, trazendo desta forma um resultado mais completo.

Sendo assim recomendo fortemente que sempre utilize a busca com o parâmetro -x definido com as extensões mais comuns para a plataforma desejada


# Turbo Search (EN)

An python application to look for URL based on word list.

This application supports multi-threading requests.

## General informations

When you no use **-x** paramter this tool will search url based on wordlist, but without extensions.
Usinig **-x** paramter, the tool will do standard search (without extension) + extented search with extensions, so i strongly recommend to you **-x** paramters in all utilizations



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
→→-→→→→→→→→→→→→→→→→→→→→→→          Turbo Search v0.0.22 by Helvio Junior
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
  --report-to [target proxy]  target proxy URL to report only just successful requests (ex: http://127.0.0.1:8080)
  --deep                      Deep Search: Look for URLs inside of HTML results
  -v, --verbose               Shows more options (-h -v). Prints commands and outputs. (default: quiet)
  --full-log                  Print full requested URLs (default: no)
  --no-forward-location       Disable forward to Location response address (default: no)
  --ignore-result [filter]    ignore resuts by result code or/and size (ex1: 302 or ex2: 302:172 or ex3: 405,302:172 )
  --find [text to find]       Text to find in content or header (comma-separated values)
  --method [http method]      Specify request method (default: GET). Available methods: GET, POST,
                              PUT, OPTIONS
  --random-agent              Use randomly selected HTTP User-Agent header value (default: no)

Word List Options:
  --md5-search                Search for a MD5 Hash version of each word (default: no)
  --sha1-search               Search for a SHA1 Hash version of each word (default: no)
  --sha256-search             Search for a SHA256 Hash version of each word (default: no)
  --hash-upper                In case of Hash Search be enabled, also search by Uppercase of Hash Hex Text (default: no)


```
