$(document).ready(function(){
  var max_days = $('#maximum_no_of_days_to_generate').val()
  var max_days_no_repeat = $('#maximum_no_of_days_to_generate_no_repeat').val()
  var max_days_default = $('#maximum_no_of_days_to_generate_default').val()

  if(parseInt(max_days_no_repeat) == 0 || parseInt(max_days_no_repeat)==max_days ){
    $('#howManyDays').attr({"max": parseInt(max_days_default)})
  }else{
    $('#howManyDays').attr({"max": parseInt(max_days_no_repeat)*2})
  }
  $('input[name=twice_the_same_meal]').change(function(){
    if($(this).is(':checked')) {
      if ($('input[name=no_repetition]').is(':checked')){
        $('#howManyDays').attr({"max" : parseInt(max_days_no_repeat)*2})
      }else{
        $('#howManyDays').attr({"max" : parseInt(max_days)*2})
      }
    }else{
      if ($('input[name=no_repetition]').is(':checked')){
        $('#howManyDays').attr({"max" : parseInt(max_days_no_repeat)})
      }else{
        $('#howManyDays').attr({"max" : parseInt(max_days)})
      }
    }
  });

  $('input[name=no_repetition]').change(function(){
    if($(this).is(':checked')) {
      if ($('input[name=twice_the_same_meal]').is(':checked')){
        $('#howManyDays').attr({"max" : parseInt(max_days_no_repeat)*2})
      }else{
        $('#howManyDays').attr({"max" : parseInt(max_days_no_repeat)})
      }
    }else{
      if ($('input[name=twice_the_same_meal]').is(':checked')){
        $('#howManyDays').attr({"max" : parseInt(max_days)*2})
      }else{
        $('#howManyDays').attr({"max" : parseInt(max_days)})
      }
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
        if(!(generatedOptionsArray.includes($(this).val()))){
          $(this).prop('checked',false)
        }
      });
      setTimeout(function(){$('#meal_options_form, #meal_options_form_hr').hide(600)}, 200);
      var day_short = $('#meals_list .text-center:last span b').text().split(' ')[0];
      $('#first_day').attr('readonly', true);

      switch(day_short){
      case 'PN':
        $('#first_day').val(2);
        break;
      case 'WT':
        $('#first_day').val(3);
        break;
      case 'ŚR':
        $('#first_day').val(4);
        break;
      case 'CZW':
        $('#first_day').val(5);
        break;
      case 'PT':
        $('#first_day').val(6);
        break;
      case 'SB':
        $('#first_day').val(7);
        break;
      case 'ND':
        $('#first_day').val(1);
        break;
      }
    }else {
      $('#meal_options_form, #meal_options_form_hr').show(600)
      $('.mealsOptions').each(function( index ) {
      $(this).prop('checked',true)
      });
      $('#first_day').attr('readonly', false);
    }
  });

  $('.stopPropagation').click(function(e){
    e.stopPropagation();
  })

  $('.dropdownMeal').click(function(e){
    var dropdown_div_id = 'dropdownMenu_' + $(this).attr('id').split('_')[1]
    $('#'+dropdown_div_id).toggle()
  })

  $('.dropdownMeal').click(function(e){
    var id = e.target.id
    var num_id = id.split('_')[1]

    $('#dropdownMealContent_' + num_id).toggle(600);
  })

  $('body').on('click', '.dropdownMenuButton_', function(e){
    var id = e.target.id
    var num_id = id.split('_')[1]
    $('#update_ingredient_' + num_id).toggle(600);
  })

  $('body').on('click', '.editExtras', function(e){
      var id = e.target.id
      var num_id = id.split('_')[1]
      var group = $('input[name="meals_list_position"]');
      group.each(function () {
              $(this).attr("value", num_id);
         });
      $('#extrasModalTitleSpan').text($('#clicked_position_meal_'+ num_id).val());
      var base_url = $('#base_delete_url').val()
      $('#delete_extras').attr('href', base_url + num_id)
      var current_extra = $('#clicked_position_extras_'+num_id).val();
      var current_extra_kcal = $('#extras_calories_' + num_id).val();
      if (current_extra && current_extra_kcal){
        $('#current_extras').text(current_extra + ' | ' + current_extra_kcal + 'kcal' )
        var extras_link = $('#extras_link_'+ num_id).val()
        $('#current_extras').attr('href', extras_link)
        $('#delete_extras').text('Usuń' + ' ' + current_extra);
        $('#delete_extras').fadeIn('fast');
        $('#current_extra_small').fadeIn('fast');
        $('#current_change_div').fadeIn('fast');
        $('#add_extras_span').fadeOut('fast');
      }

    })

    $('#extrasModal').on('hidden.bs.modal', function () {
      var base_url = $('#base_delete_url').val()
      $('#delete_extras').attr('href', base_url);
      $('#current_extras').text('')
      $('#current_extras').attr('href','')
      $('#delete_extras').fadeOut('fast');
      $('#current_change_div').fadeOut('fast');
      $('#current_extra_small').fadeOut('fast');
      $('#add_extras_span').fadeIn('fast');

    })

    $('.shoppingListSettingsButton').click(function(e){
    var id = e.target.id;
    var num_id = id.split('_')[1]
      $('#shopping_list_settings_'+num_id).toggle(600);
    })

  $('#new_ingredient_form_toggle').click(function(e){
    if ($(this).text().trim() == "Opcje") {
          $(this).text("Zamknij");
      } else {
          $(this).text("Opcje");
      };
    $('#new_ingredient_form').toggle(600);
  })

  $('.meal_option_settings').on('click', function(e){
      var id = $(e.target).closest('li').attr('id')
      var settings_id = id.split('_')
      var s_id = parseInt(settings_id[1])
      $('#settings_'+(s_id)).toggleClass('d-none');
   });

  $('body').on('click','#allow_update_recipe', function(e){
    $('#allow_update_recipe').hide('slow');
    $('#update_recipe_textarea').removeAttr('readonly');
    var rows = $('#update_recipe_textarea').attr('rows');
    if(rows >= 1 && rows < 5){
      $('#update_recipe_textarea').attr('rows', 5);
    }else{
      rows = parseInt(rows)
      $('#update_recipe_textarea').attr('rows', rows+=1);
    }
    $('#update_recipe_textarea').focus();
    $('#update_recipe').toggleClass('d-none');
   });

  $('body').on('click', '#option_name', function(e){
    $('#new_meal_option_name').toggle(600);
  });


  $('#add_invoice_button').on('click', function(e){
    $('#add_invoice').toggle(600);
  });

