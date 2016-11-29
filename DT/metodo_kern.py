# -*- coding: cp1252 -*-
# Módulo de Equações para Trocadores de Calor Duplo-Tubo
# Última alteração: 19:32 18/09/2016

from math import *
from dupl_tubo import *

fluido1={'Vazao':0,'T_entr':0,'T_said':0,'cp':0,'k':0,'Pr':0,'Viscos':0,
         'Densidade':0,'Diam_ext':0,'Diam_int':0,'Annulus':0,'Liquido':0,'Viscos_tw':0}
fluido2={'Vazao':0,'T_entr':0,'T_said':0,'cp':0,'k':0,'Pr':0,'Viscos':0,
         'Densidade':0,'Diam_ext':0,'Diam_int':0,'Annulus':1,'Liquido':0,'Viscos_tw':0}
material={'K':0,'L':1, 'R_fi':0,'R_fo':0,'Calor_cnste':0,'Contracorrente':0,
          'Num_tubs':0,'Alet_per_tube':0,'Alet_alt':0,'Alet_K':0,'Alet_espes':0,
          'Alet_type':0,'Tubo_aletado':0,'Multi_tube':0}

########################### LEMBRAR DE: ############################################
#   1º Corrigir Banco de Dados
#   2º 
#   3º 
#   4º 
####################################################################################


