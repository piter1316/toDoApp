$(document).ready(function(){
var max_days = $('#howManyDays').attr('max')
$('#howManyDays').attr({
       "max" : parseInt(max_days)*2})
  $('input[name=twice_the_same_meal]').change(function(){
    if($(this).is(':checked')) {

        console.log('ch'+ max_days)
        $('#howManyDays').attr({
       "max" : parseInt(max_days)*2})
    } else {
       $('#howManyDays').attr({
       "max" : parseInt(max_days)})
        console.log('un_ch'+parseInt(max_days) )
    }
});
});