from logging import getLogger, ERROR, basicConfig, DEBUG

getLogger("scapy.runtime").setLevel(ERROR) # Que no muestre warning
basicConfig(level=DEBUG, format='%(threadName)s: %(message)s')

from colorama.ansi      import clear_screen, AnsiCursor
from concurrent.futures import ThreadPoolExecutor
from colorama           import Fore, Back, init
from multiprocessing    import cpu_count, Pool
from argparse           import ArgumentParser
from socket             import getservbyport
from scapy.sendrecv     import sr1, conf, sr
from sys                import exit, argv
from scapy.volatile     import RandShort
from scapy.layers.inet  import IP, TCP
from tqdm               import tqdm

conf.verb = 0 #Que no muestre datos en pantalla sobre el proceso


def scann_ports(args):
    try:
        addr, range_, process_id, thread_is = args
        min_p, max_p = range_ # puertos a escanear
    
        open_ports = []
        for puerto in tqdm(range(min_p, max_p), desc=f"\r{AnsiCursor.FORWARD(process_id)}{Fore.LIGHTYELLOW_EX}Proceso {Fore.LIGHTCYAN_EX}{process_id} thread {Fore.LIGHTCYAN_EX}{process_id}{Fore.RESET}", position=process_id + 1, leave=False):
            puertoOrigen = RandShort()
            paquete = IP(dst = addr)/TCP(sport = puertoOrigen, dport = puerto, flags = "S")
            respuesta = sr1(paquete, timeout = 2)
            if("NoneType" in str(type(respuesta))): pass
            elif(respuesta.haslayer(TCP) and respuesta.getlayer(TCP).flags == 0x12):
                p = IP(dst = addr)/TCP(sport = puertoOrigen, dport = puerto, flags = "R")
                rst = sr(p, timeout = 1)
                try: servicio = getservbyport(puerto)
                except: servicio = "¿?"
                open_ports.append((puerto, servicio))
    except KeyboardInterrupt:pass
    print("\n\n")
    return open_ports

def scann_ports_thread(args):
    addr, range_, process_id, threads = args
    open_ports = []
    args_list = []
    k,j = range_
    for i in range(threads):
        j = k # valor minimo
        k += (range_[1] - range_[0]) // threads # dividir los puertos a escanear en la cantidad especificada
        # si la operacion de division da resto, el ultimo core sera el encargado de escanear los ultimos puertos de mas:
        if i == range(threads)[-1]: k += (range_[1] - range_[0]) % threads
        args_list.append((addr, (j, k), process_id, i))
        print(f"\r{Fore.LIGHTYELLOW_EX} process id {Fore.LIGHTCYAN_EX}{process_id} thread id {Fore.LIGHTCYAN_EX}{i} {Fore.LIGHTYELLOW_EX}>>> {Fore.LIGHTCYAN_EX}{addr}{Fore.LIGHTYELLOW_EX}:{Fore.LIGHTCYAN_EX}{(j, k)}{Fore.RESET}")
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for i in args_list:
            open_ports.append(executor.submit(scann_ports, i).result())
    return open_ports
        
if __name__ == '__main__':
    init()
    parser = ArgumentParser(
                prog = __doc__,
                description = """
                    Escaner de puertos multiproceso
                """,
                epilog="""
                """
            )
    parser.add_argument(
                            "-a",
                            "--addr",        
                            help="direccion a la que realizar el escaneo", 
                            type=str,
                        )
    parser.add_argument(
                            "-p",
                            "--ports",        
                            help="puertos a escanar, por defecto todos. se puede especificar un rango haciendo uso de un guion: 10-24", 
                            type=str,
                            default=(1, 2**16)
                        )
    parser.add_argument(
                            "-up",
                            "--utilization-percentage",        
                            help="porcentaje de cores a usar. Por defecto se usa 80%%", 
                            type=int,
                            default=80
                        )
    parser.add_argument(
                            "-t",
                            "--thread-cores",        
                            help="cantidad de hilos a usar por proceso, por defecto 4", 
                            type=int,
                            default=4
                        )

    if len(argv) <= 1:
        parser.print_help()
        exit(1)
    
        
    parser = parser.parse_args()
    listaPuertos = parser.ports
    if type(parser.ports) != tuple:
        try: listaPuertos = (int(parser.ports.split("-")[0]), int(parser.ports.split("-")[1]))
        except ValueError: print(f"{Fore.LIGHTRED_EX}--ports{Fore.RESET} no tiene un rango valido definido")
    
    cores = int(cpu_count() * parser.utilization_percentage / 100)
    
    print(listaPuertos)
    print(f"\n{Fore.LIGHTYELLOW_EX}Numero de procesos a usar: {cores}{Fore.RESET}")
    print(f"\n{Fore.LIGHTYELLOW_EX}Numero de hilos por proceso a usar: {parser.thread_cores}{Fore.RESET}")
    print(f"\n{Fore.LIGHTYELLOW_EX}Puertos a escanear por proceso: {(listaPuertos[1] - listaPuertos[0]) // cores}{Fore.RESET}")
    
    args_list = []
    j, k = (listaPuertos[0], listaPuertos[0])
    for i in range(cores):
        j = k # valor minimo
        k += (listaPuertos[1] - listaPuertos[0]) // cores # dividir los puertos a escanear en la cantidad especificada
        # si la operacion de division da resto, el ultimo core sera el encargado de escanear los ultimos puertos de mas:
        if i == range(cores)[-1]: k += (listaPuertos[1] - listaPuertos[0]) % cores
        args_list.append((parser.addr, (j, k), i, parser.thread_cores))
        print(f"{Fore.LIGHTYELLOW_EX}process id {Fore.LIGHTCYAN_EX}{i} {Fore.LIGHTYELLOW_EX}>>> {Fore.LIGHTCYAN_EX}{parser.addr}{Fore.LIGHTYELLOW_EX}:{Fore.LIGHTCYAN_EX}{(j, k)}{Fore.RESET}")
    
    with Pool(processes=int(cores)) as pool: 
        try: results = list(pool.imap(scann_ports_thread, args_list))
        except KeyboardInterrupt: pass
    print(results)
    print(clear_screen())
    for result in results:
        for data in result:
            for port, service in data:
                print(f"\r{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTGREEN_EX}{Back.LIGHTBLUE_EX}ABIERTO{Back.RESET}{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTYELLOW_EX} {port} {Fore.LIGHTGREEN_EX}/{Fore.LIGHTYELLOW_EX}tcp {Fore.LIGHTGREEN_EX}->{Fore.LIGHTGREEN_EX} {service} {Fore.RESET}")

    
    """
listaPuertos = list(range(20,130)) #La lista de puertos a escanear
host = "192.168.1.1" #Aquí la IP que quieres escánear

print("Escaneando los puertos de la IP:",host)
for puerto in listaPuertos:
    puertoOrigen = RandShort()
    paquete = IP(dst = host)/TCP(sport = puertoOrigen, dport = puerto, flags = "S")
    respuesta = sr1(paquete, timeout = 2)
    if("NoneType" in str(type(respuesta))):
        pass
    elif(respuesta.haslayer(TCP) and respuesta.getlayer(TCP).flags == 0x12):
        p = IP(dst = host)/TCP(sport = puertoOrigen, dport = puerto, flags = "R")
        
        rst = sr(p, timeout = 1)
        try:
            servicio = getservbyport(puerto)
        except KeyboardInterrupt:
            servicio = "¿?"
        print("[ABIERTO]",puerto," ->",servicio)"""