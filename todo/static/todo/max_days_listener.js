$(document).ready(function(){
  var max_days = $('#howManyDays').attr('max')
  $('#howManyDays').attr({
         "max" : parseInt(max_days)*2})
    $('input[name=twice_the_same_meal]').change(function(){
      if($(this).is(':checked')) {
          $('#howManyDays').attr({
         "max" : parseInt(max_days)*2})
      } else {
         $('#howManyDays').attr({
         "max" : parseInt(max_days)})
      }
  });

    $('input[name=append_existing]').change(function(){
      if($(this).is(':checked')) {
          console.log('ch')
          $('#meal_options_form, #meal_options_form_hr').hide(600)
      } else {
         $('#meal_options_form, #meal_options_form_hr').show(600)
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

  $('#allow_update_recipe').on('click', function(e){
    $('#allow_update_recipe').hide('slow');
    $('#update_recipe_textarea').removeAttr('readonly');
    var rows = $('#update_recipe_textarea').attr('rows');
    console.log(rows)
    if(rows >= 1 && rows < 5){
      $('#update_recipe_textarea').attr('rows', 5);
    }else{
      rows = parseInt(rows)
      $('#update_recipe_textarea').attr('rows', rows+=1);
    }
    $('#update_recipe_textarea').focus();
    $('#update_recipe').toggleClass('d-none');
   });

  $('#option_name').on('click', function(e){
    $('#new_meal_option_name').toggleClass('d-none');
  });

});