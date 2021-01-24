# Turbo Search (PT-BR)

Esta é uma ferramenta de busca (estilo brute-force) baseada em uma lista de palavras.

A Ferramenta foi desenvolvida em Python, tem seu código fonte aberto e suporta multi-threading, ou seja, diversas conexões simultâneas, agilizando o processo de busca.

## Instalação

Você pode instalar a última versão do TurboSearch diretamente do repositório do GitHub

```
pip3 install git+https://github.com/helviojunior/turbosearch.git#egg=turbosearch
```

Ou clonando o repositório localmente:


```
git clone https://github.com/helviojunior/turbosearch/
```

Se você deseja utilizar o TurboSearch de qualquer local do seu sistema operacional para utilizar o pip3 para realizar a instalação:


```
cd turbosearch
pip3 install .
ou
python3 -m pip install .
```


Para desinstalar:


```
pip3 uninstall turbosearch -y
ou
python3 -m pip uninstall turbosearch -y
```


## Informações gerais

Quando NÃO utilizado o parâmetro **-x** a ferramenta realizará a busca com base na lista de palavras, mas não colocando nenhuma extensão as requisições.

Porém quando utilizado o parâmetro **-x** a ferramenta irá realizar a busca padrão, ou seja, sem extensão e adicionalmente irá realizar a busca com as extensões informadas, trazendo desta forma um resultado mais completo.

Sendo assim recomendo fortemente que sempre utilize a busca com o parâmetro -x definido com as extensões mais comuns para a plataforma desejada

## Principais opções
**--deep**
Realiza a busca em profundidade na página testada, em outras palavras, lista o HTML da página buscando links presentes no HTML reportando links externos e ja colocando na fila de testes Links internos (do mesmo domínio)

**--random-agent**
Seleciona um User-Agent randômico

**--ignore-result**
Possibilidade de ignorar falso-positivo conforme o padrão definido

**--header**
Adição de cabeçlhos HTTP personalizados no formato JSON

**--proxy**
Configuração de proxy (IP/Porta) para envio de 100% das requisições

**--report-to**
Configuração de proxy (IP/Porta) para que o turbosearch realize uma requisição através deste somente quando tiver um resultado positivo da URL. Em caso de utilização de sofwares que montam arvore do site acessado, e realiza automatizações de teste através desta árvore (como o Burp Pro) essa opçãao enviará para o proxy somente as URLs que deram positivo na identificação, possibilitando manter o log do proxy limpo a acertivo nos testes, sem a necessidade de analizar o log do Turboseach e acessar as URLs novamente através do Burp.

**--case-insensitive**
Quando habilitado o turbosearch converte toda a wordlist para minúsculo e ignora palavras duplicadas.


## Pular diretório
Quanto o TurboSearch estiver realizando a busca em um subdiretório e você desejar pular este scan, basta preccionat CTRL + C que será exibido uma mensagem questionando se você deseja pular o diretório ou sair do teste (ambas opções manterão o status do teste atual caso deseje restaurar o teste).

**Exemplo:**

No exemplo abaixo foram encontrados 1 diretórios que é falso positivo (.htpassword), desta forma desejamos ignorá-lo. Quando o TurboSearch iniciar o scan deste diretório é pressionado CTRL + C sendo exibida a mensagem solicitando o que você deseja fazer, basta pressionar “S” e enter que o TurboSearch continuará o teste no próximo diretório.

```
 [+] Connection test againt http://api1.webapiexploitation.com.br/api OK! (CODE:404|SIZE:143)

 [+] Scanning url http://api1.webapiexploitation.com.br/api
 [*] Calculated default not found http code for this folder is 404 with content size 154
==> DIRECTORY: http://api1.webapiexploitation.com.br/api/.htaccess/ (CODE:403|SIZE:153)
==> DIRECTORY: http://api1.webapiexploitation.com.br/api/v1/ (CODE:200|SIZE:404)

 [+] Entering directory: http://api1.webapiexploitation.com.br/api/.htaccess
 [*] Calculated default not found http code for this folder is 403 with content size 153
^C
how do you want to proceed? [(S)kip current directory/(q)uit]
s

 [!] skipping current directory


 [+] Entering directory: http://api1.webapiexploitation.com.br/api/v1
 [*] Calculated default not found http code for this folder is 404 with content size 157
==> DIRECTORY: http://api1.webapiexploitation.com.br/api/v1/.htaccess/ (CODE:403|SIZE:153)
==> DIRECTORY: http://api1.webapiexploitation.com.br/api/v1/users/ (CODE:200|SIZE:27)

 [+] End time 2021-01-23 03:36:37
 [+] Finished tests against http://api1.webapiexploitation.com.br/api, exiting
```

# Turbo Search (EN)

An python application to look for URL based on word list.

This application supports multi-threading requests.

## Installation

You can install the latest version of TurboSearch by using the GitHub repository:


```
pip3 install git+https://github.com/helviojunior/turbosearch.git#egg=turbosearch
```



Or uou can download the latest version of TurboSearch by cloning the GitHub repository:

```
git clone https://github.com/helviojunior/turbosearch/
```

If you would like to run TurboSearch from anywhere in your system you can install it with pip3:


```
cd turbosearch
pip3 install .
ou
python3 -m pip install .
```


To uninstall it:


```
pip3 uninstall turbosearch -y
ou
python3 -m pip uninstall turbosearch -y
```


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
→→-→→→→→→→→→→→→→→→→→→→→→→          Turbo Search v0.1.4 by Helvio Junior
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
                              PUT, OPTIONS
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


```
