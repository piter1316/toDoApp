function createPDF() {
  var sTable = document.getElementById('meals_list').innerHTML;
//  var sTable = document.getElementById('meals_list_head').innerHTML;

  var style = "<style>";
  style = style + "table {width: 100%;font: 17px Calibri;}";
  style = style + ".dropdown-menu {display: none}";
  style = style + ".no_print {display: none}";
  style = style + "input {display: none}";
  style = style + ".text-left {text-align: left;}";
  style = style + "table, th, td {border: solid 1px #111; border-collapse: collapse;";
  style = style + "padding: 2px 3px;text-align: center;}";


  style = style + "</style>";

  // CREATE A WINDOW OBJECT.
  var win = window.open('', '', 'height=1280,width=768');

  win.document.write('<html><head>');
  win.document.write('<br>');
  win.document.write('<title>Profile</title>');   // <title> FOR PDF HEADER.
  win.document.write(style);          // ADD STYLE INSIDE THE HEAD TAG.
  win.document.write('</head>');
  win.document.write('<body>');
  win.document.write(sTable);         // THE TABLE CONTENTS INSIDE THE BODY TAG.
  win.document.write('</body></html>');

  win.document.close(); 	// CLOSE THE CURRENT WINDOW.

  win.print();    // PRINT THE CONTENTS.
}

function createPDFRecipe() {

var style = "<style>";
  style = style + "p {text-align:center;}";
  style = style + "#ingr {list-style-type:none;}";
  style = style + "form {dispaly: none;}";
    style = style + ".no_print {display: none}";


  style = style + "</style>";

var name = document.getElementById('option_name').innerHTML;
var list = document.getElementById('ingredients_list').innerHTML;
var recipe = document.getElementById('update_recipe_textarea').value;

var win = window.open('', '', 'height=1280,width=768');

  win.document.write('<html><head>');
  win.document.write('<br>');
  win.document.write('<title>Profile</title>');   // <title> FOR PDF HEADER.
  win.document.write(style);          // ADD STYLE INSIDE THE HEAD TAG.
  win.document.write('</head>');
  win.document.write('<body>');
  win.document.write(name);         // THE TABLE CONTENTS INSIDE THE BODY TAG.
  win.document.write('<hr>');         // THE TABLE CONTENTS INSIDE THE BODY TAG.
  win.document.write(list);         // THE TABLE CONTENTS INSIDE THE BODY TAG.
  win.document.write('<hr>');
  win.document.write(recipe);         // THE TABLE CONTENTS INSIDE THE BODY TAG.
  win.document.write('</body></html>');

  win.document.close(); 	// CLOSE THE CURRENT WINDOW.

  win.print();    // PRINT THE CONTENTS
}