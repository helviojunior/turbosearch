# Documentação dos Parâmetros — TurboSearch

`TurboSearch` é uma ferramenta de busca estilo brute-force baseada em wordlist, com suporte a multi-threading, escrita em Python. Sua função é descobrir caminhos/URLs em servidores HTTP a partir de uma lista de palavras.

**Forma geral de execução:**

```bash
./turbosearch.py -t <URL alvo> -w <wordlist> [opções]
```

---

## 1. General Setting (Configurações Gerais)

### `-t [target url]`

- **Ação:** define a URL alvo dos testes (ex.: `http://10.10.10.10/path`).
- **Consequência:** toda requisição da wordlist será concatenada a esta base. É o ponto de partida obrigatório do scan; sem ele a ferramenta não tem onde buscar.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w wordlist.txt
```

### `-w [word list]`

- **Ação:** caminho para o arquivo de wordlist (cada linha = uma palavra testada como path).
- **Consequência:** o tamanho da wordlist controla diretamente quantas requisições serão geradas. Wordlists muito grandes podem demorar (combine com `-T` e `--no-dupcheck`).
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w /usr/share/dirb/wordlists/big.txt
```

### `-T [tasks]`

- **Ação:** número de conexões em paralelo por host (default: **16**).
- **Consequência:** valores mais altos aumentam a velocidade, mas podem disparar WAF/IDS, rate-limit ou derrubar o serviço alvo. Ajuste conforme a robustez do alvo.
- **Exemplo (scan mais agressivo):**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt -T 64
```

### `-o [output file]`

- **Ação:** salva os resultados em arquivo em disco (default: nenhum).
- **Consequência:** permite consumir os resultados depois (relatórios, pipelines, automação). Sem este parâmetro, os achados ficam apenas em tela.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt -o /tmp/result.txt
```

### `-x [extensions]`

- **Ação:** lista de extensões (separadas por vírgula) a serem concatenadas a cada palavra.
- **Consequência:** para cada palavra é testada a versão **sem** extensão e também **com cada uma** das extensões. Aumenta cobertura mas multiplica o número de requisições por `N+1`.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt -x .html,.xml,.php,.txt
```

---

## 2. Custom Settings (Configurações Personalizadas)

### `-R, --restore`

- **Ação:** restaura uma sessão anteriormente abortada (a partir do arquivo `turbosearch.restore`).
- **Consequência:** retoma o teste do ponto em que parou, sem refazer o que já foi processado.
- **Exemplo:**

```bash
./turbosearch.py -R
```

### `-I, --ignore`

- **Ação:** ignora o arquivo de restore existente sem aguardar os 10 segundos de confirmação.
- **Consequência:** sobrescreve a sessão pendente imediatamente — útil em scripts/CI, perigoso se você ainda quisesse recuperar o teste anterior.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt -I
```

### `-D, --double-path`

- **Ação:** combina pares de palavras da wordlist para gerar caminhos de dois níveis (ex.: `word1/word2`).
- **Consequência:** explosão combinatória — o número de requisições passa a ser ≈ `N²`. Use com wordlists pequenas e foco específico.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w small.txt -D
```

### `--proxy [target proxy]`

- **Ação:** envia **100% das requisições** através do proxy informado.
- **Consequência:** permite inspecionar/modificar todo o tráfego via Burp/ZAP. Pode ser lento por concentrar todo o fluxo em um único ponto.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --proxy http://127.0.0.1:8080
```

### `--report-to [target proxy]`

- **Ação:** envia ao proxy **apenas as requisições com resultado positivo**.
- **Consequência:** mantém a árvore do site no Burp limpa, contendo só URLs válidas — ideal para alimentar fluxos automatizados sem poluir o histórico com 404s.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --report-to http://127.0.0.1:8080
```

### `--deep`

- **Ação:** Deep Search — analisa o HTML de páginas encontradas e extrai links presentes.
- **Consequência:** links internos (mesmo domínio) entram na fila de teste; links externos são apenas reportados. Aumenta a cobertura, porém também o tempo total e o consumo de memória.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --deep
```

### `-v, --verbose`

- **Ação:** aumenta o nível de verbosidade (pode repetir: `-v -v`).
- **Consequência:** exibe mais detalhes do que está acontecendo; útil para troubleshooting. Combinado com `-h` (`-h -v`), expõe opções adicionais ocultas na ajuda padrão.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt -v
```

### `--full-log`

- **Ação:** imprime a URL completa de cada requisição executada (default: não).
- **Consequência:** logs muito mais volumosos; recomendado apenas para depuração ou auditoria.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --full-log
```

### `--no-forward-location`

- **Ação:** desabilita o encaminhamento automático de redirecionamentos (Location).
- **Consequência:** o TurboSearch reporta o `3xx` original sem seguir o redirect — útil para mapear redirecionamentos explicitamente.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --no-forward-location
```

### `--ignore-result [filter]`

- **Ação:** ignora resultados que casem com o filtro (por código e/ou tamanho).
- **Consequência:** reduz falsos positivos. Sintaxe:
    - `302` — ignora todos os 302
    - `302:172` — ignora 302 com size 172
    - `405,302:172` — combina múltiplas regras
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --ignore-result 302:172,404
```

### `--stop-on [filter]`

- **Ação:** para o scan ao receber um resultado que case com o filtro (mesma sintaxe do `--ignore-result`).
- **Consequência:** útil para detectar banimentos/WAF (ex.: `--stop-on 403:0`) ou para parar quando um marcador específico aparece.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --stop-on 429
```

### `--find [text to find]`

- **Ação:** texto a procurar dentro do corpo ou dos headers de cada resposta (separado por vírgula).
- **Consequência:** identifica páginas que contêm strings específicas (ex.: mensagens de erro, tokens), além do critério padrão de status code/size.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --find "admin,login,token"
```

