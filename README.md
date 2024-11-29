PandaQ: consisteix en implementar un petit intèrpret anomenat PandaQ amb les característiques principals següents

-Entrada: subconjunt de consultes SQL

-Dades: arxius en format csv

-Tractament: llibreria pandas

-Interfície: Streamlit

Instalación y uso: Para utilizar este PandaQ se necessita los siguientes prerequisitos:          

   -Antrl4 para Python:

        1- pip install antlr4-tools
	2- antlr4
	3- pip install antlr4-python3-runtime

-Python3.10 o posterior. Puedes utilizar las siguientes comandas para instalar python3.10 en ubuntu:

		1- sudo add-apt-repository ppa:deadsnakes/ppa
		2- sudo apt update 
		3- sudo apt install python3.10
  
-Streamlit. Puedes utilizar las siguientes comandas para instalar streamlit en ubuntu

	1-pip install streamlit
        2-streamlit hello

-Para ejectar el panda-py con streamlit utiliza los siguientes comandos para generar los archivos necessarios:
        
        1- antlr4 -Dlanguage=Python3 -no-listener pandaQ.g4
        2- antlr4 -Dlanguage=Python3 -no-listener -visitor pandaQ.g4
        3- streamlit run PandaQ.py

Recuerda que los archivos anteriores comienzan por el nombre de la gramatica.

Características: Este programa consiste en traducir un subconjunto de consultas de SQL a funciones implementadas de la librería pandas. 

Este subconjunto de consultas están incluidos lo siguiente:

1- Integració bàsica

2- Camps

3- Order by

4- Where

5- InnerJoin

6- Taula de simbols

7- Plots

8- Subqueries

Exemples de Inputs:
       
     1- select * from countries;

     2.1- select first_name,last_name from employees;

     2.2- select first_name,salary, salary*1.05 as new_salary from employees;

     3- select * from countries order by region_id,country_name desc;

     4- select * from countries where not region_id=1 and not region_id=3;

     5.1- select first_name,department_name from employees inner join departments on department_id = department_id;

     5.2- select first_name,last_name,job_title,department_name from employees 
        inner join departments  on department_id = department_id inner join jobs on job_id = job_id;

     6.1- q := select first_name,last_name,job_title,department_name  from employees 
          inner join departments on department_id = department_id inner join jobs on job_id = job_id;

     6.2- select first_name,last_name from q;

     7.1- q := select first_name,salary, salary*1.05 as new_salary from employees where department_id = 5;
     7.2- plot q;

     8- select employee_id,first_name,last_name from employees where department_id in 
     (select department_id from departments where location_id = 1700) 
     order by first_name,last_name;

Podeu descarregar un arxiu que a la mateixa carpeta que conté les diferents taules en format csv per poder provar alguns funcionalitats anteriors descrits.
	
