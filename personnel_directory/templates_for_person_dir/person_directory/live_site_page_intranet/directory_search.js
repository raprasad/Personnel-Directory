//var directory_search_url = 'http://127.0.0.1:8000/mcb/pd/intranet-search-form-ajax/?jsoncallback=?';
var directory_search_url = 'http://webapps.sciences.fas.harvard.edu/mcb/pd/intranet-search-form-ajax/?jsoncallback=?';
//var directory_search_url = 'http://webapps.sciences.fas.harvard.edu/mcb/pd/search-form-ajax/?jsoncallback=?';
//var directory_search_url = 'http://140.247.108.24:8000/mcb/pd/search-form-ajax/?jsoncallback=?';


function submit_directory_search_form(frm_data_str){
           
      // Retrieve the form object
      var frm_obj = $("#id_mcb_directory_form");

      if (!frm_data_str) {
          frm_data_str = frm_obj.serialize();       // use data from the full form
      }else{
          frm_data_str += '&id_mcb_personnel_dir=-1'    // used data from a link
      }

      // Submit the form via ajax
      $.getJSON(directory_search_url, frm_data_str,  function(data) {  
            
            if (data.success== false){
                alert(data.msg);
                 $("#directory_search_div").html(data.msg);
            }else{
            
                // Take result page (could be success or fail) and show it in the div
                $("#directory_search_div").html(data.page_str);
            
                // Change class of "psrch_search_again" items
                $('a.psrch_search_again').each(function(){
                    $(this).addClass("psrch_lnk");
                });
            
                // Bind search again links to reload new form
                $('a.psrch_search_again').click(function(){
                    //load_search_form();
                    this.href = window.location.pathname;
                
                });

                // mark mail lnks in the results table, if the table exists
                if($('#psrch_results_table').length!=0){
                    mark_mail_links();
                    bind_lab_office_links();
                }
            
                // bind a blank search form, if it exists
                if($('#id_mcb_directory_form').length!=0){
                    binds_for_newly_loaded_form();
                }
            }
        });  
       return false;
     
 }
 

function bind_lab_office_links(){
    //alert('bind_lab_office_links');
    $('a.psrch_resubmit').click(function(){
      	var srch_arg = this.rel;
      	submit_directory_search_form(srch_arg);
    });
}

function mark_mail_links(){
    $('span.psrch_mlink').each(function(){
    	var email_str = $(this).html();
    //	var lnk_str = '<a href="mailto:' + email_str + '" class="psrch_lnk" title="send email">' + email_str.replace('@', ' (at) ') + "</a>";
	    var lnk_str = '<a href="mailto:' + email_str + '" class="psrch_lnk" title="send email">email</a>';
        
        $(this).html(lnk_str);
    });    
}

function load_search_form(){
    $.getJSON(directory_search_url, {}, function(data) {
                 // (1) load the form 
                 if (data.success== false){
                    alert(data.msg);
                     $("#directory_search_div").html(data.msg);
                 }else{
                     $("#directory_search_div").html(data.page_str);

                     // (2) bind to the form's submit button 
                     binds_for_newly_loaded_form();
                }
          });    
}

function binds_for_newly_loaded_form(){
     // bind the submit button
    $('#id_mcb_directory_form').live('submit', function() {
          submit_directory_search_form();
          return false;               
    });
    
    // submit the form as soon as an dropdown box item has been selected
    $('select.cbox').change(function(){
        if ($(this).val()==-1){ return; };
        submit_directory_search_form();
    });
    
    
}


function getUrlVars(){
    // used for looking up a url for single person
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}



