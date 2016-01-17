# -*- coding: utf-8 -*-
from datetime import date
import re, os, numpy, pandas

"""
 --- Cargando datos ---
 * El proyecto debe correrse desde el directorio base
 * output_data almacena la data luego del procesamiento
 
"""
input_data = pandas.read_csv(os.getcwd()+'/dat/data.csv', header=None, skiprows=1)
output_data = pandas.DataFrame(
	columns=['ID', 'PeriodY', 'PeriodN', 'Age', 'Birthday', 'CivilStatus', 'Gender', 'School', 'IngressY', 'IngressM', 
	'Average', 'Efficiency', 'Semester', 'Enrolled', 'Approved', 'Withdrawals', 'Failed',
	'ReasonOfFailed']
	)

"""
 --- Cédula ---
 * El identificador de c/u de las instancias
 
"""
output_data.ID = input_data[2].drop_duplicates()

"""
 --- Período académico ---
 1. Eliminando separadores entre número de período y año (pueden der espacio, '-', '/' y '\')
 2. Separando período (que se compone de año y número) en las columnas PeriodY y PeriodoN respectivamente
	2.1. Tomando los períodos que cumplan con el formato <número><año> 
	2.2. Tomando los períodos que cumplan con el formato <año><número>
	2.3. Juntando (2) y (3) en un mismo dataframe
 3. Estandarización de la columna PeriodN
 4. Estandarización de la columna PeriodY
 5. Inputación de datos erróneos o faltantes con la moda
	
"""    
# Paso 1
period_messy = input_data[1].str.replace('[\s\\\\\-\/]','') 

# Paso 2.1: extrae en los grupos year y number (c/u en distintas columnas) las cadenas con de forma <año><número>
period = period_messy.str.extract('^(?P<year>(?:20)?\d{2})(?P<number>pri(?:mero)?|seg(?:undo)?|ii?|0?[12]s?)$', re.I)

# Paso 2.2: extrae en los grupos year y number (c/u en distintas columnas) las cadenas con de forma <número><año>
period_p2 = period_messy.str.extract('^(?P<number>pri(?:mero)?|seg(?:undo)?|ii?|0?[12]s?)(?P<year>(?:20)?\d{2})$', re.I)

# Paso 2.3: Se juntan en un mismo data frame los posibles casos (intersección es nula por lo que no hay pérdida de datos)
period.update(period_p2)

# Paso 3: Estandarización de los números de período
output_data.PeriodN = period.number.str.lower().replace([r'pri(mero)?|i|0?1s|01s?', r'seg(undo)?|ii|0?2s|02s?'], [1,2], regex=True)

# Paso 4: Estandarización de los años, todos con 4 dígitos
# Se decide imputar el valor de los años expresado en 2 dígitos en el siglo XXI dado que el dataset no muestra ningún registro
# de que los valores puedan estar en alguna otra época 
output_data.PeriodY = period.year.str.replace('^\d{2}$', lambda x: '20'+x.group(0))

# Paso 5
output_data.PeriodN = output_data.PeriodN.fillna(output_data.PeriodN.mode().iloc[0])
output_data.PeriodY = output_data.PeriodY.fillna(output_data.PeriodY.mode().iloc[0]).astype('int')

"""
 --- Edad ---
 1. Estandarización de la edad a dígitos
	
"""
output_data.Age = input_data[4].str.replace('^(\d{1,2})[^0-9]+', lambda x: x.group(1)).astype('int')

"""
 --- Fecha de nacimiento ---
 1. Estandarización de la fecha a años con 4 dígitos
 2. Estandarización de la fecha a formato yyyy-mm-dd
 3. Inputar datos erróneos o faltantes con el año del período académico - edad
	
"""
current_year = date.today().strftime('%y')

# Paso 1: función lambda evalua si 2 digitos de año > año actual => el año es del siglo XX sino el año es del siglo XXI
output_data.Birthday = input_data[3].str.replace('^\d{1,2}[\s/-]?\d{1,2}[\s/-]?\d{2}$', lambda x: ['%s19%s'%(b,a) if a>current_year else '%s20%s'%(b,a) for b in [x.group(0)[:-2]] for a in [x.group(0)[-2:]]][0])

# Paso 2
output_data.Birthday = pandas.to_datetime(output_data.Birthday, dayfirst=True, errors='coerce')

# Paso 3
output_data.Birthday = output_data.apply(lambda x: pandas.to_datetime('%d/01/01' % (x.PeriodY-x.Age)) if pandas.isnull(x.Birthday) else x.Birthday, axis=1)

"""
 --- Estado civil ---
 1. Limpiar dataframe, en el que los valores posibles serán {soltero(a), casado(a), viudo(a)}
 2. Categorizar la data
 3. Imputar datos erróneos o faltantes con la moda
	
"""
# Paso 1 y 2
output_data.CivilStatus = input_data[5].str.lower().replace([r'^soltero.*', r'^casado.*', r'^viudo.*', r'(?!^(soltero|casado|viudo).*)'], [0, 1, 2, numpy.nan], regex=True)

# Paso 3
output_data.CivilStatus = output_data.CivilStatus.fillna(output_data.CivilStatus.mode().iloc[0])

"""
 --- Sexo ---
 1. Limpiar dataframe, en el que los valores posibles serán {femenino, masculino}
 2. Categorizar la data
 3. Imputar datos erróneos o faltantes con la moda
	
"""
# Paso 1 y 2
output_data.Gender = input_data[6].str.lower().replace([r'^f(?:emenino)?', r'^m(?:asculino)?', r'(?!^f(?:emenino)?|m(?:asculino)?)'], [0, 1, numpy.nan] , regex=True)

