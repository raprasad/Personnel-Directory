<?php

require_once('authz_checker.php');

print 'hello';

$authz_checker = new AuthZChecker($TEST_GET_STR);

if ($authz_checker->has_err()== false){
    $wp_user_data = $authz_checker->get_wp_user_data_array();
    print_r($wp_user_data);
}else{
    print "<h2>err</h2>";
    $authz_checker->show_error();
};
    
?>