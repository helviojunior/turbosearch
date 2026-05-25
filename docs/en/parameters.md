# Parameters Documentation — TurboSearch

`TurboSearch` is a brute-force-style search tool driven by a wordlist, with multi-threading support, written in Python. Its purpose is to discover paths/URLs on HTTP servers using a list of words.

**General invocation:**

```bash
./turbosearch.py -t <target URL> -w <wordlist> [options]
```

---

## 1. General Settings

### `-t [target url]`

- **Action:** sets the target URL of the tests (e.g., `http://10.10.10.10/path`).
- **Consequence:** every request derived from the wordlist will be appended to this base. It is the mandatory starting point of the scan; without it the tool has nowhere to search.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w wordlist.txt
```

### `-w [word list]`

- **Action:** path to the wordlist file (one word per line, each tested as a path).
- **Consequence:** the size of the wordlist directly controls how many requests are generated. Very large wordlists can take a long time (combine with `-T` and `--no-dupcheck`).
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w /usr/share/dirb/wordlists/big.txt
```

### `-T [tasks]`

- **Action:** number of parallel connections per host (default: **16**).
- **Consequence:** higher values speed things up but can trigger WAF/IDS, rate-limits, or even bring down the target service. Tune it to the target's robustness.
- **Example (more aggressive scan):**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt -T 64
```

### `-o [output file]`

- **Action:** saves results to a file on disk (default: none).
- **Consequence:** allows downstream consumption of the results (reports, pipelines, automation). Without it, findings remain only on screen.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt -o /tmp/result.txt
```

### `-x [extensions]`

- **Action:** comma-separated list of extensions to be appended to each word.
- **Consequence:** for every word, both the bare version **and** the version **with each** extension are tested. Increases coverage but multiplies the number of requests by `N+1`.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt -x .html,.xml,.php,.txt
```

---

## 2. Custom Settings

### `-R, --restore`

- **Action:** restores a previously aborted session (from the `turbosearch.restore` file).
- **Consequence:** resumes the test from where it stopped, without redoing what was already processed.
- **Example:**

```bash
./turbosearch.py -R
```

### `-I, --ignore`

- **Action:** ignores an existing restore file without waiting the 10-second confirmation window.
- **Consequence:** overwrites the pending session immediately — useful in scripts/CI, risky if you might still want to recover the previous test.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt -I
```

### `-D, --double-path`

- **Action:** combines pairs of words from the wordlist to generate two-level paths (e.g., `word1/word2`).
- **Consequence:** combinatorial explosion — the number of requests becomes roughly `N²`. Use with small, focused wordlists.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w small.txt -D
```

### `--proxy [target proxy]`

- **Action:** routes **100% of the requests** through the given proxy.
- **Consequence:** lets you inspect/modify the entire traffic via Burp/ZAP. Can be slow because all flow funnels through a single point.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --proxy http://127.0.0.1:8080
```

### `--report-to [target proxy]`

- **Action:** sends to the proxy **only the successful requests**.
- **Consequence:** keeps the site tree in Burp clean, containing only valid URLs — ideal for feeding automated workflows without polluting the history with 404s.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --report-to http://127.0.0.1:8080
```

### `--deep`

- **Action:** Deep Search — parses the HTML of discovered pages and extracts the links it contains.
- **Consequence:** internal links (same domain) enter the test queue; external links are merely reported. Increases coverage, but also total time and memory usage.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --deep
```

### `-v, --verbose`

- **Action:** increases the verbosity level (can be repeated: `-v -v`).
- **Consequence:** displays more detail about what is happening; useful for troubleshooting. Combined with `-h` (`-h -v`), exposes additional options hidden from the default help.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt -v
```

### `--full-log`

- **Action:** prints the full URL of every request executed (default: no).
- **Consequence:** much larger logs; recommended only for debugging or auditing.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --full-log
```

### `--no-forward-location`

- **Action:** disables automatic forwarding of redirects (Location header).
- **Consequence:** TurboSearch reports the original `3xx` without following the redirect — useful for explicitly mapping redirect chains.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --no-forward-location
```

### `--ignore-result [filter]`

- **Action:** ignores results that match the filter (by status code and/or size).
- **Consequence:** reduces false positives. Syntax:
    - `302` — ignore every 302
    - `302:172` — ignore 302 with size 172
    - `405,302:172` — combine multiple rules
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --ignore-result 302:172,404
```

### `--stop-on [filter]`

- **Action:** stops the scan upon receiving a result matching the filter (same syntax as `--ignore-result`).
- **Consequence:** useful for detecting bans/WAFs (e.g., `--stop-on 403:0`) or stopping when a specific marker appears.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --stop-on 429
```

### `--find [text to find]`

- **Action:** text to search for inside the body or headers of each response (comma-separated).
- **Consequence:** identifies pages that contain specific strings (e.g., error messages, tokens) beyond the default status-code/size criteria.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --find "admin,login,token"
```

