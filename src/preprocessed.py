# -*- coding: utf-8 -*-
from datetime import date
import re, os, numpy, pandas

"""
 --- Cargando datos ---
 * El proyecto debe correrse desde el directorio base
 * output_data almacena la data luego del procesamiento
 
"""
project = os.getcwd()
input_data = pandas.read_csv(project+'/dat/data.csv', header=None, skiprows=1)
output_data = pandas.DataFrame(
	columns=['ID', 'PeriodY', 'PeriodN', 'Age', 'Birthday', 'CivilStatus', 'Gender', 'School', 'AdmissionY', 'AdmissionM', 
	'Average', 'Efficiency', 'Semester', 'Enrolled', 'Approved', 'Withdrawals', 'Failed', 'ReasonOfFailed', 'Subjects',
	'EnrollThesis', 'Origin', 'Residence', 'Roommates', 'ChangeAddress', 'HousingType', 'Breadwinner', 'FamilyLoad', 
	'BreadwinnerIncome', 'BreadwinnerOthersIncomes', 'BreadwinnerTotalIncome', 'BreadwinnerFood', 'BreadwinnerTransportation', 
	'BreadwinnerMedical', 'BreadwinnerDental', 'BreadwinnerStudy', 'Services', 'Condominium', 'BreadwinnerOtherExpenses', 
	'BreadwinnerTotalExpenses', 'FinancialAid', 'Work', 'Scolarship', 'InputBreadwinner', 'Family', 'InputWork', 'TotalIncome', 
	'Food', 'Transportation', 'Medical', 'Dental', 'Personal', 'Rental', 'AuxRentalColumn','Study', 'Entertainment', 
	'OtherExpenses', 'TotalExpenses', 'Rating']
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
 3. Transformación de la columna PeriodN
 4. Transformación de la columna PeriodY
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

# Paso 3: Transformación de los números de período a enteros {1,2}
output_data.PeriodN = period.number.str.lower().replace([r'pri(mero)?|i|0?1s|01s?', r'seg(undo)?|ii|0?2s|02s?'], [1,2], regex=True)

# Paso 4: Transformación de los años, todos con 4 dígitos
# Se decide imputar el valor de los años expresado en 2 dígitos en el siglo XXI dado que el dataset no muestra ningún registro
# de que los valores puedan estar en alguna otra época 
output_data.PeriodY = period.year.str.replace('^\d{2}$', lambda x: '20'+x.group(0))

# Paso 5
output_data.PeriodN = output_data.PeriodN.fillna(output_data.PeriodN.mode().iloc[0])
output_data.PeriodY = output_data.PeriodY.fillna(output_data.PeriodY.mode().iloc[0]).astype('int')

"""
 --- Edad ---
 1. Casteo de la edad a entero
	
"""
output_data.Age = input_data[4].str.replace('^(\d{1,2})[^0-9]+', lambda x: x.group(1)).astype('int')

"""
 --- Fecha de nacimiento ---
 1. Transformación de la fecha a años con 4 dígitos
 2. Transformación de la fecha a formato yyyy-mm-dd
 3. Inputar datos erróneos o faltantes con el (año del período académico - edad)
	
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
 1. Limpiar series, en el que los valores posibles serán {soltero(a), casado(a), viudo(a)}
 2. Codificar las categorías {soltero: 0, casado: 1, viudo: 2}
 3. Imputar datos erróneos o faltantes con la moda
	
"""
# Paso 1 y 2
output_data.CivilStatus = input_data[5].str.lower().replace([r'^soltero.*', r'^casado.*', r'^viudo.*', r'.*'], [0, 1, 2, numpy.nan], regex=True)

# Paso 3
output_data.CivilStatus = output_data.CivilStatus.fillna(output_data.CivilStatus.mode().iloc[0])

"""
 --- Sexo ---
 1. Limpiar series, en el que los valores posibles serán {femenino, masculino}
 2. Codificar las categorías {femenino: 0, masculino: 1}
 3. Imputar datos erróneos o faltantes con la moda
	
"""
# Paso 1 y 2
output_data.Gender = input_data[6].str.lower().replace([r'^f(?:emenino)?', r'^m(?:asculino)?', r'.*'], [0, 1, numpy.nan] , regex=True)

# Paso 3
output_data.Gender = output_data.Gender.fillna(output_data.Gender.mode().iloc[0])

"""
 --- Escuela ---
 1. Limpiar series, en el que los valores posibles serán {enfermería, bioanálisis}
 2. Codificar las categorías {enfermería: 0, bioanálisis: 1}
 3. Imputar datos erróneos o faltantes con la moda
	
"""
# Paso 1 y 2
output_data.School = input_data[7].str.lower().replace(['enfermería', 'bioanálisis', r'.*'], [0, 1, numpy.nan], regex=True)

# Paso 3
output_data.School = output_data.School.fillna(output_data.School.mode().iloc[0])

"""
 --- Año de ingreso ---
 1. En caso de años con 2 dígitos, llevarlos a 4
	
"""
output_data.AdmissionY = input_data[8].apply(lambda x: x if x>=1900 else (x+1900 if x>int(current_year) else x+2000))

"""
 --- Modalidad de ingreso ---
 1. Limpiar series, en el que los valores posibles serán {interinstitucionales, prueba interna, internos, opsu}
 2. Codificar las categorías {interinstitucionales: 0, prueba interna: 1, internos: 2, opsu: 3}
 3. Imputar datos erróneos o faltantes con la moda
	
"""
# Paso 1 y 2
output_data.AdmissionM = input_data[9].str.replace('\s','').str.lower()
output_data.AdmissionM = output_data.AdmissionM.replace([r'.*interinstitucional(es)?.*', r'^pruebainterna.*', r'^internos.*', r'.*opsu.*', r'.*'], [0, 1, 2, 3, numpy.nan], regex=True)

# Paso 3
output_data.AdmissionM = output_data.AdmissionM.fillna(output_data.AdmissionM.mode().iloc[0])

"""
 --- Promedio ponderado ---
 1. Limpiar series, en el que los valores posibles serán entre {0, 20}
 2. Imputar datos erróneos o faltantes con la media
	
"""
# Paso 1
output_data.Average = input_data[17].apply(lambda x: float(x) if x>=0 and x<=20 else (float(x)/1000.0 if x>=1000 and x<=20000 else numpy.nan))

# Paso 2
output_data.Average = output_data.Average.fillna(output_data.Average.mean())

"""
 --- Eficiencia ---
 1. Limpiar series, en el que los valores posibles serán entre {0, 1}
 2. Imputar datos erróneos o faltantes con la media
	
"""
# Paso 1
output_data.Efficiency = input_data[18].apply(lambda x: float(x) if x>=0 and x<=1 else (float(x)/10000.0 if x>=1000 and x<=10000 else numpy.nan))

# Paso 2
output_data.Efficiency = output_data.Efficiency.fillna(output_data.Efficiency.mean())

"""
 --- Semestre ---
 1. Limpiar series, en el que los valores posibles sean numéricos y entre {1,10}
 2. Imputar datos erróneos con la moda
	
"""
# Paso 1 
output_data.Semester = input_data[10].str.replace('^(\d{1,2}).*', lambda x: x.group(1)).astype('int')
output_data.Semester = output_data.Semester.apply(lambda x: x if x>0 and x<=10 else numpy.nan)

# Paso 2
output_data.Semester = output_data.Semester.fillna(output_data.Semester.mode().iloc[0])

"""
 --- Materias inscritas, aprobadas, retiradas y reprobadas del semestre anterior ---
 1. Limpiar series, en el que los valores posibles sean numéricos
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

# Si eficiencia 1 => No hay razones de reprobar
output_data.ReasonOfFailed = output_data.apply(lambda x: None if x.Efficiency == 1.0 else x.ReasonOfFailed, axis=1)

"""
 --- Materias inscritas en el semestre en curso ---
 * Data limpia, por lo que no se aplica ningún proceso
	
"""
output_data.Subjects = input_data[20] 

"""
 --- Cantidad de veces en que inscribió Trabajo Especial/Pasantías de Grado ---
 1. Unir columnas (21) y (22) de input_data
 2. Codificar las categorías (No := 0, Si => ('1 vez' := 1, '2 veces' := 2, 'más de 2' := 3) )
 3. Valores inconsistentes entre (21) y (22) se le imputará 0 dado que todos los casos en que ocurre son estudiantes de semestres bajos

"""
# Paso 1 y 2
enrolled = input_data[21].replace(['Si', 'No'], [True, False]) 
amounts = input_data[22].replace([r'^Primera.+', r'^Segunda.+', r'^Más.+', r'.*)'], [1,2,3,numpy.nan], regex=True)
enrolled_thesis = pandas.DataFrame({'enrolled': enrolled, 'amounts': amounts})

# Paso 3
output_data.EnrolledThesis = enrolled_thesis.apply(lambda x: x.amounts if pandas.isnull(x.amounts)==False and x.enrolled else 0, axis=1)

"""
 --- Procedencia ---
 1. Codificar las categorías (todos representarán estados)

"""
output_data.Origin = input_data[23].replace([r'.+Libertador.*',r'(.+Sucre|.*(Baruta|Hatillo|Chacao|Altos|Guarenas|Valles)).*',r'Ara.*',r'Apu.*',r'Tác.*',r'Var.*',r'Mon.*',r'Por.*',r'Nue*.',r'Tru*.',r'Lar.*',r'Bol.*',r'Bar.*',r'Suc.*',r'Anz.*',r'Mér.*',r'Delta.*',r'Yar.*',r'Guár.*'], range(19), regex=True)

"""
 --- Residencia ---
 1. Codificar las categorías (todos representarán zonas de Dtto Capital y el Edo. Miranda)
 2. A los valores faltantes, se imputa la moda

"""

output_data.Residence = input_data[24].replace([r'.+Libertador.*',r'.*Sucre.*',r'.*Baruta.*',r'.*Hatillo.*',r'.*Chacao.*',r'.*Altos.*',r'.*Guarenas.*',r'.*Valles.*'], range(8), regex=True)
output_data.Residence = output_data.Residence.fillna(output_data.Residence.mode().iloc[0])

"""
 --- Compañeros de habitación ---
 1. Codificar las categorías 
    valores posibles {padres, esposo o hijo, madre, padre, familiares maternos, familiares paternos, solo, otros}

"""
output_data.Roommates = input_data[25].str.lower().str.replace('\s', '')
output_data.Roommates = output_data.Roommates.replace([r'.*padres.*',r'.*(esposo(?<!su)|hijo).*',r'.*(mamá|madre).*',r'.*(papá|padre).*',r'.+maternos.*',r'.+paternos.*',r'sol[oa]',r'.+'], range(8), regex=True)

"""
 --- Cambio de dirección ---
 1. Codificar las categorías, valores posibles {si, no}

"""
output_data.ChangeAddress = input_data[11].replace(['No', 'Si'], [0, 1])

"""
 --- Tipo de vivienda ---
 1. Codificar las categorías
 	valores posibles {quinta, edific, urbano, rural, alquilada, vecindad, estudiantil, otros}

"""
output_data.HousingType = input_data[26].str.lower().replace([r'.*quinta.*',r'.*edific.*',r'.*urbano.*',r'.*rural.*',r'.*alquilada.*',r'.*vecindad.*',r'.*estudiantil.*', r'.*'],range(8),regex=True)

"""
 --- Responsable económico ---
 1. Codificar las categorías
 	valores posibles {padres, madre, padre, cónyugue, usted, familiares, otros}

"""
output_data.Breadwinner = input_data[49].str.lower()
output_data.Breadwinner = output_data.Breadwinner.replace([r'.*padres.*',r'.*madre.*',r'.*padre.*',r'.*(cónyugue|esposo).*',r'.*(usted|ninguno).*',r'.*(familiares|abuel[oa]|herman[oa]|ti[oa]).*',r'.*'], range(7), regex=True)

"""
 --- Carga familiar del responsable económico ---
 * Data limpia, por lo que no se aplica ningún proceso

"""
output_data.FamilyLoad = input_data[50]

"""
 --- Ingreso del responsable económico ---
 1. Limpiar data, eliminando todos los caracteres que no sean numéricos y agregando '.' en las  ','
 2. Imputar en las entradas vacias 0

"""
output_data.BreadwinnerIncome = input_data[51].str.replace(',','.').str.replace('[a-zA-Z\s]','')
output_data.BreadwinnerIncome = output_data.BreadwinnerIncome.apply(lambda x: x.replace('.','',1) if x.count('.')>1 else x).astype('float')

"""
 --- Otros ingresos del responsable económico ---
 1. Limpiar data, eliminando todos los caracteres que no sean numéricos
 2. Imputar en las entradas vacias 0

"""
output_data.BreadwinnerOthersIncomes = input_data[52].str.replace('[a-zA-Z\s]','').str.extract('^(\d+\.?\d*)+$').astype('float')
output_data.BreadwinnerOthersIncomes = output_data.BreadwinnerOthersIncomes.fillna(0)

"""
 --- Ingresos totales del responsable económico ---
 1. Suma de columnas de ingresos del responsable (ingresos + otros)

"""
output_data.BreadwinnerTotalIncome = output_data.apply(lambda x: x.BreadwinnerIncome+x.BreadwinnerOthersIncomes, axis=1)

"""
 --- Gastos de alimentación del responsable económico ---
 1. Limpiar columna, de modo de que sean numéricas las entradas
 2. Imputar con la moda

"""
output_data.BreadwinnerFood = input_data[55].str.replace('^(\d+\.?\d*)(bs)?$', lambda x: x.group(1)).str.extract('^(\d+\.?\d*)$').astype('float')
output_data.BreadwinnerFood = output_data.BreadwinnerFood.fillna(output_data.BreadwinnerFood.mode().iloc[0])

"""
 --- Gastos de transporte público del responsable económico ---
 1. Limpiar columna, de modo de que sean numéricas las entradas
 2. Imputar con la moda

"""
output_data.BreadwinnerTransportation = input_data[56].str.replace('^(\d+\.?\d*)(bs)?$', lambda x: x.group(1)).str.extract('^(\d+\.?\d*)$').astype('float')
output_data.BreadwinnerTransportation = output_data.BreadwinnerTransportation.fillna(output_data.BreadwinnerTransportation.mode().iloc[0])

"""
 --- Gastos médicos del responsable económico ---
 1. Limpiar columna, de modo de que sean numéricas las entradas
 2. Imputar con la moda

"""
output_data.BreadwinnerMedical = input_data[57].str.replace('^(\d+\.?\d*)(bs)?$', lambda x: x.group(1)).str.extract('^(\d+\.?\d*)$').astype('float')
output_data.BreadwinnerMedical = output_data.BreadwinnerMedical.fillna(output_data.BreadwinnerMedical.mode().iloc[0])

"""
 --- Gastos odontológicos del responsable económico ---
 1. Limpiar columna, de modo de que sean numéricas las entradas
 2. Imputar con la moda

"""
output_data.BreadwinnerDental = input_data[58].str.extract('^(\d+\.?\d*)$').astype('float')
output_data.BreadwinnerDental = output_data.BreadwinnerDental.fillna(output_data.BreadwinnerDental.mode().iloc[0])

"""
 --- Gastos educativos del responsable económico ---
 1. Imputar con 0

"""
output_data.BreadwinnerStudy = input_data[59].fillna(0)

"""
 --- Gastos en servicios del responsable económico ---
 1. Limpiar columna, de modo de que sean numéricas las entradas
 2. Imputar con la moda

"""
output_data.Services = input_data[60].str.replace('^(\d+\.?\d*)(bs)?$', lambda x: x.group(1)).str.extract('^(\d+\.?\d*)$').astype('float')
output_data.Services = output_data.Services.fillna(output_data.Services.mode().iloc[0])

"""
 --- Gastos en condominio del responsable económico ---
 1. Limpiar columna, de modo de que sean numéricas las entradas
 2. Imputar con la moda

"""
output_data.Condominium = input_data[61].str.replace('^(\d+\.?\d*)(bs)?$', lambda x: x.group(1)).str.extract('^(\d+\.?\d*)$').astype('float')
output_data.Condominium = output_data.Condominium.fillna(output_data.Condominium.mode().iloc[0])

"""
 --- Otros gastos del responsable económico ---
 2. Imputar con la moda

"""
output_data.BreadwinnerOtherExpenses = input_data[62].fillna(input_data[62].mode().iloc[0])

"""
 --- Total de egresos del responsable económico ---
 1. Suma de columnas de gastos (alimentación+transporte+médicos+odontológico+estudio+servicios+condominio+otros)
 
"""
output_data.BreadwinnerTotalExpenses = output_data.apply(lambda x: x.BreadwinnerFood+x.BreadwinnerTransportation+x.BreadwinnerMedical+x.BreadwinnerDental+x.BreadwinnerStudy+x.Services+x.Condominium+x.BreadwinnerOtherExpenses, axis=1)

"""
 --- Solicitud de ayuda financiera a la universidad ---
 1. Codificar las categorías, valores posibles {no, si}

"""
output_data.FinancialAid = input_data[30].replace(['No', 'Si'], [0, 1])

"""
 --- Actividad generadora de ingresos ---
 1. Codificar las categorías, valores posibles {no, si}

"""
output_data.Work = input_data[32].replace(['No', 'Si'], [0, 1])

"""
 --- Monto de la beca ---
 1. Corrigiendo valores a modo que tenga 4 dígitos, cuyos valores posibles serán {1500, 2000} 

"""
output_data.Scolarship = input_data[34].apply(lambda x: x*10 if x<1000 else(x/10 if x>9999 else x))
output_data.Scolarship = output_data.Scolarship.apply(lambda x: 1500 if x<=1500 else 2000)

"""
 --- Aporte de responsable económico ---
 1. Imputar valores faltantes con 0

"""
output_data.InputBreadwinner = input_data[35].fillna(0)

"""
 --- Aporte de familiares y amigos ---
 1. Imputar valores faltantes con 0

"""
output_data.Family = input_data[36].fillna(0)

"""
 --- Aporte por trabajo ---
 1. Imputar valores faltantes con 0

"""
output_data.InputWork = input_data[37].fillna(0)

"""
 --- Ingresos totales ---
 1. Suma de columnas de aportes (responsable económico + familiares y amigos + trabajo)

"""
output_data.TotalIncome = output_data.apply(lambda x: x.Scolarship+x.InputBreadwinner+x.Family+x.InputWork, axis=1)

"""
 --- Gastos de alimentación ---
 1. Llenar valores faltantes con la moda, dado que es poco probable que no haya gastos en alimentación

"""
output_data.Food = input_data[39].fillna(input_data[39].mode().iloc[0])

"""
 --- Gastos en transporte público ---
 1. Llenar valores faltantes con la moda, dado que es poco probable que no haya gastos en transporte

"""
output_data.Transportation = input_data[40].fillna(input_data[40].mode().iloc[0])

"""
 --- Gastos médicos ---
 1. Llenar valores faltantes con 0

"""
output_data.Medical = input_data[41].fillna(0)

"""
 --- Gastos odontológicos ---
 1. Llenar valores faltantes con 0

"""
output_data.Dental = input_data[42].fillna(0)

"""
 --- Gastos personales ---
 1. Llenar valores faltantes con la moda, dado que es poco probable que no haya gastos personales

"""
output_data.Personal = input_data[43].fillna(input_data[43].mode().iloc[0])

"""
 --- Gastos en alquiler ---
 1. Filtrar personas con vivienda alquilada o residencia estudiantil
 2. Almacenar temporalmente en el dataset la columna 27 (precio de alquiler)
 3. Para personas que con tipo de vivienda distinto a vivienda alquilada o residencia estudiantil imputar con 0,
    Para los casos de valores nulos o 0 en personas con alquiler, asignar valor de columna 27
    Sino, dejar el valor de de la columna Rental
 4. Imputar con la moda en los casos que en ambas columnas esten sin valor

"""
# Paso 1
output_data.Rental = input_data[44]
# Paso 2
output_data.AuxRentalColumn = input_data[27].str.replace('^(\d+\.?\d*)(bs)?$', lambda x: x.group(1)).str.extract('^(\d+\.?\d*)$').astype('float')
# Paso 3
output_data.Rental = output_data.apply(lambda x: 0 if x.HousingType!=6 and x.HousingType!=4 else (x.AuxRentalColumn if pandas.isnull(x.Rental) or x.Rental<=0 else x.Rental), axis=1)
# Paso 4
output_data.Rental = output_data.Rental.fillna(output_data.Rental.mode().iloc[0])

"""
 --- Gastos en material de estudio ---
 * Columna limpia, por lo que no se aplica ningún proceso
 
"""
output_data.Study = input_data[45]

"""
 --- Gastos en recreación ---
 1. Llenar valores faltantes con la moda
 
"""
output_data.Entertainment = input_data[46].fillna(input_data[46].mode().iloc[0])

"""
 --- Otros gastos ---
 1. Llenar valores faltantes con la moda
 
"""
output_data.OtherExpenses = input_data[47].fillna(input_data[47].mode().iloc[0])

"""
 --- Total de egresos ---
 1. Suma de columnas de gastos (alimentación+transporte+médicos+odontológico+personales+alquiler+estudio+recreación+otros)
 
"""
output_data.TotalExpenses = output_data.apply(lambda x: x.Food+x.Transportation+x.Medical+x.Dental+x.Personal+x.Rental+x.Study+x.Entertainment+x.OtherExpenses, axis=1)

"""
 --- Rating ---
 * Columna limpia, por lo que no se aplica ningún proceso 

"""
output_data.Rating = input_data[64]

# Eliminando columnas que sirvieron para brindar integridad a otras pero que no aportan información relevante
# Edad := 3 | Precio de Alquier := 52
output_data = output_data.drop(output_data.columns[[3, 52]], axis=1)

# Generando salida
output_data.to_csv(project+'/dat/becas_crema.csv', 
		index=False, float_format='%.3f', 
		header=['C.I.', 'Período Académico Renovado (Año)', 'Período Académico Renovado (ID)', 'Fecha de Nacimiento', 'Estado Civil', 'Sexo', 'Escuela', 
		'Año de Ingreso', 'Modo de Ingreso', 'Promedio Ponderado', 'Eficiencia', 'Semestre', 'Materias Inscritas (Semestre y/o Año Anterior)', 
		'Materias Aprobadas (Semestre y/o Año Anterior)', 'Materias Retiradas (Semestre y/o Año Anterior)', 'Materias Reprobadas (Semestre y/o Año Anterior)', 
		'Motivo de Materias Reprobadas', 'Materias Inscritas Actualmente', 'Tesis Inscrita', 'Procedencia', 'Residencia', 'Compañeros de Habitación', 
		'Cambio de Dirección', 'Tipo de Vivienda', 'Responsable Económico', 'Carga Familiar', 'Ingresos Responsable Económico', 'Otros Ingresos Responsable Económico', 
		'Total de Ingresos Responsable Económico', 'Alimentación Responsable Económico', 'Transporte Responsable Económico', 'Gastos Médicos Responsable Económico', 
		'Gastos Odontológicos Responsable Económico', 'Gastos de Estudio Responsable Económico', 'Servicios Públicos', 'Condominio', 'Otros Gastos Responsable Económico', 
		'Total Egresos Responsable Económico', 'Ayuda financiera', 'Trabajo', 'Beca', 'Aporte de Responsable Económico', 'Aporte Familiar', 'Ingresos Laborales', 
		'Ingresos Totales', 'Alimentación', 'Transporte', 'Gastos Médicos', 'Gastos Odontológicos', 'Gastos Personales', 'Gastos de Alquiler', 'Gastos Estudiantiles', 
		'Recreación', 'Otros Gastos', 'Total Egresos', 'Puntación'],
		date_format='%d/%m/%Y')