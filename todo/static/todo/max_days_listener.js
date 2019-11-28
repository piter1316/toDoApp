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

  $('.dropdown-menu').click(function(e){
    e.stopPropagation();
  })

  $('.meal_option_settings').on('click', function(e){
      var id = $(e.target).closest('li').attr('id')
      var settings_id = id.split('_')
      var s_id = parseInt(settings_id[1])
      $('#settings_'+(s_id)).toggleClass('d-none');
   });

});