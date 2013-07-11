<?php

// Report all PHP errors
error_reporting(E_ALL);
ini_set('display_errors', '1');


$TEST_GET_ARRAY =  array(
    "_azp_token" => "-----BEGIN+PGP+MESSAGE-----%0A++++Version%3A+GnuPG+v1.4.10+%28GNU%2FLinux%29%0A%0A++++hQEMA2DXKM0Yr%2BmKAQf%2BP7cfudt%2Bd9QomgN9%2BBgQDjS5U8tljS7NPjUPUM1bc3CP%0A++++OhMa2g5HKRxc6NQgkpV2BGAiMrYYLMg6MKT%2FHTUCTxeymAtGnNg15q0KzsXDAbcf%0A++++j%2B1hx9cx4JiYmV2B5sht%2Fhf277RNXj2Bmt5ugdE5HXlwohugaW0HcHNqnZ2yzkv8%0A++++Nskz96G81u1hvGvchPTgTmyY1KgDaZz%2FJq4hAxO3JqXl8Hrr5EWb7JSy%2F471QDAV%0A++++gBSNQrrws%2BHRmXVj0XQwpqwAesuyIIKVqaEDZ38MSWldtl%2BncQiBVX01URTx1suG%0A++++oWdopXa21l8TV8ZZx2Znsr1S1evmgrmG99Q6pMjNitLAAwFiFCU4Pz1DItZXVudx%0A++++1XzNfXglVgWex7CGlTnE7L%2BWj2HIGx1hsZpjJxIQKZzNwDgBtGNen25yCqGwGlkV%0A++++5shNPxjGl4MnlhXm%2BL%2FkFolQXtcDbi9KL5NqHfkTUU3fSVfKLkFWlR29qTzokaBn%0A++++5W1FlzPesyUAl5ZJ1Zv4hJDrWCYqNPgB0y9S8RiuUN7MDS1lGJc6juTYjbOrVHJz%0A++++tagqrzaD260BuYOUETjyGBrzwCscq0m3Bt90mlQwPP4VRCjR8A%3D%3D%0A++++%3D%2B9V8%0A++++-----END+PGP+MESSAGE-----%0A++++");


class AuthZChecker {
    /*
        Example usage: 
        $my_authz_params = array(
                 "GPG_DIR" => '/home/p/r/prasad/.gnupg',
                 "PIN_APP_NAME" => 'FAS_FCOR_MCB_GRDB_AUTHZ',
                 "CHECK_PIN_IP_VALUE" => false,
                 "PRINT_DEBUG_STATMENTS" => true
                 );

        $authz_checker = new AuthZChecker($TEST_GET_ARRAY, $my_authz_params);

            if ($authz_checker->has_err()== false){
                $wp_user_data = $authz_checker->get_wp_user_data_array();
                print_r($wp_user_data);
            }else{
                print "<h2>err</h2>";
                $authz_checker->show_error();
            };
 
    */
    
    /* -------------------------------------------------------------------
        Given a string with an "_azp_token" from a callback url, contains one big ugly function, check_azp_token(), that does the following:

        Layer 1:
                 - Parses the url and pulls out the _azp_token
                 - Decrypts the data from the _azp_token.  Uses the server's private key to match the public key originally sent for AuthZProxy registration
                 
        Layer 2:
                 - Splits the decrypted token data into 2 parts: 
                        (a) authentication/custom data and 
                        (b) signature strings
                 - Verifies the data using the AuthZProxy public key

        Layer 3:
                 - Processes the authentication data and user attribute data
                 - Saves the user attribute data in the "custom_attributes" array 
        
        Layer 4:
                 - Checks the application name against the expected app name
                 - Checks the client IP address
                 - Looks for an expired timestamp (more than 2 minutes)
                        - may be set with "$expiration_limit_in_seconds"
                        
    ------------------------------------------------------------------- */
    var $authz_params = null;  // array to hold GPG_DIR, PIN_APP_NAME, PIN_APP_NAME
    var $AUTHZ_KEY_GPG_DIR = 'GPG_DIR';
    var $AUTHZ_KEY_PIN_APP_NAME = 'PIN_APP_NAME';
    var $AUTHZ_KEY_CHECK_PIN_IP_VALUE = 'CHECK_PIN_IP_VALUE';
    var $AUTHZ_KEY_PRINT_DEBUG_STATMENTS = 'PRINT_DEBUG_STATMENTS';
    
