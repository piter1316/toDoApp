function build(id) {
  var ingredient = document.getElementById('ingredient_'+id).value
  var quantity = document.getElementById('quantity_'+id).value
  var unit = document.getElementById('unit_'+id).value
  var shop = document.getElementById('shop_'+id).value

  var to_add = ingredient + ' - ' + quantity + ' - ' + unit + ' - ' + shop + '\n'
  var ingredients_ = document.getElementById('ingredients_'+id).value += to_add

  document.getElementById('ingredient_'+id).value = ''
  document.getElementById('quantity_'+id).value = 1
  document.getElementById('shop_'+id).value = ''

}

function printShoppingList(shop_id){
  console.log(shop_id);
  var sTable = document.getElementById('shop_'+shop_id).innerHTML;
  shop = document.getElementById('shop_'+shop_id).getElementsByTagName("input")[0].value

  var style = "<style>";
  style = style + "input, button, select {display: none}";
  style = style + "#shopping_list_settings_"+shop_id+" {display: none}";
  style = style + "#addProdForm_"+shop_id+" {display: none}";
  style = style + ".todo-completed {display: none}";
  style = style + "a {text-decoration: none; color: black}";
  style = style + ".shop_name {text-decoration: underline}";
  style = style + "li {list-style-type: circle;}";
  style = style + "</style>";

  var win = window.open('', '', 'height=1280,width=768');

  win.document.write('<html><head>');
  win.document.write('<br>');
  win.document.write('<title>Lista zakupów</title>');
  win.document.write(style);
  win.document.write('</head>');
  win.document.write('<body>');
  win.document.write('<span class="shop_name">' + shop + '</span>');
  win.document.write(sTable);
  win.document.write('</body></html>');

  win.document.close();
  win.print();
}

function printAllShoppingLists(){
  var sTable = document.getElementsByClassName('shoppingList');

  var style = "<style>";
  style = style + "input, button, select {display: none}";
  style = style + ".addProdForm {display: none}";
  style = style + ".todo-completed {display: none}";
  style = style + "a {text-decoration: none; color: black}";
  style = style + "ul {float: left; padding: 30px}";
  style = style + "li {list-style-type: circle;}";
  style = style + ".shop_name {list-style-type: none; text-decoration: underline}";
  style = style + "</style>";

  var win = window.open('', '', 'height=1280,width=768');

  win.document.write('<html><head>');
  win.document.write('<br>');
  win.document.write('<title>Listy zakupów</title>');
  win.document.write(style);
  win.document.write('</head>');
  win.document.write('<body>');
  for(var i=0;i<sTable.length;i++){
    shop = sTable[i].getElementsByTagName("input")[0].value
    win.document.write('<ul>');
    win.document.write('<li class="shop_name">' + shop + '</li>');
    win.document.write(sTable[i].innerHTML);
    win.document.write('</ul>');
  }

  win.document.write('</body></html>');
  win.document.close();
  win.print();
}

function openNav() {
  document.getElementById("mySidenav").style.width = "100%";
  document.getElementById("mySidenav").style.height = "auto";
  document.getElementById("mySidenav").style.padding = "5%";
  $('#mySidenav #menu_ul').css('display','block')
   $('#closeMenu').show();
}

/* Set the width of the side navigation to 0 */
function closeNav() {
  document.getElementById("mySidenav").style.padding = "0";
  $('#closeMenu').hide('slow');
  setTimeout(function(){

    $('#mySidenav #menu_ul').css('display','none')
    setTimeout(function(){
      document.getElementById("mySidenav").style.height = "0";
     }, 500);
  }, 200);


}