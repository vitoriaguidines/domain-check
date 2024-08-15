import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
from tqdm import tqdm
from colorama import Fore, Style, init
import os
import socket
from datetime import datetime

init(autoreset=True)

def check_port(subdomain, port):
    try:
        with socket.create_connection((subdomain, port), timeout=2):
            return port
    except (socket.timeout, ConnectionRefusedError, OSError):
        return None

def check_ports_parallel(subdomain, ports_to_check):
    subdomain = normalizar_subdominio(subdomain)
    
    open_ports = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_port, subdomain, port): port for port in ports_to_check}
        for future in as_completed(futures):
            port = future.result()
            if port:
                open_ports.append(port)
    return open_ports

def format_ports(ports, color_output=True):
    if color_output:
        formatted_ports = []
        for port in ports:
            if port in [80, 443]:
                formatted_ports.append(f"{Fore.CYAN}{port}{Style.RESET_ALL}")
            else:
                formatted_ports.append(f"{Fore.RED}{port}{Style.RESET_ALL}")
        return ', '.join(formatted_ports)
    else:
        return ', '.join(map(str, ports))

def check_subdomain(subdomain, verbose=False, check_ports=False):
    subdomain = normalizar_subdominio(subdomain)
    
    try:
        response = requests.get(f"http://{subdomain}", timeout=5)
        if response.status_code == 200:
            open_ports = []
            if verbose:
                print(f"\n{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {subdomain} está {Fore.GREEN}acessível{Style.RESET_ALL} (HTTP 200).")
                
                if check_ports:
                    ports_to_check = [80, 443, 21, 22, 25, 3306, 1433, 1521, 5432, 6379, 27017, 8080]
                    open_ports = check_ports_parallel(subdomain, ports_to_check)
                    
                    if open_ports:
                        formatted_ports = format_ports(open_ports, color_output=True)
                        print(f"{Fore.CYAN}Portas abertas em {subdomain}: {formatted_ports}{Style.RESET_ALL}\n")
                    else:
                        print(f"{Fore.CYAN}Nenhuma porta adicional encontrada aberta em {subdomain}.{Style.RESET_ALL}\n")
            return subdomain, "Acessível", open_ports
        else:
            if verbose:
                print(f"\n{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {subdomain} retornou {Fore.YELLOW}erro HTTP {response.status_code}{Style.RESET_ALL}.\n")
            return subdomain, f"Erro HTTP {response.status_code}", []
    except requests.exceptions.RequestException as e:
        error_message = str(e).split(': ')[-1]
        if verbose:
            print(f"\n{Fore.RED}[ERROR]{Style.RESET_ALL} {subdomain} não acessível.\nErro: {error_message}\n")
        return subdomain, "Não acessível", []

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

def normalizar_subdominio(subdominio):
    if subdominio.startswith("http://"):
        return subdominio[len("http://"):]
    elif subdominio.startswith("https://"):
        return subdominio[len("https://"):]
    return subdominio

def combinar_e_remover_duplicatas(wordlist1, wordlist2):
    subdomains = set()
    
    with open(wordlist1, 'r') as file:
        for linha in file:
            subdomains.add(normalizar_subdominio(linha.strip()))
    
    with open(wordlist2, 'r') as file:
        for linha in file:
            subdomains.add(normalizar_subdominio(linha.strip()))

    combined_wordlist_file = "combined_wordlist.txt"
    with open(combined_wordlist_file, 'w') as file:
        for subdomain in sorted(subdomains):
            file.write(f"{subdomain}\n")

    print(f"\n{Fore.CYAN}Wordlist combinada criada sem duplicatas: '{combined_wordlist_file}'.{Style.RESET_ALL}\n")
    
    return combined_wordlist_file

def remover_repeticoes_e_retornar_diferenca(wordlist1, wordlist2):
    subdomains1 = set()
    subdomains2 = set()
    
    with open(wordlist1, 'r') as file:
        for linha in file:
            subdomains1.add(normalizar_subdominio(linha.strip()))
    
    with open(wordlist2, 'r') as file:
        for linha in file:
            subdomains2.add(normalizar_subdominio(linha.strip()))
    
    diferenca = subdomains1.symmetric_difference(subdomains2)
    
    diferenca_file = "diferenca_wordlists.txt"
    with open(diferenca_file, 'w') as file:
        for subdomain in sorted(diferenca):
            file.write(f"{subdomain}\n")
    
    print(f"\n{Fore.CYAN}Arquivo com a diferença entre as wordlists salvo como '{diferenca_file}'.{Style.RESET_ALL}\n")
    
    return diferenca_file

def criar_pasta_execucao():
    timestamp = datetime.now().strftime("%y%m%d_%H%M")
    pasta_nome = f"exec_{timestamp}"
    os.makedirs(pasta_nome, exist_ok=True)
    return pasta_nome

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
            "  python checa-dominios.py -w subdomains1.txt subdomains2.txt -g\n"
            "  python checa-dominios.py -w subdomains1.txt subdomains2.txt -rm\n"
            "  python checa-dominios.py -w subdomains.txt -vp"
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
        "-vp", "--verbose_ports", 
        action="store_true", 
        help="Ativa a saída verbosa com verificação de portas abertas."
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
    parser.add_argument(
        "-rm", "--remove_matches", 
        action="store_true", 
        help="Remove as duplicações entre duas wordlists e retorna a diferença entre elas."
    )
    
    args = parser.parse_args()

    verbose = args.verbose or args.verbose_ports
    check_ports = args.verbose_ports

    pasta_execucao = criar_pasta_execucao()

    if len(args.wordlist) == 2:
        if args.remove_matches:
            diferenca_file = remover_repeticoes_e_retornar_diferenca(args.wordlist[0], args.wordlist[1])
            os.rename(diferenca_file, os.path.join(pasta_execucao, diferenca_file))
            return

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

    subdomains_ports = [] 

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_subdomain, subdomain, verbose, check_ports): subdomain for subdomain in subdomains}

        if not verbose:
            print("\n")
            pbar = tqdm(total=len(futures), desc="Verificando subdomínios", unit="subdomínio")
        else:
            pbar = None

        for future in as_completed(futures):
            subdomain, status, open_ports = future.result()
            results.append((subdomain, status))
            if status == "Acessível":
                accessible_subdomains.append(subdomain)
            if open_ports:
                subdomains_ports.append((subdomain, open_ports))
            if pbar:
                pbar.update(1)

        if pbar:
            pbar.close()

    with open(os.path.join(pasta_execucao, "subdomain_results.txt"), "w") as result_file:
        for subdomain, status in results:
            result_file.write(f"{subdomain}: {status}\n")

    with open(os.path.join(pasta_execucao, "accessible_subdomains.txt"), "w") as accessible_file:
        for subdomain in accessible_subdomains:
            accessible_file.write(f"{subdomain}\n")

    if check_ports:
        with open(os.path.join(pasta_execucao, "subdomains_ports.txt"), "w") as ports_file:
            for subdomain, ports in subdomains_ports:
                formatted_ports = format_ports(ports, color_output=False)
                ports_file.write(f"{subdomain}:\n")
                ports_file.write(f"Portas abertas: {formatted_ports}\n\n")

    print(f"\n{Fore.CYAN}Verificação completa.{Style.RESET_ALL} Resultados salvos na pasta '{pasta_execucao}'.\n")

    if len(args.wordlist) == 2 or args.filter or args.eliminate:
        os.remove(wordlist_file)

if __name__ == "__main__":
    main()
