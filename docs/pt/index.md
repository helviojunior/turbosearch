# TurboSearch #

[![ReadTheDocs](https://readthedocs.org/projects/turbosearch/badge/?version=latest)](https://turbosearch.readthedocs.io/en/latest/) [![Python 3](https://img.shields.io/badge/Python-3-green.svg)](https://github.com/helviojunior/turbosearch) 

`TurboSearch` é uma ferramenta de busca (estilo brute-force) baseada em uma lista de palavras. 

![turbosearch-help](help.jpg)

O `TurboSearch` inclui as seguintes funcionalidades:

  * **Uma** unica ferramenta com uma variedade de diferentes testes.
  * Uma lista completa com diversos [parâmetros](https://turbosearch.readthedocs.io/en/master/parameters/) para uma grande diversidade de diferentes cominações de teste.

## Setup ##

### Instalação rápida ###

Você pode instalar (ou atualizar para) a última versão do `TurboSearch` diretamente do repositório do GitHub.

```bash
pip3 install git+https://github.com/helviojunior/turbosearch.git#egg=turbosearch
```

### Instalação via git clone ###

Você pode instalar (ou atualizar para) a última versão do `TurboSearch` diretamente do repositório do GitHub.

```bash
git clone https://github.com/helviojunior/turbosearch/
cd turbosearch
pip3 install .
```

Ou você pode utilizar `TurboSearch` sem realizar a instalação do mesmo

```bash
git clone https://github.com/helviojunior/turbosearch/
cd turbosearch
pip3 install -r requirements.txt
./turbosearch
```

### Desinstalando ###

Para desinstalar:

```bash
pip3 uninstall turbosearch -y
ou
python3 -m pip uninstall turbosearch -y
```

### Executando ###

Basta executar o comando turbosearch de qualquer lugar do seu sistema operacional

```bash
$ turbosearch
```

### Atualização ###

Para realizar a atualização do `TurboSearch` basta executar o comando abaixo:

```bash
$ pip3 install --upgrade git+https://github.com/helviojunior/turbosearch.git#egg=turbosearch
```

## Dependências ##

Para o correto funcionamento o `TurboSearch` necessita das depenências abaixo:

- [`requests>=2.23.0`](https://github.com/psf/requests)
- [`bs4>=0.0.1`](https://github.com/waylan/beautifulsoup)
- [`colorama`](https://github.com/tartley/colorama)


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
Configuração de proxy (IP/Porta) para que o turbosearch realize uma requisição através deste somente quando tiver um resultado positivo da URL. Em caso de utilização de sofwares que montam arvore do site acessado, e realiza automatizações de teste através desta árvore (como o Burp Pro) essa opção enviará para o proxy somente as URLs que deram positivo na identificação, possibilitando manter o log do proxy limpo a acertivo nos testes, sem a necessidade de analizar o log do Turboseach e acessar as URLs novamente através do Burp.

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

### Happy hacking ###
