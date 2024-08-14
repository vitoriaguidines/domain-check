import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
from tqdm import tqdm
from colorama import Fore, Style, init
import os

init(autoreset=True)

def check_subdomain(subdomain, verbose=False):
    try:
        response = requests.get(f"http://{subdomain}", timeout=5)
        if response.status_code == 200:
            if verbose:
                print(f"\n{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {subdomain} está {Fore.GREEN}acessível{Style.RESET_ALL} (HTTP 200).\n")
            return subdomain, "Acessível"
        else:
            if verbose:
                print(f"\n{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {subdomain} retornou {Fore.YELLOW}erro HTTP {response.status_code}{Style.RESET_ALL}.\n")
            return subdomain, f"Erro HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        error_message = str(e).split(': ')[-1]
        if verbose:
            print(f"\n{Fore.RED}[ERROR]{Style.RESET_ALL} {subdomain} não acessível.\nErro: {error_message}\n")
        return subdomain, "Não acessível"

def filtrar_subdominios_por_dominio(input_file, dominio_escolhido):
    subdominios_filtrados = []
    with open(input_file, 'r') as file:
        for linha in file:
            subdominio = linha.strip()
            if subdominio.endswith(dominio_escolhido):
                subdominios_filtrados.append(subdominio)
    
    output_file = f'subdominios_{dominio_escolhido}.txt'
    with open(output_file, 'w') as file:
        for subdominio in subdominios_filtrados:
            file.write(f"{subdominio}\n")

    print(f"\nQuantidade de subdomínios filtrados: {len(subdominios_filtrados)}")
    print(f"Os subdomínios filtrados foram salvos em '{output_file}'\n")
    
    return output_file

def eliminar_linhas_em_branco(input_file):
    linhas_sem_branco = []
    output_file = f'clean_{os.path.basename(input_file)}'

    with open(input_file, 'r') as file:
        for linha in file:
            if linha.strip():
                linhas_sem_branco.append(linha)

    with open(output_file, 'w') as file:
        file.writelines(linhas_sem_branco)

    print(f"\nLinhas em branco eliminadas. O arquivo limpo foi salvo como '{output_file}'.\n")
    
    return output_file 

def remover_duplicatas(subdomains):
    subdomains_unicos = list(set(subdomains))
    if len(subdomains_unicos) < len(subdomains):
        print(f"\n{Fore.YELLOW}[INFO]{Style.RESET_ALL} Duplicatas encontradas e removidas. Total de subdomínios únicos: {len(subdomains_unicos)}.\n")
    return subdomains_unicos

def combinar_e_remover_duplicatas(wordlist1, wordlist2):
    subdomains = set()
    
    with open(wordlist1, 'r') as file:
        for linha in file:
            subdomains.add(linha.strip())
    
    with open(wordlist2, 'r') as file:
        for linha in file:
            subdomains.add(linha.strip())

    combined_wordlist_file = "combined_wordlist.txt"
    with open(combined_wordlist_file, 'w') as file:
        for subdomain in sorted(subdomains):
            file.write(f"{subdomain}\n")

    print(f"\n{Fore.CYAN}Wordlist combinada criada sem duplicatas: '{combined_wordlist_file}'.{Style.RESET_ALL}\n")
    
    return combined_wordlist_file

