<?php

require_once('authz_checker.php');  // home of the AuthZChecker class


//add_filter( 'authenticate', 'hu_pin2_authz_check', 10, 3 );


$A_TEST_GET_ARRAY =  array(
    "_azp_token" => "-----BEGIN+PGP+MESSAGE-----%0A++++Version%3A+GnuPG+v1.4.10+%28GNU%2FLinux%29%0A%0A++++hQEMA2DXKM0Yr%2BmKAQf%2BP7cfudt%2Bd9QomgN9%2BBgQDjS5U8tljS7NPjUPUM1bc3CP%0A++++OhMa2g5HKRxc6NQgkpV2BGAiMrYYLMg6MKT%2FHTUCTxeymAtGnNg15q0KzsXDAbcf%0A++++j%2B1hx9cx4JiYmV2B5sht%2Fhf277RNXj2Bmt5ugdE5HXlwohugaW0HcHNqnZ2yzkv8%0A++++Nskz96G81u1hvGvchPTgTmyY1KgDaZz%2FJq4hAxO3JqXl8Hrr5EWb7JSy%2F471QDAV%0A++++gBSNQrrws%2BHRmXVj0XQwpqwAesuyIIKVqaEDZ38MSWldtl%2BncQiBVX01URTx1suG%0A++++oWdopXa21l8TV8ZZx2Znsr1S1evmgrmG99Q6pMjNitLAAwFiFCU4Pz1DItZXVudx%0A++++1XzNfXglVgWex7CGlTnE7L%2BWj2HIGx1hsZpjJxIQKZzNwDgBtGNen25yCqGwGlkV%0A++++5shNPxjGl4MnlhXm%2BL%2FkFolQXtcDbi9KL5NqHfkTUU3fSVfKLkFWlR29qTzokaBn%0A++++5W1FlzPesyUAl5ZJ1Zv4hJDrWCYqNPgB0y9S8RiuUN7MDS1lGJc6juTYjbOrVHJz%0A++++tagqrzaD260BuYOUETjyGBrzwCscq0m3Bt90mlQwPP4VRCjR8A%3D%3D%0A++++%3D%2B9V8%0A++++-----END+PGP+MESSAGE-----%0A++++");

function hu_pin2_authz_check(){
    print 'hello 3<br />';
    global $A_TEST_GET_ARRAY;

    $test_authz_params = array(
             "GPG_DIR" => '/home/p/r/prasad/.gnupg',
             "PIN_APP_NAME" => 'FAS_FCOR_MCB_GRDB_AUTHZ',
             "CHECK_PIN_IP_VALUE" => false,
             "PRINT_DEBUG_STATMENTS" => true
             
             );

    $authz_checker = new AuthZChecker($A_TEST_GET_ARRAY, $test_authz_params);

        if ($authz_checker->has_err()== false){
            $wp_user_data = $authz_checker->get_wp_user_data_array();
            print_r($wp_user_data);
        }else{
            print "<h2>err</h2>";
            $authz_checker->show_error();
        };
    
}
hu_pin2_authz_check();
    
?>