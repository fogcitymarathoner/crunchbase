/**
 * Created by marc on 6/1/2015.
 */
$( document ).ready(function() {
    console.log( "ready!" );
    $('input[name="reset_btn"]').click(function( event ) {
        event.preventDefault();
        $('input[name="q"]').val(null);
        $(location).attr('href',"/crunchbase_search");
    });

});