def yut(fluido1,fluido2,material):
    if not all([fluido1['Vazao'],fluido2['Vazao'],fluido1['T_entr'],
                fluido1['T_said'],fluido2['T_entr'],fluido2['T_said']]):
        calor_vazao(fluido1,fluido2) # Add in the commments section!
    if material['arranj_ser_paral']==True:
        if material['T_I_Paralelo']:
            fluido1['Vazao']=fluido1['Vazao']/material['Num_ramos']
        elif material['R_A_Paralelo']:
            fluido2['Vazao']=fluido2['Vazao']/material['Num_ramos']
    reynolds_tube(fluido1,fluido2,material)
    nusselt_tube(fluido1,fluido2,material)
    nusselt_tube(fluido2,fluido1,material)
    dTm=check_dtm(fluido1,fluido2,material)    
    h_i=fluido1['Nu']*fluido1['k']/fluido1['Diam_int']
    if material['Tubo_aletado']==True:
        d_h,h_o,U_d,U_c,A_tot=alets(fluido1,fluido2,material)
    else:
        # Annulus - UNfinned
        h_o=fluido2['Nu']*fluido2['k']/((fluido2['Diam_int']**2-fluido1['Diam_ext']**2)/fluido1['Diam_ext'])
        U_d=(fluido1['Diam_ext']/(fluido1['Diam_int']*h_i)+(fluido1['Diam_ext']*material['R_fi'])/fluido1['Diam_int']+(fluido1['Diam_ext']*log(fluido1['Diam_ext']/fluido1['Diam_int']))/(2*material['K'])+material['R_fo']+(1/h_o))**-1
        U_c=((fluido1['Diam_ext']/(fluido1['Diam_int']*h_i))+(fluido1['Diam_ext']*log(fluido1['Diam_ext']/fluido1['Diam_int'])/(2*material['K']))+(h_o**-1))**-1
    q=fluido1['Vazao']*fluido1['cp']*abs(fluido1['T_entr']-fluido1['T_said'])
    if material['arranj_ser_paral']==True:
        F_p=dupl_fact_ser_paral(material)
        area=q/(U_d*F_p*dTm)
    else:
        area=(q)/(U_d*dTm);
    area_grampo=A_tot if material['Tubo_aletado']==True else 2*pi*fluido1['Diam_ext']*material['L']
    if material['arranj_ser_paral']==True:
        x=int(area/area_grampo);n=material['Num_ramos'];
        num_grampo=(x//n)*n+n
    else:
        num_grampo=int(area/area_grampo) if area/area_grampo==int(area/area_grampo) else int(area/area_grampo)+1 
    material['Num_gramp']=num_grampo
    Pressure_drop_serth(fluido1,material)
    if material['Tubo_aletado']==True:
        Pressure_drop_serth(fluido2,material,diam_h=d_h)
    else:    
        Pressure_drop_serth(fluido2,material,diam_h=fluido2['Diam_int']-fluido1['Diam_ext'])
    fluido1['Potencia_bomb']=fluido1['Vazao']*fluido1[u'\u0394Ptotal']/(material['Efic_bomb1']*fluido1['Densidade'])
    fluido2['Potencia_bomb']=fluido2['Vazao']*fluido2[u'\u0394Ptotal']/(material['Efic_bomb2']*fluido2['Densidade'])
    CF=U_d/U_c;OS=100*U_c*(1-CF)/(U_c*CF)
    result_fl={u'Vazão':(str(fluido1['Vazao'])+u' Kg/s',str(fluido2['Vazao'])+u' Kg/s'),
                u'Temperatura de Entrada':(str(fluido1['T_entr'])+u' ºC',str(fluido2['T_entr'])+u' ºC'),
                u'Temperatura de Saída':(str(fluido1['T_said'])+u' ºC',str(fluido2['T_said'])+u' ºC'),
                u'Velocidade Média de Escoamento':(str(fluido1['Vel_m'])+u' m/s',str(fluido2['Vel_m'])+u' m/s'),
                u'Número de Reynolds':(str(fluido1['Re'])+u' ',str(fluido2['Re'])+u' '),
                u'Número de Nusselts':(str(fluido1['Nu'])+u' ',str(fluido2['Nu'])+u' '),
                u'Coeficiente de Película (h)':(str(h_i)+u' W/m2.K',str(h_o)+u' W/m2.K')};
    result_pres={u'\u2206P':(str(fluido1[u'\u0394P'])+u' Pa',str(fluido2[u'\u0394P'])+u' Pa'),
                u'\u2206Prb':(str(material[u'\u0394Pr1'])+u' Pa',str(material[u'\u0394Pr2'])+u' Pa'),
                u'\u2206Ptotal':(str(fluido1[u'\u0394Ptotal'])+u' Pa',str(fluido2[u'\u0394Ptotal'])+u' Pa'),
                u'Potência de Bombeamento':(str(fluido1['Potencia_bomb'])+u' W',str(fluido2['Potencia_bomb'])+u' W'),
                u'\u2206Pnl (bocais)':(str('---')+u' Pa',str(material[u'\u0394Pn'])+u' Pa')}
    result_geral={u'Área de Troca Térmica Total':(str(area)+u' m2'),
                u'Calor Trocado (Heat Duty)':(str(q)+u' J'),
                u'Coef. de Trans. de Calor Limpo (Uc)':(str(U_c)+u' W/m2.K'),
                u'Coef. de Trans. de Calor Incrustado (Ud)':(str(U_d)+u' W/m2.K'),
                u'Fator de Limpeza (CF)':(str(CF)+u' '),
                u'Var. Log. de Temperatura (\u2206Tm)':(str(dTm)+u' K'),
                u'Área por Grampo Tubular':(str(area_grampo)+u' m2'),
                u'Número de Grampos':(str(num_grampo)+u' grampo(s)'),
                u'Excesso de Área (Over-Surface Design)':(str(OS)+u'%')}
    return result_fl,result_pres,result_geral


# Exemplo 6.1 Kakaç e Liu (2002)
'''
fluido1={'Vazao':0,'T_entr':140,'T_said':125,'cp':4268,'k':0.687,'Pr':1.28,'Viscos':0.207*10**-3,'Densidade':932.53,'Diam_ext':0.0603,'Diam_int':0.0525,'Annulus':0,'Liquido':1,'Viscos_tw':0.196*10**-3};fluido2={'Vazao':5000/3600.,'T_entr':20,'T_said':35,'cp':4179,'k':0.609,'Pr':5.77,'Viscos':0.841*10**-3,'Densidade':996.4,'Diam_ext':0,'Diam_int':0.0779,'Annulus':1,'Liquido':1,'Viscos_tw':0.719*10**-3};material={'K':54,'L':3.5, 'R_fi':0.000176,'R_fo':0.000352,'Calor_cnste':1,'Contracorrente':1,'Efic_bomb1':0.8,'Efic_bomb2':0.8,'Num_tubs':0,'Alet_per_tube':0,'Alet_alt':0,'Alet_K':0,'Alet_espes':0,'Alet_type':0,'Tubos_Aletado':0}
'''

# Exemplo 6.3 STT Sample
"""
fluido1={'Pr':16.16959743921541,'Annulus':0,'T_entr':148.8889,'T_said':154.444,'cp':2473.926, 'Liquido':1,'Diam_int':0.052502,'Vazao':4.56741944,'Viscos':8.247780588*10**-4,'Diam_ext':0.060452,'k':0.1261899,'Densidade':758.8635647561536,'Viscos_tw':0};fluido2={'Pr':67.12089254763255,'Annulus':1,'T_entr':232.2222,'T_said':176.6667,'cp':2595.32, 'Liquido':1,'Diam_int':0.077927,'Vazao':0.869384666666,'Viscos':0.00299942964836582,'Diam_ext':0.0889,'k':0.115977,'Densidade':770.8837447469,'Viscos_tw':0};material={'K': 54, 'L': 6.096, 'Calor_cnste': 1, 'R_fi':0.0056869019274806264 , 'R_fo': 0.0056869019274806264, 'Contracorrente': 1,'Efic_bomb1':0.8,'Efic_bomb2':0.8,'Num_tubs':0,'Alet_per_tube':0,'Alet_alt':0,'Alet_K':0,'Alet_espes':0,'Alet_type':0,'Tubos_Aletado':0}
"""

# Exemplo 6.1 Kern
"""
fluido1={'Pr': 1735.2*(541.23*10**-6)/(140.1072*10**-3), 'Annulus': 0, 'T_entr': 26.6, 'T_said': 48.8, 'cp': 1735.2, 'Liquido': 1, 'Diam_int': 35.052*10**-3, 'Vazao': 1.2372, 'Viscos': 541.23*10**-6, 'Diam_ext': 42.164*10**-3, 'k': 140.1072*10**-3, 'Densidade': 860.111, 'Viscos_tw': 0};fluido2={'Pr':1768.3*(575.7156*10**-6)/(121.154*10**-3) , 'Annulus': 1, 'T_entr': 71.1, 'T_said': 37.8, 'cp': 1768.3, 'Liquido': 1, 'Diam_int': 52.5018*10**-3, 'Vazao': 0.0, 'Viscos': 575.7156*10**-6, 'Diam_ext': 60.452*10**-3, 'k': 121.154*10**-3, 'Densidade': 834.356, 'Viscos_tw': 0};material={'K': 54, 'L': 6.096, 'Calor_cnste': 1, 'R_fi':0.0002 , 'R_fo': 0.0002, 'Contracorrente': 1,'Efic_bomb1':0.8,'Efic_bomb2':0.8,'Num_tubs':0,'Alet_per_tube':0,'Alet_alt':0,'Alet_K':0,'Alet_espes':0,'Alet_type':0,'Tubos_Aletado':0}
"""

# Exemplo Serth 4.1 pg 116
"""
fluido1={'Vazao':1.26,'T_entr':15.5556,'T_said':48.889,'cp':1758.456,'k':0.1594452,'Pr':6.06572,'Viscos':0.55*10**-3,'Densidade':879.0,'Diam_ext':0.0603, 'Diam_int':0.0525,'Annulus':0, 'Liquido':1,'Viscos_tw':0.33*10**-3};fluido2={'Vazao':0,'T_entr':65.5556,'T_said':37.7778,'cp':2177.136,'k':0.1731,'Pr':25.15466,'Viscos':2*10**-3,'Densidade':1022.0,'Diam_ext':0,'Diam_int':0.0779,'Annulus':1,'Liquido':1,'Viscos_tw':1.55*10**-3};material={'K':16.2714,'L':4.8768, 'R_fi':0.000176,'R_fo':0.000352, 'Calor_cnste':1,'Contracorrente':1,'Efic_bomb1':0.8,'Efic_bomb2':0.8,'Num_tubs':0,'Alet_per_tube':0,'Alet_alt':0,'Alet_K':0,'Alet_espes':0,'Alet_type':0,'Tubos_Aletado':0}
"""

# Exemplo 6.2 Kakaç e Liu pg 206
"""
fluido1={'Vazao':0,'T_entr':20,'T_said':30,'cp':4004.0,'k':0.693,'Pr':6.29,'Viscos':9.64*10**-4,'Densidade':1013.4,'Diam_ext':0.0266,'Diam_int':0.02093,'Annulus':0,'Liquido':1,'Viscos_tw':9.64*10**-4};fluido2={'Vazao':3.0,'T_entr':65,'T_said':55,'cp':1902.0,'k':0.1442,'Pr':1050.0,'Viscos':0.075,'Densidade':885.27,'Diam_ext':0,'Diam_int':0.0525,'Annulus':1,'Liquido':1,'Viscos_tw':0.197};material={'K':52,'L':4.5, 'R_fi':0.000176,'R_fo':0.088*10**-3,'Calor_cnste':1,'Contracorrente':1,'Efic_bomb1':0.8,'Efic_bomb2':0.8,'Num_tubs':1,'Alet_per_tube':30,'Alet_alt':0.0127,'Alet_K':52,'Alet_espes':0.9*10**-3,'Alet_type':'retangular','Tubos_Aletado':1}
"""