    var $show_debug_msg = false;        // show print statements as it runs
    
    /* example:
    $test_authz_params = array(
             "GPG_DIR" => '/home/p/r/prasad/.gnupg',
             "PIN_APP_NAME" => 'FAS_FCOR_MCB_GRDB_AUTHZ',
             "CHECK_PIN_IP_VALUE" => false
             );
    */
    var $authz_proxy_token_key = '_azp_token';
    var $encrypted_azp_token = null;
    var $custom_attributes = array();   // To hold user 'sn', 'email', and 'givenname'
    var $expiration_limit_in_seconds = 120; // time limit for expired timestamp

    /* ------------------
       Error Flags
    --------------------- */
    var $err_found = false;
    var $err_msg = '';
    
    var $err_missing_authz_params = false;
    var $err_url_parse = false;
    var $err_no_azp_token = false;
    var $err_layer1_gnupg_home_directory_not_found = false;
    var $err_layer1_decrypt_failed = false;
    var $err_layer2_decrypt_failed = false;
    var $err_layer2_signature_fail = false;
    var $err_layer3_not_two_parts = false;
    var $err_layer3_attribute_data_part_fail = false;
    var $err_layer3_authen_data_part_fail = false;
    var $err_layer4_app_name_not_matched = false;
    var $err_layer4_ip_check_failed = false;
    var $err_layer4_token_time_elapsed = false;
    var $err_layer4_time_check_exception = false;
    var $err_layer3_missing_user_vals = false;
    

    
    
    /* ------------------------------------------------------ 
        Constructor
    ------------------------------------------------------ */
    function __construct($GET_ARRAY, $authz_params) {

        // Is the debug flag set to true via $authz_params (this shows print statements)?
        if (isset($authz_params[$this->AUTHZ_KEY_PRINT_DEBUG_STATMENTS])==true){
    $authz_params[$this->AUTHZ_KEY_PRINT_DEBUG_STATMENTS];
            $this->show_debug_msg = $authz_params[$this->AUTHZ_KEY_PRINT_DEBUG_STATMENTS];
        }
    
        // Make sure $authz_params has the needed keys
        //
        $this->debug_msg_bold('Constructor');
        $this->debug_msg('Check the authz params');
        $this->debug_show_array($authz_params);

        foreach (array($this->AUTHZ_KEY_GPG_DIR, $this->AUTHZ_KEY_PIN_APP_NAME, $this->AUTHZ_KEY_CHECK_PIN_IP_VALUE) as $authz_param_key){
            if (isset($authz_params[$authz_param_key])==false){
                 $this->err_found = true;
                 $this->err_missing_authz_params = true;
                 $this->err_msg = "Missing AuthZ parameter: '$authz_param_key'  (id: err_missing_authz_params)";
                 return;
            }
        }
        
       
        

        $this->authz_params = $authz_params;
        
        
        // Make sure the GET params include the authz_proxy_token_key
        $this->debug_msg("Check the GET params for the authz token key ['$this->authz_proxy_token_key']");
        if (isset($GET_ARRAY[$this->authz_proxy_token_key])==false){
            $this->err_found = true;
            $this->err_no_azp_token = true;
            return;
        }    
            
        // Check the url
        $this->encrypted_azp_token = urldecode($GET_ARRAY[$this->authz_proxy_token_key]);
        $this->check_azp_token();
    }
    
