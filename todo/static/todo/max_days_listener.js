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
    var max_days_no_repeat = $('#maximum_no_of_days_to_generate_no_repeat').val()
    console.log(max_days_no_repeat)
    $('input[name=no_repetition]').change(function(){
      if($(this).is(':checked')) {
          $('#howManyDays').attr({
         "max" : max_days_no_repeat})
      } else {
         $('#howManyDays').attr({
         "max" : parseInt(max_days)})
      }
    });

    $('input[name=append_existing]').change(function(){
      if($(this).is(':checked')) {
        var allOptions = $('.mealsOptions')
        allOptionsArray = []
        generatedOptionsArray = []
        $('.generated_meal_options').each(function( index ) {
          generatedOptionsArray.push($( this ).val() );
        });
        $('.mealsOptions').each(function( index ) {
          allOptionsArray.push($( this ) );
          console.log($(this).val())
          if(!(generatedOptionsArray.includes($(this).val()))){
            $(this).prop('checked',false)
          }
        });
        setTimeout(function(){$('#meal_options_form, #meal_options_form_hr').hide(600)}, 200);

        var day_short = $('#meals_list tr:last th').text().trim()
        $('#first_day').attr('readonly', true);
        switch(day_short){
        case 'PN':
          $('#first_day').val(1);
          break;
        case 'WT':
          $('#first_day').val(2);
          break;
        case 'ŚR':
          $('#first_day').val(3);
          break;
        case 'CZW':
          $('#first_day').val(4);
          break;
        case 'PT':
          $('#first_day').val(5);
          break;
        case 'SB':
          $('#first_day').val(6);
          break;
        case 'ND':
          $('#first_day').val(0);
          break;
        }
      } else {
         $('#meal_options_form, #meal_options_form_hr').show(600)
         $('.mealsOptions').each(function( index ) {
              $(this).prop('checked',true)
          });
          $('#first_day').attr('readonly', false);
      }
  });

  $('.dropdown-menu').click(function(e){
    e.stopPropagation();
  })

  $('#new_ingredient_form_toggle').click(function(e){
    if ($(this).text() == "Nowy Składnik") {
          $(this).text("Zamknij formularz");
      } else {
          $(this).text("Nowy Składnik");
      };
    $('#new_ingredient_form').toggle(600);
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