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
→→-→→→→→→→→→→→→→→→→→→→→→→          Turbo Search v0.0.1 by Helvio Junior
→→|→→→→→→→→→→→→→→→→→→→→→→→→        automated url finder
→→-→→→→→→→→→→→→→→→→→→→→→→          https://gitlab.com/helvio_junior/overflow
HHHHHH           →→→→→→
HHHHHH           →→→→HH
HHHHHH           →→HHH

    
optional arguments:
  -h, --help          show this help message and exit

SETTINGS:
  -v, --verbose       Shows more options (-h -v). Prints commands and outputs. (default: quiet)
  -t [target url]     target url (ex: http://10.10.10.10/path)
  -w [word list]      word list to be tested
  -T [tasks]          number of connects in parallel (per host, default: 16)
  -o [output file]    save output to disk (default: none)

CUSTOM:
  --forward-location  Forward to Location response address (default: yes)
  -x [extensions]     Append each request with this extensions (comma-separated values)
```