# Paso 3
output_data.Gender = output_data.Gender.fillna(output_data.Gender.mode().iloc[0])

"""
 --- Escuela ---
 1. Limpiar dataframe, en el que los valores posibles serán {enfermeria, bioanalisis}
 2. Categorizar la data
 3. Imputar datos erróneos o faltantes con la moda
	
"""
# Paso 1 y 2
output_data.School = input_data[7].str.lower().replace(['enfermería', 'bioanálisis', r'(?!enfermería|bioanálisis)'], [0, 1, numpy.nan], regex=True)

# Paso 3
output_data.School = output_data.School.fillna(output_data.School.mode().iloc[0])

"""
 --- Año de ingreso ---
 1. En caso de años con 2 dígitos, llevarlos a 4
	
"""
output_data.IngressY = input_data[8].apply(lambda x: x if x>=1900 else (x+1900 if x>int(current_year) else x+2000))

"""
 --- Modalidad de ingreso ---
 1. Limpiar dataframe, en el que los valores posibles serán {interinstitucionales, prueba interna, internos, opsu}
 2. Categorizar la data
 3. Imputar datos erróneos o faltantes con la moda
	
"""
# Paso 1 y 2
output_data.IngressM = input_data[9].str.replace('\s','').str.lower()
output_data.IngressM = output_data.IngressM.replace([r'.*interinstitucional(es)?.*', r'^pruebainterna.*', r'^internos.*', r'.*opsu.*', r'(?!.*interinstitucional(es)?.*|^pruebainterna.*|^internos.*|.*opsu.*)'], [0, 1, 2, 3, numpy.nan], regex=True)

# Paso 3
output_data.IngressM = output_data.IngressM.fillna(output_data.IngressM.mode().iloc[0])

"""
 --- Promedio Ponderado ---
 1. Limpiar dataframe, en el que los valores posibles serán entre {0, 20}
 3. Imputar datos erróneos o faltantes con la media
	
"""
# Paso 1
output_data.Average = input_data[17].apply(lambda x: float(x) if x>=0 and x<=20 else (float(x)/1000.0 if x>=1000 and x<=20000 else numpy.nan))

# Paso 2
output_data.Average = output_data.Average.fillna(output_data.Average.mean())

"""
 --- Eficiencia ---
 1. Limpiar dataframe, en el que los valores posibles serán entre {0, 1}
 3. Imputar datos erróneos o faltantes con la media
	
"""
# Paso 1
output_data.Efficiency = input_data[18].apply(lambda x: float(x) if x>=0 and x<=1 else (float(x)/10000.0 if x>=1000 and x<=10000 else numpy.nan))

# Paso 2
output_data.Efficiency = output_data.Efficiency.fillna(output_data.Efficiency.mean())

"""
 --- Semestre ---
 1. Limpiar dataframe, en el que los valores posibles sean numéricos
 2. Imputar datos erróneos con la moda
	
"""
# Paso 1 
output_data.Semester = input_data[10].str.replace('^(\d{1,2}).*', lambda x: x.group(1)).astype('int')
output_data.Semester = output_data.Semester.apply(lambda x: x if x>0 and x<=10 else numpy.nan)

# Paso 2
output_data.Semester = output_data.Semester.fillna(output_data.Semester.mode().iloc[0])

"""
 --- Materias Inscritas, aprobadas, retiradas y reprobadas del semestre anterior ---
 1. Limpiar dataframes, en el que los valores posibles sean numéricos
 2. Imputar datos erróneos de acuerdo a que cumpla que materias inscritas = materias aprobadas + materias retiradas + materias reprobadas
	
"""
# Paso 1
output_data.Enrolled = input_data[13]
output_data.Approved = input_data[14].str.extract('^(\d{1,2})$').astype('float')
output_data.Withdrawals = input_data[15]
output_data.Failed = input_data[16]
output_data.ReasonOfFailed = input_data[19]

# Paso 2: hipótesis planteada: La columna inscritos esta correcta
# Descartando personas con eficiencia 1 y además quienes no tienen razón de reprobar
# Se asume como pre-condición que es un requisito obligatorio para quienes reprobaron
# materias expresar un motivo
output_data.Failed = output_data.apply(lambda x: 0 if x.Efficiency == 1.0 else (0 if pandas.isnull(x.ReasonOfFailed) else x.Failed), axis=1)

# Recuperar valores perdidos en aprobadas
output_data.Approved = output_data.apply(lambda x: x.Enrolled-x.Failed-x.Withdrawals if pandas.isnull(x.Approved) else x.Approved, axis=1)

# Dado que la proporción de estudiantes con materias retiradas es baja, se asume
# que si retiradas > inscritas-aprobadas-reprobadas => 0
output_data.Withdrawals = output_data.apply(lambda x: 0 if x.Withdrawals > (x.Enrolled-x.Failed-x.Approved) else x.Withdrawals, axis=1)

# Casos en que el error se encuentra en la columna aprobadas
output_data.Approved = output_data.apply(lambda x: x.Enrolled-x.Failed-x.Withdrawals if x.Enrolled != (x.Approved+x.Withdrawals+x.Failed) else x.Approved, axis=1)

prueba = output_data.apply(lambda x: x.Enrolled != (x.Approved+x.Withdrawals+x.Failed), axis=1)

output_data[prueba].to_csv(dir+'/dat/prueba4.csv', float_format='%.3f', date_format='%d/%m/%Y')