    function debug_show_array($arr){
        if ($this->show_debug_msg){
            print_r($arr);
        }
    }
    function debug_msg($msg){
        if ($this->show_debug_msg){
            print '<div style="padding:5px 15px;">' . $msg . '</div>';
        }
    }
    function debug_msg_bold($msg){
        if ($this->show_debug_msg){
            print '<br /><br /><b>' . $msg . '</b>';
        }
    }
    
    /* ------------------------------------------------------ 
        Did the authentication produce an error
    ------------------------------------------------------ */    
    function has_err(){
        if ($this->err_found){
            $this->debug_msg('Err found<br >' . $this->err_msg);
            
            return true;
        }else{
            $this->debug_msg('No err');
            return false;
        }
    }

    /* ------------------------------------------------------ 
        Authentication passed, get the Wordpress user data
    ------------------------------------------------------ */
    function get_wp_user_data_array(){
        // Build an array of user data for Wordpress
        $this->debug_msg_bold('Return WP user data (get_wp_user_data_array)');
        
        if ($this->has_err() == true){
            return null;
        }
        
        $wp_userdata = array( 'user_email' => $this->custom_attributes['mail'],
		    'user_login' => $this->custom_attributes['mail'],
		    'first_name' => $this->custom_attributes['givenname'],
		    'last_name' => $this->custom_attributes['sn']
		    );
		
		return $wp_userdata;
    }

 
    function check_azp_token(){
        $this->debug_msg_bold('Check Authz Token');
        
        /* (1) verify GPG_DIR */
        if(!(is_dir( $this->authz_params[$this->AUTHZ_KEY_GPG_DIR]))){
            $this->err_found = true;
            $this->err_layer1_gnupg_home_directory_not_found = true;
            
            return;
        }
        putenv("GNUPGHOME=" .  $this->authz_params[$this->AUTHZ_KEY_GPG_DIR]);
        
        $this->debug_msg('GPG dir found and GNUPGHOME set');
         
        /* ------------------------------------------------------ 
         Layer 1: Check the "_azp_token" encrypted_data_string 
         ------------------------------------------------------ */
        /* (2) decode azp_token */
        $gnupg_resource = gnupg_init();
        $this->debug_msg('GPG init done');

        $decrypted_parts = gnupg_decrypt($gnupg_resource, $this->encrypted_azp_token);
        
        if (gnupg_geterror($gnupg_resource)!= false){
            $this->err_found = true;
            $this->err_layer1_decrypt_failed = true;
            $this->err_msg = gnupg_geterror($gnupg_resource);
            return;
        }
        
        $decrypted_parts = urldecode($decrypted_parts);
        $this->debug_msg('decrypted_parts: '. $decrypted_parts);

        /* ------------------------------------------------------ 
            Layer 2: Unencrypted Data and Signature Strings
           - split by '&' and decode each part
           - check that the first parameter has been encoded with the 
            AuthZProxy's PGP private key
          ------------------------------------------------------ */

        /* ------------------------------------------------------ 
        Layer 3: Authentication Data and Attribute List Strings
        e.g. 12345678|2012-12-06T17:18:44Z|140.247.10.93|FAS_FCOR_MCB_GRDB_AUTHZ|P&mail=raman_prasad%40harvard.edu|sn=Prasad|givenname=Raman
        ------------------------------------------------------ */
        // Skip for now
        $decrypted_data = explode('&', $decrypted_parts);
        
        $this->debug_msg('decrypted_data');
        $this->debug_show_array($decrypted_data);
        
        if (count($decrypted_data) != 2){
            $this->err_found = true;
            $this->err_layer3_not_two_parts = true;
            return;
        }
        $authentication_data = $decrypted_data[0];
        $this->debug_msg("authentication_data: $authentication_data");
                
        $attribute_data = $decrypted_data[1];
        $this->debug_msg("attribute_data: $attribute_data");
        
        /* ------------------------------------------------------
          -- Attribute Data --
         Should be 3 attributes
        # e.g. mail=raman_prasad@harvard.edu|sn=Prasad|givenname=Raman
        ------------------------------------------------------ */
        $this->debug_msg_bold("Process attributes (email, first name (givenname), last name (sn))");
        
        $this->custom_attributes = array();
        //$attribute_data = 'mail=joanne_chang@harvard.edu|sn=Chang|givenname='; # test for failure, no 'givenname'
        foreach (explode('|', $attribute_data) as $key_val_pair) {
            $key_val_array = explode('=', $key_val_pair);
            if (count($key_val_array) == 2){
                $attr_key = $key_val_array[0];
                $attr_val = $key_val_array[1];
                if (($attr_val == null)||($attr_val == '')){
                    $this->err_found = true;
                    $this->err_layer3_missing_user_vals = true;
                    //$this->err_layer3_attribute_data_part_fail = true;
                    $this->err_msg = "No value for user attribute '$attr_key'";
                    return;
                }
                $this->custom_attributes[$attr_key] = $attr_val;
            }
        }
        
        /* check for all 3 attributes */
        if (count($this->custom_attributes)!=3){
            $this->err_found = true;
            $this->err_layer3_attribute_data_part_fail = true;
            $this->err_msg = 'Not all attributes found.  Original string: ' . $attribute_data;
            
            return;
        }
        $this->debug_msg("custom_attributes: ");
        $this->debug_show_array($this->custom_attributes);


        /* ------------------------------------------------------
        # Layer 4: Authentication Data
        ------------------------------------------------------ */
        $this->debug_msg_bold("Layer 4: Authentication Data");
        
        $authen_data_array = explode('|', $authentication_data);
         if (count($authen_data_array)!=5){
                $this->err_found = true;
                $this->err_layer3_authen_data_part_fail = true;
                $this->err_msg = 'Original string: ' . $authentication_data;                
                return;
            }
        
        $user_id = $authen_data_array[0]; 
        $login_timestamp = $authen_data_array[1]; 
        $client_ip = $authen_data_array[2]; 
        $app_id = $authen_data_array[3]; 
        $id_type = $authen_data_array[4]; 
        
        /* -----------------------------------------------------------------
            (4a) check application name
        ----------------------------------------------------------------- */
        $this->debug_msg("(4a) check application name");
        
        if ($app_id != $this->authz_params[$this->AUTHZ_KEY_PIN_APP_NAME]){
            $this->err_found = true;
            $this->err_layer4_app_name_not_matched = true;
            $this->err_msg = 'Given ID [' . $app_id . '] Should be ['. $PIN_APP_NAME . ']';                
            return; 
        }
        $this->debug_msg("ok");

        /* -----------------------------------------------------------------
            (4b) check the client IP
        ----------------------------------------------------------------- */
        $this->debug_msg("(4b) check the client IP");
        
        if ($this->authz_params[$this->AUTHZ_KEY_CHECK_PIN_IP_VALUE] == true) {
          // Verify current user's IP address.
          if ( $client_ip !== $_SERVER['REMOTE_ADDR'] ) {
            $this->err_found = true;
            $this->err_layer4_ip_check_failed = true;
            $this->err_msg = 'Given IP [' . $client_ip . '] Should be ['. $_SERVER['REMOTE_ADDR'] . ']';                
            return;
          }
        }
        $this->debug_msg("ok");
        /* -----------------------------------------------------------------
            (4c) Verify time parameter is not longer than 2 minutes (120 seconds) old. 

            Subtract timestamp value sent by PIN server from the current time (on web server)    
        ----------------------------------------------------------------- */
        $this->debug_msg("(4c) Verify time parameter is not longer than 2 minutes (120 seconds) old. ");
        
         $request_time_seconds = $_SERVER['REQUEST_TIME'];
         $login_timestamp_seconds = strtotime($login_timestamp);
         //$login_timestamp_seconds = $request_time_seconds + 10; // test
         $elapsed_seconds = abs($request_time_seconds - $login_timestamp_seconds);
         
         $this->debug_msg("request time seconds: $request_time_seconds<br />login_timestamp_seconds: $login_timestamp_seconds<br />elapsed_seconds: $elapsed_seconds");
         
         if ($elapsed_seconds > $this->expiration_limit_in_seconds){
             $this->err_found = true;
             $this->err_layer4_token_time_elapsed = true;
             $this->err_msg = 'More than 120 seconds elapsed [' . $elapsed_seconds. ' seconds]';
             return;
         }
         $this->debug_msg("ok");
         

    } // end check_azp_token

    
    function get_error_msg_html(){
        
        $err_lines = array();
        
        if ($this->err_found == false){
            $err_lines[] = 'No Error';
        };

        if ($this->err_url_parse){
            $err_lines[] =  'Failed to parse url.  (id: err_url_parse)';
        }
        if ($this->err_no_azp_token){
            $err_lines[] =  'AuthZProxy token not found (_authz_token).  (id: err_no_azp_token)';
        }
        if ($this->err_layer1_gnupg_home_directory_not_found){
            $err_lines[] =  'GNUPG directory not found.  (id: err_layer1_gnupg_home_directory_not_found)';
        }
        if ($this->err_layer1_decrypt_failed){
            $err_lines[] =  'Failed to decrypt url with private key.  (id: err_layer1_decrypt_failed)';
        }
        if ($this->err_layer2_decrypt_failed){
            $err_lines[] =  'Failed layer 2 decrypt.  (id: err_layer2_decrypt_failed)';
        }
        if ($this->err_layer2_signature_fail){
            $err_lines[] =  'Failed to verify signature with public key.  (id: err_layer2_signature_fail)';
        }
        if ($this->err_layer3_not_two_parts){
            $err_lines[] =  'Failed to find authentication and attribute parts of url.  (id: err_layer3_not_two_parts)';
        }
        if ($this->err_layer3_missing_user_vals){
                $err_lines[] =  'At least one of the user data attributes was blank.  (id: err_layer3_attribute_data_part_fail)';
            }
        if ($this->err_layer3_attribute_data_part_fail){
            $err_lines[] =  'Failed to find all user data attributes in url (email, fname, lname).  (id: err_layer3_attribute_data_part_fail)';
        }
        if ($this->err_layer3_authen_data_part_fail){
            $err_lines[] =  'Failed to find all 5 authentication data pieces.  (id: err_layer3_authen_data_part_fail)';
        }
        if ($this->err_layer4_app_name_not_matched){
            $err_lines[] =  'Failed to match application name.  (id: err_layer4_app_name_not_matched)';
        }
        if ($this->err_layer4_app_name_not_matched){
            $err_lines[] =  'Failed to pass IP address check.  (id: err_layer4_app_name_not_matched)';
        }
        if ($this->err_layer4_token_time_elapsed){
            $err_lines[] =  "Too much time passed.  Token has elapsed.  (More than $this->expiration_limit_in_seconds seconds have passed).  (id: err_layer4_token_time_elapsed)";
        }


        if ($this->err_msg != ''){
            $err_lines[] =  $this->err_msg;
        }
        
        return implode("<br />", $err_lines);
        
    }   // end get_error_msg_html


}  // end AuthZChecker class
    
/* ----------------------------------------
    Test Run
 ---------------------------------------- */
     
/*
// uncomment this to run the "authz_checker.php" file directly
$my_authz_params = array(
         "GPG_DIR" => '/home/p/r/prasad/.gnupg',
         "PIN_APP_NAME" => 'FAS_FCOR_MCB_GRDB_AUTHZ',
         "CHECK_PIN_IP_VALUE" => false,
         "PRINT_DEBUG_STATMENTS" => true
         );
         
$authz_checker = new AuthZChecker($TEST_GET_ARRAY, $my_authz_params);

    if ($authz_checker->has_err()== false){
        $wp_user_data = $authz_checker->get_wp_user_data_array();
        print_r($wp_user_data);
    }else{
        print "<h2>err</h2>";
        $authz_checker->show_error();
    };

 */ 
?>
