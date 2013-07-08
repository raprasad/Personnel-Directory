<?php
/*
     One big ugly function that does the following:
         - Layer 1:
             - Parses the url and pulls out the _azp_token
             - Decrypts the data from the _azp_token.  Use the private key, matching the public key sent for AuthZ registration
         - Layer 2:
             - Splits the token decrypted data into 2 parts: (a) authentication/custom data and (b) signature strings
             - Verifies the data using the AuthZ public key
         - Layer 3:
             - Splits the authentication data and attribute data
             - Saves the attribute data to the 
         - Layer 4:
             - Checks the application name against the expected app name
             - Checks the client IP address
             - Looks for an expired timestamp (more than 2 minutes)
*/

$test_msg = "https://adminapps.mcb.harvard.edu/mcb-grad/hu_azp/callback?_azp_token=-----BEGIN+PGP+MESSAGE-----%0D%0AVersion%3A+Cryptix+OpenPGP+0.20050418%0D%0A%0D%0AhQEMA%2FVD%2FGQNXDZ2AQgArrnoVaz2SsDBvIcIdi%2BtRbOwlXZf0S0jNA3OCpL%2F5D5b%0D%0ADQIXT5D9urAGJPyjN0kB%2BG2%2BL0e22fJy3S3QjDhbYPm97GKywHUJDW3K9BagYEaD%0D%0A1Mry8XRGDY5bf%2F6xfMq%2Bq3tT%2FGs1WpfDQLT7zzzRa0T6dOusP9RjWm6%2F%2FfLrPtSw%0D%0AIko8vmgL7vdvU4QjqmUb0dMsUw0VEfsagRDcSTAglfhryOFWf7%2B%2BDerJqagHQSdH%0D%0A%2BGYkxCCcdwvWe9Ta7qJcVIM%2BfFaqYTDSSjE1h%2Fz3XDeilUgJAyCVRl%2FRCcoWwhrn%0D%0A47lSV2DxIjVo1D%2BWQeFR%2BbPS9S3uU9af%2BdLM2Zh4sqUBKdYB12oj1GVnVaHxTSA2%0D%0Ac5kKetfDdS5mAv3prmQdkYrPoF1gBwNfM1NGjjDC38Uhz%2BhDavCVVsx6FaVP2Tvu%0D%0AncCgA2Zrj46lTObQsbNcIYUgi5XNA2c3ArrbKGc2LmgFqaNjUP6LrcysurpojK74%0D%0ArAVJiXcGaeD8meCGZGZyMlm%2FcYpAPY5ikknTq88c70Eq2EVHFvV2HKB7FACrTkSH%0D%0AsKs5ZaSAvm2h7%2BxtvXIjhixkzRRxDiq5qZJq6VIK9bYkbzsJ%2FCVxJ0htkHq8yuYG%0D%0AtMAe3iE54kaGZpaCm4ozjqXPQa47%2FASgcUBOd6qMX%2FFLnOdWzxENCSwtXX1qEZvT%0D%0ALqOsDULeZtwtrNXWB11zO4As4etNbd%2FQbAjET%2FkhjJgBNuOw5vUQZ28g8Q%3D%3D%0D%0A%3DgFeY%0D%0A-----END+PGP+MESSAGE-----%0D%0A";

