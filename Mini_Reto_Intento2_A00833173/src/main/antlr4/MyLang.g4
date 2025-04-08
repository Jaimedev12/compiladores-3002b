// MyLang.g4
grammar MyLang;

prog: stat+ ;

stat: 'print' ID ';'               # printExpr
    | ID '=' expr ';'             # assignExpr
    ;

expr: expr op=('*'|'/') expr      # MulDiv
    | expr op=('+'|'-') expr      # AddSub
    | INT                         # intExpr
    | ID                          # idExpr
    | '(' expr ')'                # parensExpr
    ;

ID  : [a-zA-Z_][a-zA-Z_0-9]* ;
INT : [0-9]+ ;
WS  : [ \t\r\n]+ -> skip ;
