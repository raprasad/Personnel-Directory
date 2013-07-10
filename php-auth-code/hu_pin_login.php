<?php

require_once('authz_checker.php');

print 'hello 2<br />';

$test_authz_params = array(
         "GPG_DIR" => '/home/p/r/prasad/.gnupg',
         "PIN_APP_NAME" => 'FAS_FCOR_MCB_GRDB_AUTHZ',
         "CHECK_PIN_IP_VALUE" => false
         );
         
$authz_checker = new AuthZChecker($TEST_GET_ARRAY, $test_authz_params);

    if ($authz_checker->has_err()== false){
        $wp_user_data = $authz_checker->get_wp_user_data_array();
        print_r($wp_user_data);
    }else{
        print "<h2>err</h2>";
        $authz_checker->show_error();
    };

    
?>