from datetime import date
import re, os, numpy, pandas

"""
 --- Cargando datos ---
 * El proyecto debe correrse desde el directorio base
 * output_data almacena la data luego del procesamiento
 
"""
input_data = pandas.read_csv(os.getcwd()+'/dat/data.csv', header=None, skiprows=1)
output_data = pandas.DataFrame(
	columns=['CI', 'PeriodoA', 'PeriodoN', 'FechaNac', 'Edad', 'EdoCivil', 'Sexo', 'Escuela', 'IngresoA', 'IngresoM', 'Semestre']
	)

"""
 --- Cedula ---
 * El identificador de c/u de las instancias
 
"""
output_data.CI = input_data[2].astype(numpy.int).drop_duplicates()

"""
 --- Periodo academico ---
 1. Eliminando separadores entre periodo y ano (pueden der espacio, '-', '/' y '\')
 2. Separando periodo (que se compone de ano y numero) en las columnas PeriodoA y PeriodoN respectivamente
	2.1. Tomando los periodos que cumplan con el formato <periodo><ano> 
	2.2. Tomando los periodos que cumplan con el formato <ano><periodo>
	2.3. Juntando (2) y (3) en un mismo dataframe
 3. Estandarizacion de la columna PeriodoN
 4. Estandarizacion de la columna PeriodoA
 5. Inputacion de datos erroneos o faltantes 
	
"""    
# Paso 1
period_messy = input_data[1].str.replace('[\s\\\\\-\/]','') 

# Paso 2.1: extrae en los grupos year y number (c/u en distintas columnas) las cadenas con de forma <ano><periodo>
period = period_messy.str.extract('^(?P<year>(?:20)?\d{2})(?P<number>pri(?:mero)?|seg(?:undo)?|ii?|0?[12]s?)$', re.I)

# Paso 2.2: extrae en los grupos year y number (c/u en distintas columnas) las cadenas con de forma <periodo><ano>
period_p2 = period_messy.str.extract('^(?P<number>pri(?:mero)?|seg(?:undo)?|ii?|0?[12]s?)(?P<year>(?:20)?\d{2})$', re.I)

# Paso 2.3: Se juntan en un mismo data frame los posibles casos (interseccion es nula por lo que no hay perdida de datos)
period.update(period_p2)

# Paso 3: Se binariza las entradas de acuerdo a el siguiente conjunto (con valores posibles de {1,2})
repl = {'pri':'1','primero':'1','i':'1','1s':'1','01':'1','01s':'1',
		'seg':'2','segundo':'2','ii':'2','2s':'2','02':'2','02s':'2'}
output_data.PeriodoN = period.number.str.replace('pri(mero)?|seg(undo)?|ii?|0?[12]s|0[12]s?', lambda x: repl[x.group(0).lower()], flags=re.I)

# Paso 4: Estandarizacion de los anos, todos con 4 digitos
# Se decide imputar el valor de los anos expresado en 2 digitos en el siglo XXI dado que el set de datos no muestra ningun registro
# que los valores puedan estar en alguna otra epoca 
output_data.PeriodoA = period.year.str.replace('^\d{2}$', lambda x: '20'+x.group(0))

# Paso 5: inputacion de datos erroneos o faltantes mediante la moda estadistica
output_data.PeriodoN = output_data.PeriodoN.fillna(output_data.PeriodoN.mode().iloc[0])
output_data.PeriodoA = output_data.PeriodoA.fillna(output_data.PeriodoA.mode().iloc[0])

"""
 --- Fecha de nacimiento ---
 1. Estandarizacion de la fecha a anos con 4 digitos
 2. Estandarizacion de la fecha a formato yyyy-mm-dd
	
"""
current_year = date.today().strftime('%y')

# Paso 1: funcion lambda evalua si 2 digitos de ano > a el actual => el ano es del siglo XX sino el ano es del siglo XXI
output_data.FechaNac = input_data[3].str.replace('^\d{1,2}[\s/-]?\d{1,2}[\s/-]?\d{2}$', 
	lambda x: x.group(0)[:-2]+'19'+x.group(0)[-2:] if x.group(0)[-2:]>current_year else x.group(0)[:-2]+'20'+x.group(0)[-2:])

# Paso 2	
output_data.FechaNac = pandas.to_datetime(output_data.FechaNac, dayfirst=True, errors='coerce')

"""
 --- Edad ---
 1. Estandarizacion de la edad a digitos
	
"""
output_data.Edad = input_data[4].str.replace('(\d{1,2}).+', lambda x: x.group(1))

"""
 --- Estado civil ---
 1. Limpiar dataframe, en el que los valores posibles seran {soltero(a), casado(a), viudo(a)}
 2. Categorizar la data
 3. Imputar datos erroneos de acuerdo a la moda estadistica
	
"""
output_data.EdoCivil = input_data[5].str.extract('^(soltero|casado|viudo).*', re.I)