$TEST_GET_STR =  array(
    "_azp_token" => "-----BEGIN PGP MESSAGE-----
    Version: GnuPG v1.4.10 (GNU/Linux)

    hQEMA2DXKM0Yr+mKAQf+P7cfudt+d9QomgN9+BgQDjS5U8tljS7NPjUPUM1bc3CP
    OhMa2g5HKRxc6NQgkpV2BGAiMrYYLMg6MKT/HTUCTxeymAtGnNg15q0KzsXDAbcf
    j+1hx9cx4JiYmV2B5sht/hf277RNXj2Bmt5ugdE5HXlwohugaW0HcHNqnZ2yzkv8
    Nskz96G81u1hvGvchPTgTmyY1KgDaZz/Jq4hAxO3JqXl8Hrr5EWb7JSy/471QDAV
    gBSNQrrws+HRmXVj0XQwpqwAesuyIIKVqaEDZ38MSWldtl+ncQiBVX01URTx1suG
    oWdopXa21l8TV8ZZx2Znsr1S1evmgrmG99Q6pMjNitLAAwFiFCU4Pz1DItZXVudx
    1XzNfXglVgWex7CGlTnE7L+Wj2HIGx1hsZpjJxIQKZzNwDgBtGNen25yCqGwGlkV
    5shNPxjGl4MnlhXm+L/kFolQXtcDbi9KL5NqHfkTUU3fSVfKLkFWlR29qTzokaBn
    5W1FlzPesyUAl5ZJ1Zv4hJDrWCYqNPgB0y9S8RiuUN7MDS1lGJc6juTYjbOrVHJz
    tagqrzaD260BuYOUETjyGBrzwCscq0m3Bt90mlQwPP4VRCjR8A==
    =+9V8
    -----END PGP MESSAGE-----
    ",
    "_azp_token_2" => "-----BEGIN+PGP+MESSAGE-----%0D%0AVersion%3A+Cryptix+OpenPGP+0.20050418%0D%0A%0D%0AhQEMA%2FVD%2FGQNXDZ2AQgArrnoVaz2SsDBvIcIdi%2BtRbOwlXZf0S0jNA3OCpL%2F5D5b%0D%0ADQIXT5D9urAGJPyjN0kB%2BG2%2BL0e22fJy3S3QjDhbYPm97GKywHUJDW3K9BagYEaD%0D%0A1Mry8XRGDY5bf%2F6xfMq%2Bq3tT%2FGs1WpfDQLT7zzzRa0T6dOusP9RjWm6%2F%2FfLrPtSw%0D%0AIko8vmgL7vdvU4QjqmUb0dMsUw0VEfsagRDcSTAglfhryOFWf7%2B%2BDerJqagHQSdH%0D%0A%2BGYkxCCcdwvWe9Ta7qJcVIM%2BfFaqYTDSSjE1h%2Fz3XDeilUgJAyCVRl%2FRCcoWwhrn%0D%0A47lSV2DxIjVo1D%2BWQeFR%2BbPS9S3uU9af%2BdLM2Zh4sqUBKdYB12oj1GVnVaHxTSA2%0D%0Ac5kKetfDdS5mAv3prmQdkYrPoF1gBwNfM1NGjjDC38Uhz%2BhDavCVVsx6FaVP2Tvu%0D%0AncCgA2Zrj46lTObQsbNcIYUgi5XNA2c3ArrbKGc2LmgFqaNjUP6LrcysurpojK74%0D%0ArAVJiXcGaeD8meCGZGZyMlm%2FcYpAPY5ikknTq88c70Eq2EVHFvV2HKB7FACrTkSH%0D%0AsKs5ZaSAvm2h7%2BxtvXIjhixkzRRxDiq5qZJq6VIK9bYkbzsJ%2FCVxJ0htkHq8yuYG%0D%0AtMAe3iE54kaGZpaCm4ozjqXPQa47%2FASgcUBOd6qMX%2FFLnOdWzxENCSwtXX1qEZvT%0D%0ALqOsDULeZtwtrNXWB11zO4As4etNbd%2FQbAjET%2FkhjJgBNuOw5vUQZ28g8Q%3D%3D%0D%0A%3DgFeY%0D%0A-----END+PGP+MESSAGE-----%0D%0A");

$GPG_BIN = '/usr/bin/gpg';
$GPG_DIR = '/home/p/r/prasad/.gnupg';
$PIN_APP_NAME = 'FAS_FCOR_MCB_GRDB_AUTHZ';

#12345678|2012-12-06T17:18:44Z|140.247.10.93|FAS_FCOR_MCB_GRDB_AUTHZ|P&mail=raman_prasad%40harvard.edu|sn=Prasad|givenname=Raman 

class AuthZChecker {

    var $encrypted_azp_token = null;

    // Error Flags
    var $err_found = false;
    var $err_msg = '';
    
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
    var $err_missing_user_vals = false;
    
    // To hold user 'sn', 'email', and 'givenname'
    var $custom_attributes = array();
    
    function has_err(){
        if ($this->err_found){
            print '<br />err found';
            print '<br >' . $this->err_msg;
            return true;
        }else{
            print '<br />No err';
            return false;
        }
    }

    function __construct($GET_ARRAY) {
        print 'authz';
         if ($GET_ARRAY['_azp_token']) {
            $this->encrypted_azp_token = $GET_ARRAY['_azp_token'];
            $this->check_azp_token();
         }else{
            $this->err_found = true;
            $this->err_no_azp_token = true;
            return;
         }
    }
 
