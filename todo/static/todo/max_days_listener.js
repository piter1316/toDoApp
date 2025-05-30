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
      var day_short = $('#meals_list .text-center:last span b').text().split(' | ')[0];
      var date_short = $('#meals_list .text-center:last span b').text().split('|')[1].split(':')[0].trim();
      var parsed_date = new Date(date_short)
      parsed_date.setDate(parsed_date.getDate() + 1)
      var year = parsed_date.getFullYear()
      var month = parsed_date.getMonth()
      month +=1
      if (month <= 9)
        month = '0'+ String(month)
      var day = parsed_date.getDate()
      if (day <= 9)
        day = '0'+ String(day)
      var proper_date = String(year) + '-' + String(month) + '-' + String(day)
      var current_options = new Array()
      $('#first_day').attr('readonly', true);
       $("#first_day option").each(function() {
        current_options.push(this.value);
    });

    switch(day_short){
    case 'PN':
      var to_append = $('<option>',{value: '2|'+ proper_date, text : "WTOREK "+ " | "+ proper_date})
      if(current_options.includes(to_append.val())){
        $('#first_day').val('2|'+ proper_date);
      }
      else{
        $('#first_day').append(to_append);
        $('#first_day').val('2|'+ proper_date);
      }
      break;

    case 'WT':
      var to_append = $('<option>',{value: '3|'+ proper_date, text : "ŚRODA "+ " | "+ proper_date})
      if(current_options.includes(to_append.val())){
        $('#first_day').val('3|'+ proper_date);
      }
      else{
        $('#first_day').append(to_append);
        $('#first_day').val('3|'+ proper_date);
      }
      break;

    case 'ŚR':
      var to_append = $('<option>',{value: '4|'+ proper_date, text : "CZWARTEK "+ " | "+ proper_date})
      if(current_options.includes(to_append.val())){
      $('#first_day').val('4|'+ proper_date);
      }
      else{
        $('#first_day').append(to_append);
        $('#first_day').val('4|'+ proper_date);
      }
      break;

    case 'CZW':
      var to_append = $('<option>',{value: '5|'+ proper_date, text : "PIĄTEK "+ " | "+ proper_date})
      if(current_options.includes(to_append.val())){
        $('#first_day').val('5|'+ proper_date);
      }
      else{
        $('#first_day').append(to_append);
        $('#first_day').val('5|'+ proper_date);
      }
      break;

    case 'PT':
      var to_append = $('<option>',{value: '6|'+ proper_date, text : "SOBOTA "+ " | "+ proper_date})
      if(current_options.includes(to_append.val())){
        $('#first_day').val('6|'+ proper_date);
      }
      else{
        $('#first_day').append(to_append);
        $('#first_day').val('6|'+ proper_date);
      }
      break;

    case 'SB':
      var to_append = $('<option>',{value: '7|'+ proper_date, text : "NIEDZIELA "+ " | "+ proper_date})
      if(current_options.includes(to_append.val())){
        $('#first_day').val('7|'+ proper_date);
      }
      else{
        $('#first_day').append(to_append);
        $('#first_day').val('7|'+ proper_date);
      }
      break;

    case 'ND':
      var to_append = $('<option>',{value: '1|'+ proper_date, text : "PONIEDZIAŁEK "+ " | "+ proper_date})
      if(current_options.includes(to_append.val())){
        $('#first_day').val('1|'+ proper_date);
      }
      else{
        $('#first_day').append(to_append);
        $('#first_day').val('1|'+ proper_date);
      }
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
    if($('#li_' + num_id).hasClass('default')){
      $('#li_' + num_id).removeClass('default')
      $('#li_' + num_id).addClass('bg-secondary text-light')
    } else{
      $('#li_' + num_id).removeClass('bg-secondary text-light')
      $('#li_' + num_id).addClass('default')
    }

  })

  $('body').on('click', '.editExtras', function(e){
      var id = e.target.id
      var num_id = id.split('_')[1]
      var group = $('input[name="meals_list_position"]');
      group.each(function () {
              $(this).attr("value", num_id);
         });
      var form_group = $('form[name="editExtras"]');
      form_group.each(function () {
              $(this).attr("id", 'toUpdateExtras_' + num_id);
         });

//      var select_group = $('select[name="extras_select"]');
//      select_group.each(function () {
//              $(this).attr("id", 'extrasSelect_' + num_id);
//         });
      var modal_group = $('.extrasModal');
      modal_group.each(function () {
              $(this).attr("id", 'extrasModal_' + num_id);
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
    $('#meal_copy_div').toggle(600);
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

  var v_pills = $('#v-pills-tab a');
  v_pills_array = []
  v_pills.each(function(a){v_pills_array.push($(this).attr('href'))})

  v_pills_array.forEach(function(element, index,v_pills_array){
    if(window.location.href.includes(element)){
      $(element+'-tab').addClass('active')
      $(element).addClass('show active')
    }
    else if (window.location.href.includes('#')){
      $(element+'-tab').removeClass('active')
      $(element).removeClass('active')
      $(element).removeClass('show')
    }
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


setInterval(function(){
  var time_now_smalls = $('.time_now_')
  var time_now = $(time_now_smalls[0]).text().split(' ')
  var current_date_time = new Date()
  var current_time = current_date_time.toTimeString().substring(0,5)
  if (current_time != time_now[3]){
    time_now.pop()
    time_now.push(current_time)
    $('.time_now_').replaceWith("<small class='w-100 text-left time_now_ mb-1 font-italic font-weight-light'>"+time_now.join(' ')+"</small>");
  }
}, 1000);

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


$('body').on('click','.toDoButtonAdd',function(e){
  var id_num = $(this).attr('id').split('_')[1]
  if($('#toDo_'+id_num).is(":visible")){
    $('#toDo_'+id_num).hide('slow');
    $(this).html('<i class="fas fa-plus"></i>')
  }else{
    $('#toDo_'+id_num).show('slow');
    $(this).html('<i class="fas fa-minus"></i>')
    $('#addStep_'+id_num).focus()
  }
});

$('body').on('click','#v-pills-tab a',function(e){
  var id_num = $(this).attr('id').split('-')[2]
  var tab_panes = $('.tab-pane')
  for(var i=0; i<tab_panes.length; i++){
  tab_panes[i].classList.remove("show");
  tab_panes[i].classList.remove("active");
  }
});


$('body').on('change','input[name=only_hi_protein_in_select]',function(){
  var select = $("select[name='to_update']");
  var options = select.find("option");
  var extrasSelect = $("select[name='extras_select']");
  var extrasOptions = extrasSelect.find("option");
  if ($(this).is(':checked')) {
    options.each(function() {
      var optionText = $(this).text();
      if (!(optionText.includes("| B") || optionText.includes("| b"))) {
        $(this).hide();
      }
    });
    extrasOptions.each(function() {
      var optionText = $(this).text();
      if (!(optionText.includes("| B") || optionText.includes("| b"))) {
        $(this).hide();
      }
    });
    } else {
  options.show();
  extrasOptions.show();
  }
})
function refreshOnMealChange(form_id, thToRefresh, checkbox, data){
  $('#modalTitleSpan_' + form_id).replaceWith($('#modalTitleSpan_' + form_id, data));
  $('#dropdownMeal_'+form_id).replaceWith($('#dropdownMeal_' + form_id,data));
  $('#dropdownMenu_'+form_id).removeClass('show');
  $('#span_'+form_id).replaceWith($('#span_' + form_id,data));
  $('#b-t-w').replaceWith($('#b-t-w',data));
  $('#mobileAverageContainer').replaceWith($('#mobileAverageContainer',data));
  $('#tr_'+form_id).replaceWith($('#tr_'+form_id,data));
  $('#editExtrasSmall_'+form_id).replaceWith($('#editExtrasSmall_'+form_id,data));
  $('#' + thToRefresh.id).replaceWith($('#' + thToRefresh.id, data));
  var tdToRefresh = thToRefresh.id.replace('th', 'td')
  var trToRefresh = thToRefresh.id.replace('th', 'tr').replace('div_', '')
  $('#' + trToRefresh).replaceWith($('#' + trToRefresh,data));
  $('#' + trToRefresh).replaceWith($('#' + trToRefresh,data));
  $('#editExtras_' + form_id).replaceWith($('#editExtras_' + form_id,data));
  $(checkbox).fadeOut();
  $(checkbox).prop('checked', true);

}

function refreshModal(form_id, opt_id, data){
$('#extrasSelect_'+ opt_id).val($('#extrasSelect_'+ opt_id + ' option:first').val());
$('#dismiss_extras_modal').click();
if ($('#editExtrasSmall_' + form_id).length) {
        ;
    } else {
        $('#td_' + form_id).append($('#editExtrasSmallWrap_' + form_id,data));
    }


}

$('body').on('change','select[name="to_update"]',function(e){
    e.preventDefault();
    var id = e.target.id
    var form_id = id.split('_')[1]
    var newMealOptionId = $('#form_'+ form_id + ' #toUpdate_' + form_id).val();
    var newMealOptionText = $('#toUpdate_' + form_id + ' option[value="' + newMealOptionId +'"]').text();
    if(newMealOptionText.includes('|')){
      var newMealOptionName = newMealOptionText.split('|')[0]
    } else{
      var newMealOptionName = '------'
    }
    $('#dropdownMeal_'+form_id).text(newMealOptionName);
    var rows = $('input[name=day]');
    for (let i = 0; i < rows.length; i++) {
      var row = rows[i]
      if (row.value.includes(form_id)){
        var thToRefresh = row.parentNode
        var checkboxCheck = $(row);
        if($(checkboxCheck).is(':checked')){
        var checkbox = row;
        }
        }
    }

    $.ajax({
      type:'POST',
      url:'/mealsList/1/update',
      data:{
        record_id:$('#form_'+ form_id + ' input[name="record_id"]').val(),
        to_update:$('#form_'+ form_id + ' #toUpdate_' + form_id).val(),
        csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
      },
      success: function(data){
        refreshOnMealChange(form_id, thToRefresh, checkbox, data)
      }
    });
  });

  $('body').on('change','select[name="extras_select"]',function(e){
    e.preventDefault();
    var form_id = $('input[name="meals_list_position"]').val()
    var _id = e.target.id
    var opt_id = _id.split('_')[1]
    var newMealOptionId = $('#form_'+ form_id + ' #toUpdate_' + form_id).val();
    var newMealOptionText = $('#toUpdateExtras_' + form_id + ' option[value="' + newMealOptionId +'"]').text();
    if(newMealOptionText.includes('|')){
      var newMealOptionName = newMealOptionText.split('|')[0]
    } else{
      var newMealOptionName = '------'
    }
    $('#dropdownMeal_'+form_id).text(newMealOptionName);
    var rows = $('input[name=day]');
    for (let i = 0; i < rows.length; i++) {
      var row = rows[i]
      if (row.value.includes(form_id)){
        var thToRefresh = row.parentNode
        var checkboxCheck = $(row);
        if($(checkboxCheck).is(':checked')){
        var checkbox = row;
        }
        }
    }
    var option = $('#option_id').val();
    console.log(option)
    $.ajax({
      type:'POST',
      url:'/mealsList/1/edit_extras/',
      data:{
        meals_list_position:$('#toUpdateExtras_'+ form_id + ' input[name="meals_list_position"]').val(),
        extras_select:$('#extrasSelect_'+ opt_id).val(),
        csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()
      },

      success: function(data){
        refreshOnMealChange(form_id, thToRefresh, checkbox, data)
        refreshModal(form_id, opt_id, data)
      }
    });
  });

  $('body').on('click','#delete_extras',function(e){
    e.preventDefault();
    var form_id = $('input[name="meals_list_position"]').val()
    var _id = e.target.id
    var opt_id = _id.split('_')[1]
    var newMealOptionId = $('#form_'+ form_id + ' #toUpdate_' + form_id).val();
    var newMealOptionText = $('#toUpdateExtras_' + form_id + ' option[value="' + newMealOptionId +'"]').text();
    if(newMealOptionText.includes('|')){
      var newMealOptionName = newMealOptionText.split('|')[0]
    } else{
      var newMealOptionName = '------'
    }
    $('#dropdownMeal_'+form_id).text(newMealOptionName);
    var rows = $('input[name=day]');
    for (let i = 0; i < rows.length; i++) {
      var row = rows[i]
      if (row.value.includes(form_id)){
        var thToRefresh = row.parentNode
        var checkboxCheck = $(row);
        if($(checkboxCheck).is(':checked')){
        var checkbox = row;
        }
        }
    }
    var option = $('#option_id').val();
    $.ajax({
      type:'GET',
      url:e.target.href,
      data:{},

      success: function(data){
        refreshOnMealChange(form_id, thToRefresh, checkbox, data)
        refreshModal(form_id, opt_id, data)
      }
    });
  });


