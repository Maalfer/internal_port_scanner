# internal_port_scanner

----

Escaner de puertos usando scapy, multithrearing y multiprocessing.

modulos necesarios:
```python
concurrent, colorama, multiprocessing, argparse, socket, scapy, sys, tqdm              
```

instalacion de modulos necesarios:
```shell
pip install -r requirements.txt
```

Uso:
```shell
C:\Users\Desmon0xFF\Desktop\internal_port_scanner>python internal_port_scanner.py
usage: internal_port_scanner.py [-h] [-a ADDR] [-p PORTS] [-up UTILIZATION_PERCENTAGE] [-t THREAD_CORES]

Escaner de puertos multiproceso

options:
  -h, --help            show this help message and exit
  -a ADDR, --addr ADDR  direccion a la que realizar el escaneo
  -p PORTS, --ports PORTS
                        puertos a escanar, por defecto todos. se puede especificar un rango haciendo uso de un guion: 10-24
  -up UTILIZATION_PERCENTAGE, --utilization-percentage UTILIZATION_PERCENTAGE
                        porcentaje de cores a usar. Por defecto se usa 80%
  -t THREAD_CORES, --thread-cores THREAD_CORES
                        cantidad de hilos a usar por proceso, por defecto 4
```

- `-a`: direccion IP a escanear
- `-p`: rango de puertos a escanear. Por defecto se escanea todos los puertos existentes
- `-up`: cantidad de cores a usar, a de especificarse usando porcentajes. Por defecto se usa un 8o% de los que el sistema disponga.
- `-t`: cantidad de hilos a usar por proceso, a de especificarse usando un numero. Por defecto se usa un 4.

Ejemplo practico para escanera la direccion `192.168.1.1` usando el 50% de cores disponnibles, usando 4 hilos por proceso y escaneando puertos del 1 al 3000:
```shell
python internal_port_scanner.py -a 192.168.1.1 -up 50 -p 1-3000
```

----