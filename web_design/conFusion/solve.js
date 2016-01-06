var quad = require('./quadratic')
quad(4,2,2,function(err,quadsolve){
  if(err){console.log('Error: ', err);}
  else {console.log("Roots are" + quadsolve.root1() + " " | quadsolve.root2());}
});