### `--method [http method]`

- **Ação:** define o(s) método(s) HTTP usados nas requisições (default: `GET`).
- **Valores aceitos:** `GET`, `POST`, `PUT`, `PATCH`, `HEAD`, `OPTIONS`, `all` ou vários separados por vírgula.
- **Consequência:** `all` (ou múltiplos) multiplica o número de requisições por método; útil em APIs.
- **Exemplo:**

```bash
./turbosearch.py -t http://api/ -w big.txt --method GET,POST,PUT
```

### `--random-agent`

- **Ação:** envia um `User-Agent` HTTP aleatório a cada requisição.
- **Consequência:** dificulta a detecção/bloqueio por filtros simples baseados em UA fixo.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --random-agent
```

### `--header [headers]`

- **Ação:** adiciona cabeçalhos HTTP personalizados em formato **JSON**.
- **Consequência:** necessário para alvos que exigem cookies de sessão, tokens, ou cabeçalhos específicos (`Authorization`, `Host`, etc.).
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt \
  --header '{"PHPSESSID":"gvksi1cmjl2kqgntqof19sh823","Authorization":"Bearer xxx"}'
```

### `--ci, --case-insensitive`

- **Ação:** converte toda a wordlist para minúsculas e remove duplicatas.
- **Consequência:** evita testar a mesma palavra em diferentes capitalizações em servidores case-insensitive (IIS, por exemplo).
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --ci
```

### `--stats-db`

- **Ação:** grava as URIs com sucesso em banco SQLite local `stats.db`.
- **Consequência:** habilita integração com ferramentas externas (por exemplo, **WebHunterScreen**, que gera screenshots a partir desse arquivo).
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --stats-db
```

### `--no-robots`

- **Ação:** NÃO consulta `robots.txt` antes do scan.
- **Consequência:** evita revelar paths via robots em alvos públicos, mas pode perder dicas valiosas geralmente listadas ali.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --no-robots
```

### `--ip`

- **Ação:** obtém e exibe o IP externo atual (do executor).
- **Consequência:** útil para auditoria/registro de origem do teste, sobretudo em pentests autorizados.
- **Exemplo:**

```bash
./turbosearch.py --ip
```

---

## 3. Word List Options (Opções da Wordlist)

### `--md5-search`

- **Ação:** para cada palavra, também testa a versão em **MD5 hash**.
- **Consequência:** útil quando o alvo expõe diretórios/arquivos nomeados como hash MD5.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --md5-search
```

### `--sha1-search`

- **Ação:** mesma lógica com **SHA1**.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --sha1-search
```

### `--sha256-search`

- **Ação:** mesma lógica com **SHA256**.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --sha256-search
```

### `--hash-upper`

- **Ação:** quando alguma busca por hash está habilitada, também testa a versão em **maiúsculas** do hex.
- **Consequência:** dobra o volume de requisições para os hashes, mas cobre alvos que distinguem case.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --md5-search --hash-upper
```

### `--no-dupcheck`

- **Ação:** desativa a verificação de palavras duplicadas na wordlist.
- **Consequência:** acelera o carregamento de wordlists muito grandes (economia de RAM/CPU no preprocess), mas pode gerar requisições redundantes se houver duplicatas reais.
- **Exemplo:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w huge_wordlist.txt --no-dupcheck
```

---

## 4. Cenários combinados de uso

**a) Scan básico com extensões e arquivo de saída**

```bash
./turbosearch.py -t http://alvo.com/ -w big.txt -x .html,.php,.txt -o result.txt
```

**b) Scan via Burp Suite, reportando apenas hits**

```bash
./turbosearch.py -t http://alvo.com/ -w big.txt \
  --report-to http://127.0.0.1:8080 --stats-db
```

**c) Pentest autenticado com cookie + User-Agent aleatório**

```bash
./turbosearch.py -t http://alvo.com/ -w big.txt \
  --header '{"Cookie":"PHPSESSID=abc123"}' --random-agent
```

**d) Scan profundo, ignorando falsos positivos típicos**

```bash
./turbosearch.py -t http://alvo.com/ -w big.txt --deep \
  --ignore-result 404,302:0 -x .php,.bak,.old
```

**e) Restauração de sessão interrompida**

```bash
./turbosearch.py -R
```

**f) Fuzzing combinado (GET/POST/PUT) com busca por termo no body**

```bash
./turbosearch.py -t http://api/ -w api.txt \
  --method GET,POST,PUT --find "error,exception,token"
```

**g) Brute em alvo case-insensitive com wordlist gigante**

```bash
./turbosearch.py -t http://alvo.com/ -w huge.txt --ci --no-dupcheck -T 32
```

---

## 5. Observações importantes

- O parâmetro `-x` faz **dupla varredura**: primeiro a palavra crua, depois a palavra + extensão. Sempre que possível, defina extensões compatíveis com a stack alvo (`.aspx`, `.jsp`, `.php`, etc.).
- `--proxy` envia **tudo** ao proxy; `--report-to` envia **somente os achados**. São complementares e mutuamente úteis.
- `Ctrl+C` durante o scan oferece a opção de **pular o diretório atual** sem encerrar a sessão (`S` = skip / `q` = quit). O estado é preservado para uso posterior com `-R`.
- Combine `-T` alto com cautela: pode gerar negação de serviço involuntária e bloqueios por WAF.