//  $('input[name=day]').change(function(){
  $('body').on('change','input[name=day]',function(){
    var atLeastOneIsChecked = $('input[name=day]').is(':checked');
    if(atLeastOneIsChecked){
      $('.deleteSelectedDaysButton').removeAttr("disabled");
    }else{
      $('.deleteSelectedDaysButton').attr("disabled","true")
    }

    var CheckedMealsListItemsArray = $(this).val().split(',')
    CheckedMealsListItemsArray.pop()
    if($(this).is(':checked')) {
      function check(element, index, array) {
        $('.mealsListPosition_'+element).prop('checked', true).prop('checked', true)
      }
      CheckedMealsListItemsArray.forEach(check);
    }else {
      function uncheck(element, index, array) {
          $('.mealsListPosition_'+element).prop('checked', false)
       }
       CheckedMealsListItemsArray.forEach(uncheck);
    }
  });

  $('#mealsOptionsButton').on('click', function(){
    if ($('#mealsOptionsButtonText').text() == "opcje") {
          $('#mealsOptionsButtonText').text('zamknij')
      } else {
        $('#mealsOptionsButtonText').text('opcje')
      };
  })

  $(function () {
    $('[data-toggle="tooltip"]').tooltip()
  })

 if(window.location.href.includes('#service')){
 $('#fuel').removeClass('show')
 $('#fuel').removeClass('active')
 $('#fuel-tab').removeClass('active')
 $('#service').addClass('show');
 $('#service').addClass('active');
 $('#service-tab').addClass('active');
 }

 if(window.location.href.includes('#division')){
 $('#macro').removeClass('show')
 $('#macro').removeClass('active')
 $('#macro-tab').removeClass('active')
 $('#division').addClass('show');
 $('#division').addClass('active');
 $('#division-tab').addClass('active');
 }

 if(window.location.href.includes('#info')){
 $('#fuel').removeClass('show')
 $('#fuel').removeClass('active')
 $('#fuel-tab').removeClass('active')
 $('#info').addClass('show');
 $('#info').addClass('active');
 $('#info-tab').addClass('active');
 }

 $(".divisionPriority_").keypress(function(e) {
    if (isNaN(String.fromCharCode(e.which))) e.preventDefault();
});

});

$('body').on('click','.dropdown_shopping_item',function(e){
  var id = e.target.id;
  var num_id = id.split('_')[1]

  $('#'+num_id).toggle(600);
  $('#badge_edit_'+num_id).toggle(600);
});

$('body').on('click','.crossChecked_',function(e){
  var id = e.target.id;
  var num_id = id.split('_')[1]
  $('#checkItemLabel_'+num_id).addClass('text-muted');
  $('#checkItemLabel_'+num_id).css('text-decoration', 'line-through');
//  $('#badge_edit_'+num_id).toggle(600);
});

$('body').on('click','.editToggleLg, .editToggle',function(e){
  var id = e.target.id;
  var num_id = id.split('_')[1]
  $('.serviceEditButton_' + num_id).toggle('slow')
  $('.invoiceEditButton_' + num_id).toggle('slow')
  $('.deleteServiceButton_' + num_id).toggle('slow')
});





$('body').on('change','input[name=bought_many]',function(e){
var id_num = $(this).attr('id').split('_')[1]
  var form_id = $(this).closest('div').find('.bought_checkbox_form').attr('id').split('_')[1]
  if($(this).is(':checked')) {
    $('#checked_'+id_num).prop('checked', true);
  } else {
    $('#checked_'+id_num).prop('checked', false);
  }
  var ul_id = $(this).closest('ul').attr('id')
  var atLeastOneIsChecked = $('#'+ul_id+' input:checkbox').is(':checked');
  var form_id = $(this).closest('div').find('.bought_checkbox_form').attr('id').split('_')[1]

  if(atLeastOneIsChecked){
    $('#boughtManyForm_'+ form_id).fadeIn()
  }else{
    $('#boughtManyForm_'+ form_id).fadeOut()
  }
});