### `--method [http method]`

- **Action:** defines the HTTP method(s) used in requests (default: `GET`).
- **Accepted values:** `GET`, `POST`, `PUT`, `PATCH`, `HEAD`, `OPTIONS`, `all`, or several comma-separated.
- **Consequence:** `all` (or multiple methods) multiplies the number of requests by method; useful against APIs.
- **Example:**

```bash
./turbosearch.py -t http://api/ -w big.txt --method GET,POST,PUT
```

### `--random-agent`

- **Action:** sends a random HTTP `User-Agent` with each request.
- **Consequence:** hampers detection/blocking by simple filters based on a fixed UA.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --random-agent
```

### `--header [headers]`

- **Action:** adds custom HTTP headers in **JSON** format.
- **Consequence:** required for targets that demand session cookies, tokens, or specific headers (`Authorization`, `Host`, etc.).
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt \
  --header '{"PHPSESSID":"gvksi1cmjl2kqgntqof19sh823","Authorization":"Bearer xxx"}'
```

### `--ci, --case-insensitive`

- **Action:** lowercases the entire wordlist and removes duplicates.
- **Consequence:** avoids testing the same word in different capitalizations on case-insensitive servers (e.g., IIS).
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --ci
```

### `--stats-db`

- **Action:** stores successful URIs in a local SQLite database called `stats.db`.
- **Consequence:** enables integration with external tools (for example, **WebHunterScreen**, which generates screenshots from that file).
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --stats-db
```

### `--no-robots`

- **Action:** does NOT query `robots.txt` before scanning.
- **Consequence:** avoids signaling paths via robots on public targets, but may miss valuable hints typically listed there.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --no-robots
```

### `--ip`

- **Action:** retrieves and prints the current external IP (of the runner).
- **Consequence:** useful for auditing/logging the test's origin, especially in authorized pentests.
- **Example:**

```bash
./turbosearch.py --ip
```

---

## 3. Word List Options

### `--md5-search`

- **Action:** for each word, also tests its **MD5 hash** version.
- **Consequence:** useful when the target exposes directories/files named as MD5 hashes.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --md5-search
```

### `--sha1-search`

- **Action:** same logic with **SHA1**.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --sha1-search
```

### `--sha256-search`

- **Action:** same logic with **SHA256**.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --sha256-search
```

### `--hash-upper`

- **Action:** when any hash search is enabled, also tests the **uppercase** version of the hex digest.
- **Consequence:** doubles the request volume for hashes, but covers targets that distinguish case.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w big.txt --md5-search --hash-upper
```

### `--no-dupcheck`

- **Action:** disables the duplicate-word check on the wordlist.
- **Consequence:** speeds up loading of very large wordlists (saves RAM/CPU during preprocessing), but may generate redundant requests if real duplicates exist.
- **Example:**

```bash
./turbosearch.py -t http://10.10.10.10/ -w huge_wordlist.txt --no-dupcheck
```

---

## 4. Combined usage scenarios

**a) Basic scan with extensions and output file**

```bash
./turbosearch.py -t http://target.com/ -w big.txt -x .html,.php,.txt -o result.txt
```

**b) Scan via Burp Suite, reporting only hits**

```bash
./turbosearch.py -t http://target.com/ -w big.txt \
  --report-to http://127.0.0.1:8080 --stats-db
```

**c) Authenticated pentest with cookie + random User-Agent**

```bash
./turbosearch.py -t http://target.com/ -w big.txt \
  --header '{"Cookie":"PHPSESSID=abc123"}' --random-agent
```

**d) Deep scan, ignoring typical false positives**

```bash
./turbosearch.py -t http://target.com/ -w big.txt --deep \
  --ignore-result 404,302:0 -x .php,.bak,.old
```

**e) Restoring an interrupted session**

```bash
./turbosearch.py -R
```

**f) Combined fuzzing (GET/POST/PUT) with body-text search**

```bash
./turbosearch.py -t http://api/ -w api.txt \
  --method GET,POST,PUT --find "error,exception,token"
```

**g) Brute-forcing a case-insensitive target with a huge wordlist**

```bash
./turbosearch.py -t http://target.com/ -w huge.txt --ci --no-dupcheck -T 32
```

---

## 5. Important notes

- The `-x` parameter performs a **dual sweep**: first the raw word, then the word + extension. Whenever possible, set extensions matching the target stack (`.aspx`, `.jsp`, `.php`, etc.).
- `--proxy` sends **everything** to the proxy; `--report-to` sends **only the hits**. They are complementary and useful together.
- `Ctrl+C` during the scan offers the option to **skip the current directory** without ending the session (`S` = skip / `q` = quit). State is preserved for later use with `-R`.
- Combine a high `-T` with care: it can cause unintentional denial of service and WAF blocks.
