/*

This is a sample file that main.py tests

*/

let arr = [1, 2, 3];

function myFunction(x) {
  if(x == 3) {
    return x;
  }
  for (let i = 0; i < x; i++) {
    console.log(i);
  }
  return x + 1;
}

let userInput = prompt("Enter a value:");
print(myFunction(userInput));
