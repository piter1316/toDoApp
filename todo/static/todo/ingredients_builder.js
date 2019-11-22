function build(id) {
  var ingredient = document.getElementById('ingredient_'+id).value
  var quantity = document.getElementById('quantity_'+id).value
  var shop = document.getElementById('shop_'+id).value

  var to_add = ingredient + ' - ' + quantity + ' - ' + shop + '\n'
  var ingredients_ = document.getElementById('ingredients_'+id).value += to_add


}
