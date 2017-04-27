window.onload = function init() {
  var options = {
    valueNames: [
      { data: ['distinct'] },
      'name',
      'package',
      'repo' 
    ] 
  };
  var userList = new List('deps', options);
}