    function check_azp_token(){
        global $GPG_DIR;
        print '<br />check_azp_token';
        
        /* (1) verify GPG_DIR */
        if(!(is_dir($GPG_DIR))){
            $this->err_found = true;
            $this->err_layer1_gnupg_home_directory_not_found = true;
            
            return;
        }
        putenv("GNUPGHOME=$GPG_DIR");
        
        print '<br />gpg dir found--';

        /* ------------------------------------------------------ */
        /* Layer 1: Check the "_azp_token" encrypted_data_string */
        /* ------------------------------------------------------ */
        /* (2) decode azp_token */
        $gnupg_resource = gnupg_init();
        $decrypted_parts = gnupg_decrypt($gnupg_resource, $this->encrypted_azp_token);
        
        if (!(gnupg_geterror($gnupg_resource)=== false)){
            $this->err_found = true;
            $this->err_layer1_decrypt_failed = true;
            $this->err_msg = gnupg_geterror($gnupg_resource);
            return;
        }
        //gnupg_adddecryptkey($res,"8660281B6051D071D94B5B230549F9DC851566DC","test");
        //$plain = gnupg_decrypt($res, $this->encrypted_azp_token );
        //print '<br />gnupg_decrypt done';
        
        echo $decrypted_parts;
        $decrypted_parts = urldecode($decrypted_parts);
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
        # Skip for now
        $decrypted_data = explode('&', $decrypted_parts);
        print_r($decrypted_data);
        if (!(count($decrypted_data) == 2)){
            $this->err_found = true;
            $this->err_layer3_not_two_parts = true;
            return;
        }
        $authentication_data = $decrypted_data[0];
        echo "<br />authentication_data: $authentication_data";
        
        $attribute_data = $decrypted_data[1];
        echo "<br />attribute_data: $attribute_data";
        
        # split apart attribute data
        # e.g. mail=raman_prasad%40harvard.edu|sn=Prasad|givenname=Raman
        $this->custom_attributes = array();
        foreach (explode('|', $attribute_data) as $key_val_pair) {
            $key_val_array = explode('=', $key_val_pair);
            if (count($key_val_array) == 2){
                $this->custom_attributes[$key_val_array[0]] = $key_val_array[1];
            }
        }
        print_r($this->custom_attributes);
        print 'ok';


    } // end check_azp_token
}

