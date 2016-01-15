from datetime import date
import re, os, numpy, pandas

"""
 --- Cargando datos ---
 * El proyecto debe correrse desde el directorio base
 * output_data almacena la data luego del procesamiento
 
"""
input_data = pandas.read_csv(os.getcwd()+'/dat/data.csv', header=None, skiprows=1)
output_data = pandas.DataFrame(
	columns=['CI', 'PeriodoA', 'PeriodoN', 'FechaNac', 'Edad', 'EdoCivil', 'Sexo', 'Escuela', 'AnoDeIngreso', 'ModoDeIngreso', 
	'PromedioPond', 'Eficiencia', 'Semestre', 'NroMateriasInsc', 'NroMateriasAprob', 'NroMateriasRet', 'NroMateriasReprob']
	)

"""
 --- Cedula ---
 * El identificador de c/u de las instancias
 
"""
output_data.CI = input_data[2].drop_duplicates()

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

# Paso 3: Estandarizacion de los numeros de periodo
output_data.PeriodoN = period.number.str.lower().replace([r'pri(mero)?|i|0?1s|01s?', r'seg(undo)?|ii|0?2s|02s?'], [1,2], regex=True)

# Paso 4: Estandarizacion de los anos, todos con 4 digitos
# Se decide imputar el valor de los anos expresado en 2 digitos en el siglo XXI dado que el set de datos no muestra ningun registro
# que los valores puedan estar en alguna otra epoca 
output_data.PeriodoA = period.year.str.replace('^\d{2}$', lambda x: '20'+x.group(0))

# Paso 5: inputacion de datos erroneos o faltantes mediante la moda estadistica
output_data.PeriodoN = output_data.PeriodoN.fillna(output_data.PeriodoN.mode().iloc[0])
output_data.PeriodoA = output_data.PeriodoA.fillna(output_data.PeriodoA.mode().iloc[0]).astype('int')

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
output_data.Edad = input_data[4].str.replace('^(\d{1,2})[^0-9]+', lambda x: x.group(1)).astype('int')

"""
 --- Estado civil ---
 1. Limpiar dataframe, en el que los valores posibles seran {soltero(a), casado(a), viudo(a)}
 2. Categorizar la data
 3. Imputar datos erroneos de acuerdo a la moda estadistica
	
"""
# Paso 1 y 2
output_data.EdoCivil = input_data[5].str.lower().replace([r'^soltero.*', r'^casado.*', r'^viudo.*', r'(?!^(soltero|casado|viudo).*)'], [0, 1, 2, numpy.nan], regex=True)

# Paso 3
output_data.EdoCivil = output_data.EdoCivil.fillna(output_data.EdoCivil.mode().iloc[0])

"""
 --- Sexo ---
 1. Limpiar dataframe, en el que los valores posibles seran {femenino, masculino}
 2. Categorizar la data
 3. Imputar datos erroneos de acuerdo a la moda estadistica
	
"""
# Paso 1 y 2
output_data.Sexo = input_data[6].str.lower().replace([r'^f(?:emenino)?', r'^m(?:asculino)?', r'(?!^f(?:emenino)?|m(?:asculino)?)'], [0, 1, numpy.nan] , regex=True)

# Paso 3
output_data.Sexo = output_data.Sexo.fillna(output_data.Sexo.mode().iloc[0])

"""
 --- Escuela ---
 1. Limpiar dataframe, en el que los valores posibles seran {enfermeria, bioanalisis}
 2. Categorizar la data
 3. Imputar datos erroneos de acuerdo a la moda estadistica
	
"""
# Paso 1 y 2
output_data.Escuela = input_data[7].str.lower().replace(['enfermería', 'bioanálisis', r'(?!enfermería|bioanálisis)'], [0, 1, numpy.nan], regex=True)

# Paso 3
output_data.Escuela = output_data.Escuela.fillna(output_data.Escuela.mode().iloc[0])

"""
 --- Ano de ingreso ---
 1. En caso de anos con dos digitos, llevarlos a 4
	
"""
output_data.AnoDeIngreso = input_data[8].apply(lambda x: x+1900 if x<100 and x>int(current_year) else (x+2000 if x<100 and x<=int(current_year) else x))

"""
 --- Modalidad de ingreso ---
 1. Limpiar dataframe, en el que los valores posibles seran {interinstitucionales, prueba interna, internos, opsu}
 2. Categorizar la data
 3. Imputar datos erroneos de acuerdo a la moda estadistica
	
"""
# Paso 1 y 2
output_data.ModoDeIngreso = input_data[9].str.replace('\s','').str.lower()
output_data.ModoDeIngreso = output_data.ModoDeIngreso.replace([r'.*interinstitucional(es)?.*', r'^pruebainterna.*', r'^internos.*', r'.*opsu.*', r'(?!.*interinstitucional(es)?.*|^pruebainterna.*|^internos.*|.*opsu.*)'], [0, 1, 2, 3, numpy.nan], regex=True)

# Paso 3
output_data.ModoDeIngreso = output_data.ModoDeIngreso.fillna(output_data.ModoDeIngreso.mode().iloc[0])

"""
 --- Promedio Ponderado ---
 1. Limpiar dataframe, en el que los valores posibles seran entre {0, 20}
 3. Imputar datos erroneos o faltantes de acuerdo a la media
	
"""
# Paso 1
output_data.PromedioPond = input_data[17].apply(lambda x: x if x>=0 and x<=20 else (x/1000 if x>=1000 and x<=20000 else numpy.nan))

# Paso 2
output_data.PromedioPond = output_data.PromedioPond.fillna(output_data.PromedioPond.mean())

"""
 --- Eficiencia ---
 1. Limpiar dataframe, en el que los valores posibles seran entre {0, 20}
 3. Imputar datos erroneos o faltantes de acuerdo a la media
	
"""
# Paso 1
output_data.Eficiencia = input_data[18].apply(lambda x: x if x>=0 and x<=1 else (x/10000 if x>=1000 and x<=10000 else numpy.nan))

# Paso 2
output_data.Eficiencia = output_data.Eficiencia.fillna(output_data.Eficiencia.mean())

"""
 --- Semestre ---
 1. Limpiar dataframe, en el que los valores posibles sean numericos
 2. Imputar datos erroneos de acuerdo a la moda estadistica
	
"""
# Paso 1 
output_data.Semestre = input_data[10].str.replace('^(\d{1,2}).*', lambda x: x.group(1)).astype('int')
output_data.Semestre = output_data.Semestre.apply(lambda x: x if x>0 and x<=10 else numpy.nan)

# Paso 2
output_data.Semestre = output_data.Semestre.fillna(output_data.Semestre.mode().iloc[0])

"""
 --- Materias Inscritas, aprobadas, retiradas y reprobadas del semestre anterior ---
 1. Limpiar dataframes, en el que los valores posibles sean numericos
 2. Imputar datos erroneos de acuerdo a que materias inscritas = materias aprobadas + materias retiradas + materias reprobadas
	
"""
# Paso 1
output_data.NroMateriasInsc = input_data[13]
output_data.NroMateriasAprob = input_data[14].str.extract('^\d{1,2}$').astype('int')
output_data.NroMateriasInsc = input_data[15]
output_data.NroMateriasInsc = input_data[16]

# Paso 2 
output_data.NroMateriasInsc = output_data.apply(lambda x: )
output_data.NroMateriasAprob = input_data[14].str.extract('^\d{1,2}$').astype('int')
output_data.NroMateriasInsc = input_data[15]
output_data.NroMateriasInsc = input_data[16]
