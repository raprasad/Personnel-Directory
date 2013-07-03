<?php

// Report all PHP errors (see changelog)
ini_set("display_errors","1");
error_reporting(E_ALL);


$GPG_BIN = '/usr/bin/gpg';
$GPG_DIR = '/home/p/r/prasad/.gnupg';
$PIN_APP_NAME = 'FAS_FCOR_MCB_GRDB_AUTHZ';


$test_msg = "https://adminapps.mcb.harvard.edu/mcb-grad/hu_azp/callback?_azp_token=-----BEGIN+PGP+MESSAGE-----%0D%0AVersion%3A+Cryptix+OpenPGP+0.20050418%0D%0A%0D%0AhQEMA%2FVD%2FGQNXDZ2AQgArrnoVaz2SsDBvIcIdi%2BtRbOwlXZf0S0jNA3OCpL%2F5D5b%0D%0ADQIXT5D9urAGJPyjN0kB%2BG2%2BL0e22fJy3S3QjDhbYPm97GKywHUJDW3K9BagYEaD%0D%0A1Mry8XRGDY5bf%2F6xfMq%2Bq3tT%2FGs1WpfDQLT7zzzRa0T6dOusP9RjWm6%2F%2FfLrPtSw%0D%0AIko8vmgL7vdvU4QjqmUb0dMsUw0VEfsagRDcSTAglfhryOFWf7%2B%2BDerJqagHQSdH%0D%0A%2BGYkxCCcdwvWe9Ta7qJcVIM%2BfFaqYTDSSjE1h%2Fz3XDeilUgJAyCVRl%2FRCcoWwhrn%0D%0A47lSV2DxIjVo1D%2BWQeFR%2BbPS9S3uU9af%2BdLM2Zh4sqUBKdYB12oj1GVnVaHxTSA2%0D%0Ac5kKetfDdS5mAv3prmQdkYrPoF1gBwNfM1NGjjDC38Uhz%2BhDavCVVsx6FaVP2Tvu%0D%0AncCgA2Zrj46lTObQsbNcIYUgi5XNA2c3ArrbKGc2LmgFqaNjUP6LrcysurpojK74%0D%0ArAVJiXcGaeD8meCGZGZyMlm%2FcYpAPY5ikknTq88c70Eq2EVHFvV2HKB7FACrTkSH%0D%0AsKs5ZaSAvm2h7%2BxtvXIjhixkzRRxDiq5qZJq6VIK9bYkbzsJ%2FCVxJ0htkHq8yuYG%0D%0AtMAe3iE54kaGZpaCm4ozjqXPQa47%2FASgcUBOd6qMX%2FFLnOdWzxENCSwtXX1qEZvT%0D%0ALqOsDULeZtwtrNXWB11zO4As4etNbd%2FQbAjET%2FkhjJgBNuOw5vUQZ28g8Q%3D%3D%0D%0A%3DgFeY%0D%0A-----END+PGP+MESSAGE-----%0D%0A";


//phpinfo();
print 'hi';

   $stdout = "";
  $stderr = "";
 
// sudo gpg --decrypt test_file.txt.gpg
 // Use gnupg to verify signature.
  $descriptorspec = array(
    0 => array('pipe', 'r'), // stdin
    1 => array('pipe', 'w'), // stdout
    2 => array("file", "/tmp/error-output.txt", "a")  
    //2 => array('pipe', 'w') // stderr
  );


$cmd_stmt = '/usr/bin/gpg --homedir ' . $GPG_DIR . ' --decrypt test_file.txt.gpg';
print '<p>' . $cmd_stmt . '</p>';

 $process = proc_open($cmd_stmt, $descriptorspec, $pipes);
if (!is_resource($process)) {
      echo stream_get_contents($pipes[0]);	
}else{

	echo stream_get_contents($pipes[1]);
	fclose($pipes[1]);
}
 //fwrite($pipes[0], $pgp_message);
 // fclose($pipes[0]);
// proc_close in order to avoid a deadlock
 $return_value = proc_close($process);

 echo "<br />command returned $return_value\n";

print '<p>ok';





?>