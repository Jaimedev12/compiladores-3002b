grammar Arithmetic;

prog:   expr+ ;

expr:   term ((PLUS | MINUS) term)* ;
term:   factor ((MUL | DIV) factor)* ;
factor: INT | '(' expr ')' ;

PLUS:   '+' ;
MINUS:  '-' ;
MUL:    '*' ;
DIV:    '/' ;
INT:    [0-9]+ ;

WS:     [ \t\r\n]+ -> skip ;
