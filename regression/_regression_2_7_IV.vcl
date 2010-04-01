### 
### Regression tests for Vocola 2.7, part IV
### 


## 
## Test runtime errors:
## 

test Eval   bad conversion = EvalTemplate(%i, bar);
test Repeat bad conversion = Repeat(foo, bar);
test Dragon bad conversion = Wait("foo'bar");


(test=x) (Python=2) (bindings=3) = Eval($3 * $1 plus $2);

test bad Dragon = Wait(-1);

try Unimacro unavailable = Unimacro(x);



$set MaximumCommands 2;

  #try "test Dragon bad conversion continue":
continue = "Didn't stop!";



## 
## Test reported error location:
## 

what line is this = Eval(0/0);

what
about
this
line 
=
Eval(0/0)
;  # this line number is reported

include ".\.\regression_2_7_IV_ugly'name.vch";
