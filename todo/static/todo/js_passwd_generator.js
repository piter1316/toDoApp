function generate() {
  var output = document.getElementById('result').innerHTML = ''
  var chars = document.getElementById('chars').value
  var specials = document.getElementById('specials').checked
  var chars_int = parseInt(chars)
  var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  var special_characters = '!"#$%&()*+,-./:;=?@[\]^_`{|}~'
  var characters_with_special_characters = characters + special_characters
  var charactersLength = characters.length;
  characters_with_special_charactersLenght = characters_with_special_characters.length
  var passwd = ''



switch(specials){
  case false:
    for (var i=0; i<chars_int; i++){
      passwd += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    var output = document.getElementById('result').innerHTML = passwd
    break;
  case true:
    for (var i=0; i<chars_int; i++){
      passwd += characters_with_special_characters.charAt(Math.floor(Math.random() * characters_with_special_charactersLenght));
    }
    var output = document.getElementById('result').innerHTML = passwd
  break;
}

}