def main():
    parser = argparse.ArgumentParser(
        description="Script para verificar a acessibilidade de subdomínios a partir de uma ou duas wordlists, com opções de filtragem, eliminação de linhas em branco, remoção de duplicatas e geração de wordlists combinadas.",
        epilog=(
            "Exemplos de uso:\n"
            "  python checa-dominios.py -w subdomains.txt -v\n"
            "  python checa-dominios.py -w subdomains1.txt subdomains2.txt -v\n"
            "  python checa-dominios.py -w subdomains.txt -f exemplo.com -v\n"
            "  python checa-dominios.py -w subdomains.txt -e -v\n"
            "  python checa-dominios.py -w subdomains.txt -e -f exemplo.com -v\n"
            "  python checa-dominios.py -w subdomains.txt -c\n"
            "  python checa-dominios.py -w subdomains1.txt subdomains2.txt -g"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "-w", "--wordlist", 
        nargs='+',
        required=True, 
        help="Especifica um ou dois arquivos de wordlist com os subdomínios a serem verificados."
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Ativa a saída verbosa, mostrando detalhes de cada verificação."
    )
    parser.add_argument(
        "-f", "--filter", 
        help="Filtra a wordlist pelos subdomínios que terminam com o domínio especificado antes de realizar a verificação."
    )
    parser.add_argument(
        "-e", "--eliminate", 
        action="store_true", 
        help="Elimina as linhas em branco do arquivo de wordlist antes de realizar a verificação."
    )
    parser.add_argument(
        "-c", "--correct", 
        action="store_true", 
        help="Remove subdomínios duplicados e salva a wordlist corrigida em um novo arquivo."
    )
    parser.add_argument(
        "-g", "--generate", 
        action="store_true", 
        help="Gera uma wordlist combinada de duas listas sem duplicatas e salva em um novo arquivo."
    )
    
    args = parser.parse_args()

    verbose = args.verbose

    if len(args.wordlist) == 2:
        wordlist_file = combinar_e_remover_duplicatas(args.wordlist[0], args.wordlist[1])

        if args.generate:
            print(f"{Fore.CYAN}Wordlist combinada gerada e salva em '{wordlist_file}'.{Style.RESET_ALL}")
            return
    else:
        wordlist_file = args.wordlist[0]

    if args.eliminate:
        print(f"\nEliminando linhas em branco de '{wordlist_file}'...")
        wordlist_file = eliminar_linhas_em_branco(wordlist_file)

    try:
        with open(wordlist_file, "r") as file:
            subdomains = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"\n{Fore.RED}Arquivo '{wordlist_file}' não encontrado.{Style.RESET_ALL}\n")
        return

    if args.correct:
        subdomains = remover_duplicatas(subdomains)
        output_file = f'corrected_{os.path.basename(wordlist_file)}'
        with open(output_file, 'w') as file:
            file.writelines(f"{subdomain}\n" for subdomain in subdomains)
        print(f"{Fore.CYAN}Wordlist corrigida salva em '{output_file}'.{Style.RESET_ALL}")
        return 

    if args.filter:
        print(f"\nFiltrando subdomínios por domínio '{args.filter}'...")
        wordlist_file = filtrar_subdominios_por_dominio(wordlist_file, args.filter)
        with open(wordlist_file, "r") as file:
            subdomains = [line.strip() for line in file.readlines()]

    subdomains = remover_duplicatas(subdomains)

    results = []
    accessible_subdomains = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_subdomain, subdomain, verbose): subdomain for subdomain in subdomains}

        if not verbose:
            print("\n")
            pbar = tqdm(total=len(futures), desc="Verificando subdomínios", unit="subdomínio")
        else:
            pbar = None

        for future in as_completed(futures):
            subdomain, status = future.result()
            results.append((subdomain, status))
            if status == "Acessível":
                accessible_subdomains.append(subdomain)
            if pbar:
                pbar.update(1)

        if pbar:
            pbar.close()

    with open("subdomain_results.txt", "w") as result_file:
        for subdomain, status in results:
            result_file.write(f"{subdomain}: {status}\n")

    with open("accessible_subdomains.txt", "w") as accessible_file:
        for subdomain in accessible_subdomains:
            accessible_file.write(f"{subdomain}\n")

    print(f"\n{Fore.CYAN}Verificação completa.{Style.RESET_ALL} Resultados salvos em 'subdomain_results.txt' e subdomínios acessíveis em 'accessible_subdomains.txt'.\n")

    if len(args.wordlist) == 2 or args.filter or args.eliminate:
        os.remove(wordlist_file)

if __name__ == "__main__":
    main()
