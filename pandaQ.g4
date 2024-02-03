grammar pandaQ;


root : (statement ';')*;

statement: query | assign | plot; 

query   : SELECT columns FROM table (inner)? (where)? (order)?    #queryN
	;


plot    : PLOT ID;
assign  : ID ':=' query;



columns : '*' | column (',' column)*;
column  : expr (AS ID)?; 

table   : ID;


inner   : (innerJoin)+;
innerJoin: INNER JOIN table ON innercond;
innercond: ID '=' ID;


order	: ORDER BY camps;
camps	: camp (',' camp )*;
camp 	: ID  ( ASC | DESC)?;


where   : WHERE (conditions | subquery);

conditions: condition ('and' condition)*;
condition: '(' condition ')' 		      		      #paren
	| NOT condition				      #not
	| ID COND INT					      #cond
	;


subquery: ID IN '(' query ')';


COND   : AND | MENOR | MAYOR | IGUAL;
NOT    : 'NOT' | 'not';
AND    : 'AND' | 'and';
MENOR  : '<';
MAYOR  : '>';
IGUAL  : '=';




expr : '(' expr ')' 		    # exparent
     | <assoc=right> expr '^' expr #exp
     | expr ('*' | '/') expr    # mult
     | expr ('+' | '-') expr    # suma
     | flotant			 # exprflot
     | ID			  # id
     ;

flotant: INT '.' (INT)*
	| INT
	;



SELECT : 'SELECT' | 'select' ;
FROM   : 'FROM' | 'from' ;
AS     : 'AS' | 'as';
ASC    : 'ASC' | 'asc';
DESC   : 'DESC' | 'desc' ;
ORDER  : 'ORDER' | 'order';
BY     : 'BY' | 'by';
WHERE  : 'WHERE' | 'where';
INNER  : 'INNER' | 'inner';
JOIN   : 'JOIN' | 'join';
ON     : 'ON' | 'on';
PLOT   : 'PLOT' | 'plot';
IN     : 'IN' | 'in';

// Define tokens
ID      : [a-zA-Z_][a-zA-Z0-9_]*; // Id
INT     : [0-9]+;                // Int
WS      : [ \t\r\n]+ -> skip;    // Whitespace
