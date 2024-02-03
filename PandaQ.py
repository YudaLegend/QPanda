
from math import exp
from operator import truediv
from antlr4 import *
from exprsLexer import exprsLexer
from exprsParser import exprsParser
from exprsVisitor import exprsVisitor #Les classes de visitors son heredats del padre. Lo que fem es visitar el node.

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt



st.write("""# My first PANDAS """)

# Adding an input box
user_input = st.text_area("Enter your text here:")

# Adding a button
submit_button = st.button("Submit")


def remove_not_and_extract(info,neg=False):
    if isinstance(info, tuple):
        if info[0] == 'not':
            # Skip 'not' and process the rest of the tuple
            return remove_not_and_extract(info[1], not neg)
        else:
            # Process each element in the tuple
            result =  tuple(remove_not_and_extract(element, neg) for element in info[1:])

            return (info[0], *result), neg
    else:
        # Base case: return non-tuple elements as they are
        return info
    
def negateOperator(op):
    match op:
        case '<':
            return '>='
        case '>':
            return '<='
        case '=':
            return '!'
        case _:
            print ("No case")
        

class EvalVisitor(exprsVisitor):
    def __init__(self):
        self.ts = {}
        self.subqueries = []

    def visitRoot(self, ctx):
        [statement,_] = list(ctx.getChildren())

        (self.visit(statement))
            
    # Visit a parse tree produced by exprsParser#taula.
    def visitQueryN(self, ctx):
    
        l = list(ctx.getChildren())
        
        #FROM
        self.df = self.visit(l[3])
        

        #Parte para identificar si hay inner,where o order
        inner = False
        where = (False,0)
        order = (False,0)
        if (len(l) == 5):
            if ("inner" in l[4].getText()):    
                inner = True
            elif ("where" in l[4].getText()):
                where = (True,4)
            else:
                order = (True,4)

        elif (len(l) == 6):
            if ("inner" in l[4].getText()):    
                inner = True
            if ("where" in l[4].getText()):
                where = (True,4)
            if ("where" in l[5].getText()):
                where = (True,5)
            
            if ("order" in l[5].getText()):
                order = (True,5)
        
        elif (len(l) == 7):
            inner = True
            where = (True,5)
            order = (True,6)

        #INNER JOIN
        if (inner):
            info_inner = self.visit(l[4])

            #Para cada inner join
            for x in info_inner:
                tabla_inner = x[0]
                fst_col = x[1][0]
                snd_col = x[1][1]

                
                inner_data = pd.read_csv(tabla_inner + ".csv")

                self.df = pd.merge(self.df,inner_data, left_on=fst_col,right_on=snd_col,how='inner')
        
        #WHERE
        if (where[0]):
            if ("in" in l[where[1]].getText()):
                
                self.subqueries.append(self.df)

                info_i = self.visit(l[where[1]])
                i_camp = info_i[0]
                df2 = info_i[1]

                df1 = self.subqueries.pop()

                
                self.df = df1[df1[i_camp].isin(df2[i_camp])]

            else:
                listacond = self.visit(l[where[1]])

                for cond in listacond:
                    info = remove_not_and_extract(cond)

                    #Coger informacion de la condicion
                    info_col = info[0][0]
                    info_op = info[0][1]
                    info_value = int(info[0][2])

                    neg = info[1]
                    
                    if (neg):
                        info_op = negateOperator(info_op)
                    
                    match info_op:
                        case '<':
                            condition = self.df[info_col] < info_value
                            
                        case '>':
                            condition = self.df[info_col] > info_value
                            
                        case '=':
                            condition = self.df[info_col] == info_value
                            
                        case '!':
                            
                            condition = self.df[info_col] != info_value

                        case '<=':
                            condition = self.df[info_col] <= info_value

                        case '>=':
                            condition = self.df[info_col] >= info_value

                        case _:
                            print ("No case")
                    
                    self.df = self.df[condition]            


        #SELECT
        res = self.visit(l[1])

        if (res != 1):
            self.df = self.df[res]
        
        #ORDER
        if (order[0]):
            listac = self.visit(l[order[1]])
            sort_colums = [ seq[0] for seq in listac ]
            sort_order = [ seq[1] for seq in listac ] 
            self.df = self.df.sort_values(by=sort_colums,ascending=sort_order)

        

        st.dataframe(self.df)

        return self.df
        
    # Visit a parse tree produced by exprsParser#plot.
    def visitPlot(self, ctx):
        [_,id] = list(ctx.getChildren())
        key = id.getText()
        if key in st.session_state:
            chart_data = st.session_state[key]
            #Filtrar por numeros
            st.line_chart(data=chart_data.select_dtypes(include='number'), use_container_width=True)
            

    # Visit a parse tree produced by exprsParser#assign.
    def visitAssign(self, ctx):
        [id,_,query] = list(ctx.getChildren())
        key = id.getText()
        
        
        value = self.visit(query)
        st.session_state[key] = value 
    

    # Visit a parse tree produced by exprsParser#inner.
    def visitInner(self, ctx):
        listinner = list(ctx.getChildren())
        
        listai = []
        for x in listinner:
            listai.append(self.visit(x))
        return listai
    
    # Visit a parse tree produced by exprsParser#innerJoin.
    def visitInnerJoin(self, ctx):
        [_,_,table1,_,c] = list(ctx.getChildren())
        
        return (table1.getText(),self.visit(c))

    # Visit a parse tree produced by exprsParser#innercond.
    def visitInnercond(self, ctx):
        [camp1,op,camp2] = list(ctx.getChildren())
        return (camp1.getText(),camp2.getText())
    

    def visitColumns(self, ctx):
        columns = list(ctx.getChildren())
    
        if (len(columns) == 1 and columns[0].getText() == '*'):
             dataFrame = 1
             return dataFrame
        else:
            listaCol = []
            #Aqui tienes que coger la lista de columnas
            #ejemplo de "select c1,c2,c3 from t;"
            # hace un for x in [c1,c2,c3]
            for x in columns:
                if (x.getText() != ','):
                    listaCol.append(self.visit(x))
            return listaCol
                    
    def visitColumn(self, ctx):
        colum = list(ctx.getChildren())

        #caso de columna sin el "as"
        #Por lo tanto solo retornamos el dataFrame de
        if (len(colum) == 1):
            
            return colum[0].getText()
        else:
            #Caso cuando tenemos un col1 as col2, o col1 * 2 as col2
            #El primer valor es una expr, mirar la gramatica
            nuevoCol = colum[2].getText()
            self.nv = nuevoCol
            
            self.visit(colum[0])
            
            return nuevoCol

    # Visit a parse tree produced by exprsParser#exparent.
    def visitExparent(self, ctx:exprsParser.ExparentContext):
        [_,col,_] = list(ctx.getChildren())

        return self.visit(col)
    
    # Visit a parse tree produced by exprsParser#exp.
    def visitExp(self, ctx):
        [col,op,f] = list(ctx.getChildren())
        self.df[self.nv] = self.visit(col) ** self.visit(f)

    # Visit a parse tree produced by exprsParser#mult.
    def visitMult(self, ctx):
        [col,op,f] = list(ctx.getChildren())
        if (op.getText() == '*'):       
            aux = self.visit(col) * self.visit(f)
            self.df[self.nv] = aux
            return self.df[self.nv]
        else: 
            self.df[self.nv] = self.visit(col) / self.visit(f)
            return self.df[self.nv]
    # Visit a parse tree produced by exprsParser#suma.
    def visitSuma(self, ctx):
        [col,op,f] = list(ctx.getChildren())
        if (op.getText() == '+'):       
            aux = self.visit(col) + self.visit(f)
            self.df[self.nv] = aux
            return self.df[self.nv]
        else: 
            self.df[self.nv] = self.visit(col) - self.visit(f)
            return self.df[self.nv]
    # Visit a parse tree produced by exprsParser#id.
    def visitId(self, ctx):
        [col] = list(ctx.getChildren())
        self.df[self.nv] = self.df[col.getText()]

        return self.df[self.nv]
    
    # Visit a parse tree produced by exprsParser#exprflot.
    def visitExprflot(self, ctx:exprsParser.ExprflotContext):
        [col] = list(ctx.getChildren())

        return float(col.getText())
    
    # Visit a parse tree produced by exprsParser#table.
    def visitTable(self, ctx):
        [table] = list(ctx.getChildren())

        if table.getText() not in st.session_state:
            return pd.read_csv(table.getText() + ".csv")

        return st.session_state[table.getText()]

    # Visit a parse tree produced by exprsParser#order.
    def visitOrder(self, ctx):
        [o,b,c] = list(ctx.getChildren())
        #Aqui ya tienes la lista de campos i la lista de ordering,
        # Decidir si hacerlo en la etiqueta de query o directamente desde aqui.
        # Ir a self.ts obtener el dataFrame i mostrarlo directamente        
        return self.visit(c)

    # Visit a parse tree produced by exprsParser#camps.
    def visitCamps(self, ctx):
        camps = list(ctx.getChildren())
        #Retornar la lista de campos [c1,c2,c3] i la lista de sus ordering [False,True,False]
        listac = []
        for x in camps:
            if (x.getText() != ','):
                listac.append(self.visit(x))
       
        return listac


    # Visit a parse tree produced by exprsParser#camp.
    def visitCamp(self, ctx):
        camp = list(ctx.getChildren())
        if (len(camp) == 1):
            return (camp[0].getText(),True)
        else:
            asc = False
            if (camp[1].getText() == "ASC" or camp[1].getText() == "ASC"):
                asc = True
            return (camp[0].getText(), asc)
    
    # Visit a parse tree produced by exprsParser#subquery.
    def visitSubquery(self, ctx):
        [camp,i,_,query,_] =  list(ctx.getChildren())
        
        return (camp.getText(),self.visit(query))
    
    #Parte del where
    def visitWhere(self, ctx):
        [w,conditions] = list(ctx.getChildren())

        return self.visit(conditions)

    # Visit a parse tree produced by exprsParser#conditions.
    def visitConditions(self, ctx:exprsParser.ConditionsContext):
        conds = list(ctx.getChildren())
        #? select * from c where not r=1 and not r=2 and r=2 and not r=4;
        #Retornar la lista de campos [[('not', ('r', '=', '1')), ('not', ('r', '=', '2')), ('r', '=', '2'), ('not', ('r', '=', '4'))]
        listaconds = []
        for x in conds:
            if (x.getText() != 'and'):
                listaconds.append(self.visit(x))
       
        return listaconds
    

    # Visit a parse tree produced by exprsParser#col.
    def visitCond(self, ctx):
        [col,op,value] = list(ctx.getChildren())
        
        return (col.getText(),op.getText(),value.getText())


    # Visit a parse tree produced by exprsParser#paren.
    def visitParen(self, ctx):
        [_,conditions,_] = list(ctx.getChildren())
        
        return self.visit(conditions)


    # Visit a parse tree produced by exprsParser#not.
    def visitNot(self, ctx):
        [no,cond] = list(ctx.getChildren())

        c = self.visit(cond)
        return (no.getText(),c)



evalu= EvalVisitor()
if submit_button:
    input_stream = InputStream(user_input)
    lexer = exprsLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = exprsParser(token_stream)
    
    tree = parser.root() 
    evalu.visit(tree)
