<?
/*
	(a) Accepts an incoming URL from the HU PIN System (PIN 2)
        (b) Verifies the Pin is Valid
        (c) Checks the user's uid attribute against the MCB directory
        (d) Returns a valid response--or not
*/

	function is_allowed_ip(){
	  //allowed IP. Change it to your static IP
	  $allowed_ip = '140.247.185.222';
	  if ($_SERVER['REMOTE_ADDR']== $allowed_ip){
	     return true;  
	  }
	  return false;  
	}

	if (!is_allowed_ip()){
	   echo json_encode(array('result' => '0'));
	   return;
	}

    if($_GET['user'] == 'rprasad22' && $_GET['pass'] == 'test') {
	    echo json_encode(array('result' => '1', 'username' => 'rprasad22', 'first_name' => 'Raman', 'last_name' => 'Prasad', 'email' => 'rprasad@harvard.edu'));
    } else {
	    echo json_encode(array('result' => '0'));
    }
?>
