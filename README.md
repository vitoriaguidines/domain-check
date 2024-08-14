
# Subdomain Checker

Este script realiza a verificação de acessibilidade de subdomínios a partir de uma ou duas wordlists, com funcionalidades adicionais como filtragem de subdomínios, eliminação de linhas em branco, remoção de duplicatas e geração de wordlists combinadas.

## Funcionalidades

- **Verificação de Subdomínios**: Verifica a acessibilidade de subdomínios fornecidos em uma ou duas wordlists.
- **Filtragem por Domínio**: Filtra os subdomínios na wordlist que terminam com um domínio específico.
- **Eliminação de Linhas em Branco**: Remove linhas em branco da wordlist antes de realizar a verificação.
- **Remoção de Duplicatas**: Remove subdomínios duplicados da wordlist.
- **Geração de Wordlist Combinada**: Combina duas wordlists, remove duplicatas e gera uma nova wordlist.
- **Saída Verbosa**: Exibe informações detalhadas sobre a verificação de cada subdomínio.

## Instalação

Antes de executar o script, instale as bibliotecas necessárias com:

```bash
pip install requests tqdm colorama
```

## Uso

### Parâmetros

- `-w`, `--wordlist` (obrigatório): Especifica uma ou duas wordlists com os subdomínios a serem verificados.
- `-v`, `--verbose`: Ativa a saída verbosa, mostrando detalhes de cada verificação.
- `-f`, `--filter`: Filtra a wordlist pelos subdomínios que terminam com o domínio especificado antes de realizar a verificação.
- `-e`, `--eliminate`: Elimina as linhas em branco do arquivo de wordlist antes de realizar a verificação.
- `-c`, `--correct`: Remove subdomínios duplicados e salva a wordlist corrigida em um novo arquivo.
- `-g`, `--generate`: Gera uma wordlist combinada de duas listas sem duplicatas e salva em um novo arquivo.

### Exemplos de Uso

1. **Verificação de Subdomínios com uma Única Wordlist**:

   ```bash
   python checa-dominios.py -w subdomains.txt -v
   ```

2. **Verificação de Subdomínios com Duas Wordlists Combinadas**:

   ```bash
   python checa-dominios.py -w subdomains1.txt subdomains2.txt -v
   ```

3. **Eliminação de Linhas em Branco e Verificação**:

   ```bash
   python checa-dominios.py -w subdomains.txt -e -v
   ```

4. **Filtragem por Domínio e Verificação**:

   ```bash
   python checa-dominios.py -w subdomains.txt -f exemplo.com -v
   ```

5. **Geração de Wordlist Corrigida sem Duplicatas**:

   ```bash
   python checa-dominios.py -w subdomains.txt -c
   ```

6. **Geração de Wordlist Combinada de Duas Listas sem Duplicatas**:

   ```bash
   python checa-dominios.py -w subdomains1.txt subdomains2.txt -g
   ```

## Detalhes do Script

### Verificação de Subdomínios

O script verifica se os subdomínios fornecidos são acessíveis (retornando código HTTP 200) ou se respondem com algum erro. A verificação pode ser feita com uma wordlist ou com duas wordlists combinadas.

### Filtragem por Domínio

Ao usar o parâmetro `-f`, você pode filtrar os subdomínios na wordlist para incluir apenas aqueles que terminam com um domínio específico, como `exemplo.com`.

### Eliminação de Linhas em Branco

Se o parâmetro `-e` for utilizado, o script eliminará todas as linhas em branco na wordlist antes de prosseguir com a verificação.

### Remoção de Duplicatas

O parâmetro `-c` permite que você remova subdomínios duplicados da wordlist e salve a lista corrigida em um novo arquivo.

### Geração de Wordlist Combinada

Quando duas wordlists são fornecidas, o parâmetro `-g` pode ser usado para gerar uma wordlist combinada, sem duplicatas, sem realizar a verificação.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma issue ou enviar um pull request com melhorias.

## Licença

Este projeto está licenciado sob a Licença MIT.