$authz_checker = new AuthZChecker($TEST_GET_STR);
$authz_checker->has_err();
    
    

 /*   
     # break the url into key/value pairs
     try:
         self.url_dict = parse_qs(urlparse(self.url_full_path).query)
     except:
         self.err_url_parse = True
         return

     for k, v in self.url_dict.iteritems():
         self.url_dict.update({k: v[0].strip()})
     
     #---------------------------------------------------
     # Layer 1: Check the "_azp_token" encrypted_data_string 
     #---------------------------------------------------
     encrypted_data_string = self.url_dict.get(URL_KEY_AZP_TOKEN, None)
     if encrypted_data_string is None:
         self.err_no_azp_token = True
         return
             
     if not os.path.isdir(self.gnupghome):
         self.add_err('directory not found: %s' % self.gnupghome)
         self.err_layer1_gnupg_home_directory_not_found = True
         return
         
     gpg_obj = gnupg.GPG(gnupghome=self.gnupghome, verbose=self.is_debug)
     
     if self.gpg_passphrase:
         decrypted_data = gpg_obj.decrypt(encrypted_data_string\
                                         , passphrase=self.gpg_passphrase)
     else:
         decrypted_data = gpg_obj.decrypt(encrypted_data_string)
         
     #print '\n\ndecrypted_data: %s' % decrypted_data

     if decrypted_data is None:
         self.err_layer1_decrypt_failed = True
         return
     
     #---------------------------------------------------
     # Layer 2: Unencrypted Data and Signature Strings
     #   - split by '&' and decode each part
     #   - check that the first parameter has been encoded the AuthZProxy's PGP private key
     #---------------------------------------------------
     decrypt_parts = decrypted_data.data.split('&')
     if not len(decrypt_parts) == 2:
         self.err_layer2_decrypt_failed = True
         return
         
     url_encoded_data_string,  url_encoded_signature_string = decrypt_parts

     decoded_data_string = urllib.unquote(url_encoded_data_string) 
     self.decoded_data_string_for_potential_err_msg = decoded_data_string
     decoded_signature_string = urllib.unquote(url_encoded_signature_string)

     #print 'url_encoded_data_string: [%s]' % decoded_data_string
     #print ''
     #print 'url_encoded_signature_string: [%s]' % decoded_signature_string
     
     pgp_msg = self.get_pgp_msg(decoded_data_string, decoded_signature_string)

     v = gpg_obj.verify(pgp_msg)
     if v is not None and v.valid==True:
         pass
         #print 'yes'
     else:
         self.add_err('Signature fail.\npgp message: [%s]\ndecoded_data_string: [%s]\ndecoded_signature_string: [%s]' % (pgp_msg, decoded_data_string, decoded_signature_string))
         self.err_layer2_signature_fail = True
         return

     #---------------------------------------------------
     # Layer 3: Authentication Data and Attribute List Strings
     #---------------------------------------------------
     # 12345678|2012-12-06T17:18:44Z|140.247.10.93|FAS_FCOR_MCB_GRDB_AUTHZ|P&mail=raman_prasad%40harvard.edu|sn=Prasad|givenname=Raman
     
     layer3_data_parts = decoded_data_string.split('&')
     if not len(layer3_data_parts) == 2:
         self.err_layer3_not_two_parts = True
         return
     authentication_data, attribute_data = layer3_data_parts

     # split apart attribute data
     # e.g. mail=raman_prasad%40harvard.edu|sn=Prasad|givenname=Raman
     try:
         self.custom_attributes = {}
         for pair in attribute_data.split('|'):
             if len(pair.split('=')) == 2:
                 k, v = pair.split('=')
                 self.custom_attributes[k] = urllib.unquote(v)            
     except:
         self.err_layer3_attribute_data_part_fail = True
         self.add_err('original attribute_data string: [%s]' % attribute_data)
         return
                     
     
     # split apart Authentication Data 
     authen_data_parts = authentication_data.split('|')
     if not len(authen_data_parts) == 5:
         self.err_layer3_authen_data_part_fail = True
         self.add_err('original authentication_data string: [%s]' % authentication_data)
         return        
         
     #---------------------------------------------------
     # Layer 4: Authentication Data
     #---------------------------------------------------
     # 12345678|2012-12-06T17:18:44Z|140.247.10.93|FAS_FCOR_MCB_GRDB_AUTHZ|P
     user_id, login_timestamp, client_ip, app_id, id_type = authen_data_parts

     # (4a) check application name
     if not app_id in self.app_names:
         self.err_layer4_app_name_not_matched = True
         self.add_err('authz app id: [%s] actual app id: [%s]' % (app_id, self.app_names))
         self.add_err('\nAdditional info: \ndecoded_data_string: [%s]\ndecoded_signature_string: [%s]' % ( decoded_data_string, decoded_signature_string))
         
         return
     
     #return # skip IP and timestamp verifiation settings
     
     # (4b) verify the IP
     if self.is_debug and self.user_request_ip == '127.0.0.1':
         # allow client address of 127.0.0.1 for testing
         pass
     elif not client_ip == self.user_request_ip:
         self.err_layer4_ip_check_failed = True            
         self.add_err('authz client_ip: [%s] user ip: [%s]' % (client_ip, self.user_request_ip))
         self.add_err('\nAdditional info: \ndecoded_data_string: [%s]\ndecoded_signature_string: [%s]' % (decoded_data_string, decoded_signature_string))
         
         return
             
     # (4c) Check the timestamp
     dt_pat = '%Y-%m-%dT%H:%M:%SZ'
     try:
         login_datetime_obj = datetime.strptime(login_timestamp, dt_pat)
         time_now = datetime.utcnow()
         time_diff = time_now - login_datetime_obj
         if time_diff.seconds < 0 or time_diff.seconds > self.expiration_time_seconds:
             self.err_layer4_token_time_elapsed = True
             msg('%s second rule failed verification: \nauthz msg: [%s] \nsystem: [%s]' % (self.expiration_time_seconds, login_timestamp, time_now))
             self.add_err('\nAdditional info: \ndecoded_data_string: [%s]\ndecoded_signature_string: [%s]' % ( decoded_data_string, decoded_signature_string))
             
             return
     except:
         self.err_layer4_time_check_exception = True
         
         msg('time diff failed: auth z timestamp str [%s]' % (login_timestamp))
         self.add_err('\nAdditional info:\ndecoded_data_string: [%s]\ndecoded_signature_string: [%s]' % ( decoded_data_string, decoded_signature_string))
         
         return None
*/
?>
