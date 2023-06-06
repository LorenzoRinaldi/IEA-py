# -*- coding: utf-8 -*-
"""
@authors: 
    Lorenzo Rinaldi, Department of Energy, Politecnico di Milano, Italy
"""


import pandas as pd
from ieastatsbrowser.constants import sets,flow_commodity_map
import mario
from mario.tools.constants import _MASTER_INDEX as MI
from ieastatsbrowser.data_transformation import (
    sut_empty,
    fill_S,
    fill_U,
    fill_Y,
    fill_E,
    fill_V,
    )

from ieabrowser.errors import WrongInput


class iea_stats:
    
    def __init__(
            self,
            path_balances:str,
            path_electricity:str,
            region:str,
            CHP:bool = False,
            )->None:
                
        self.data = {
            'Balances': {},
            'Electricity': {},
            'Heat': {},
            }
        
        self.CHP_split = False
        self.region = region
        
        for k,v in sets['Balances'].items():
            if k !='Flows':
                self.data['Balances'][k] = pd.read_excel(path_balances,index_col=[0]).loc[v,:]
                self.data['Balances'][k] = self.data['Balances'][k].iloc[:,:-1]
    
    
        for k,v in sets['Electricity'].items():
            if k !='Flows':
                self.data['Electricity'][k] = pd.read_excel(path_electricity,index_col=[0], header=[0,1]).loc[v,('Electricity','GWh')].to_frame()
                self.data['Electricity'][k].columns = [k]
                self.data['Electricity'][k].index.names = ['Flows']

        for k,v in sets['Electricity'].items():
            if k !='Flows':
                self.data['Heat'][k] = pd.read_excel(path_electricity,index_col=[0], header=[0,1]).loc[v,('Heat','TJ')].to_frame()*3.6
                self.data['Heat'][k].columns = [k]
                self.data['Heat'][k].index.names = ['Flows']
                
        if CHP==False:
            self.split_CHP
        
        
    def split_CHP(
            self,
            )->None:
        
        """
        This function re-allocates CHP plants production to Electricity plants and Heat plants
              
        Returns
        -------
        None.

        """
        
        CHP_ee_prod = self.data['Balances']['Transformation'].loc['CHP plants','Electricity']
        CHP_heat_prod = self.data['Balances']['Transformation'].loc['CHP plants','Heat']
        
        CHP_ee_ratio = CHP_ee_prod/(CHP_ee_prod+CHP_heat_prod)
        CHP_heat_ratio = 1 - CHP_ee_ratio
        
        for flow in self.data['Balances']['Flows']:
            self.data['Balances']['Transformation'].loc['Electricity plants',flow] += self.data['Balances']['Transformation'].loc['CHP plants',flow]*CHP_ee_ratio
            self.data['Balances']['Transformation'].loc['Heat plants',flow] += self.data['Balances']['Transformation'].loc['CHP plants',flow]*CHP_heat_ratio
            self.data['Balances']['Transformation'].loc['CHP plants',flow] *= 0
            
    
    def calc_efficiency(
            self,
            )->pd.DataFrame():
        
        """
        This function calculates efficiencies of electricity and heat plants by source
        
        Returns
        -------
        pd.DataFrame
        """        
        
        techs = ['Electricity plants','Heat plants']
        
        efficiency = pd.DataFrame(
            0,
            index=techs, 
            columns=sets['Balances']['Flows']
            )
        
        for subflow,flow in flow_commodity_map['Electricity'].items():
            ee_prod_subflow = self.data['Electricity']['Total production'].loc[subflow,:].values[0]
            efficiency.loc["Electricity plants",flow] += ee_prod_subflow

            heat_prod_subflow = self.data['Heat']['Total production'].loc[subflow,:].values[0]
            efficiency.loc["Heat plants",flow] += heat_prod_subflow
        
        for flow in set([y for x,y in flow_commodity_map['Electricity'].items()]):
            efficiency.loc["Electricity plants",flow] /= -self.data['Balances']['Transformation'].loc['Electricity plants',flow]
            efficiency.loc["Heat plants",flow] /= -self.data['Balances']['Transformation'].loc['Heat plants',flow]
        
        efficiency = efficiency.fillna(0)
        efficiency = efficiency.clip(upper=1)

        return efficiency
        

    def calc_prod_mix(
            self,
            flows:list = ['Electricity','Heat'],
            )->dict:
        
        """ 
        This function calculates the production mix of a electricity and heat flows
        
        Parameters
        ----------
        flows : list
            list of flows, acceptable can be just 'Electricity' and heat

        Returns
        -------
        Dict
        
        """
        
        _ACCEPTABLE_FLOWS = ['Electricity','Heat']

        if set(flows) > set(_ACCEPTABLE_FLOWS ):
            raise WrongInput(f"Acceptable flows are {_ACCEPTABLE_FLOWS }")
        
        prod_mix = {}
        for flow in flows:
            if flow == ' Electricity':
                prod_mix[flow] = self.data['Electricity']['Total production']/self.data['Electricity']['Total production'].sum()
            if flow == ' Heat':
                prod_mix[flow] = self.data['Heat']['Total production']/self.data['Heat']['Total production'].sum()
                
        for flow,mix in prod_mix.items():
            mix.reset_index(inplace=True)
            mix['Flows mapped'] = mix['Flows'].map(flow_commodity_map['Electricity'])
            mix.set_index(['Flows','Flows mapped'],inplace=True)
            mix = mix.groupby(level='Flows mapped').sum()
            mix.index.names = ['Flows']
            prod_mix[flow] = mix       

        return prod_mix
        
        
    def to_sut(
            self,
            net_export:bool = True,
            ):

        """ 
        This function rearranges IEA statistics in the shape of a supply-use table
        
        Parameters
        ----------
        net_export : bool
            if True, imports will be treated as a final demand vector, else as a factor of production

        Returns
        -------
        mario.Database
        
        """
        
        empty_matrices = sut_empty(self,net_export) # Preparing empty matrices
        efficiency = self.calc_efficiency()
        
        S = fill_S(self, empty_matrices['S'])
        U, avoid_in_own_use = fill_U(self, empty_matrices['U'])
        Y = fill_Y(self, empty_matrices['Y'], avoid_in_own_use, net_export)
        E = fill_E(self, empty_matrices['E'], U, efficiency)
        V = fill_V(self, empty_matrices['V'], net_export)
            
        
        "Z matrix"
        Z = pd.DataFrame(0,index=pd.concat([S,U],axis=1).columns,columns=pd.concat([S,U],axis=1).columns)
        Z.update(U)
        Z.update(S)
        
        "E matrix"
        E_ca = pd.DataFrame(0,index=E.index,columns=Z.columns)
        E_ca.update(E)
        
        "Y matrix"
        Y_ca = pd.DataFrame(0,index=Z.index,columns=Y.columns)
        Y_ca.update(Y)
        
        "V matrix"
        V_ca = pd.DataFrame(0,index=V.index,columns=Z.columns)
        V_ca.update(V)
        
        "EY matrix"
        EY = pd.DataFrame(0,index=E.index,columns=Y.columns)
        
        units = {
            MI['c']: pd.DataFrame('TJ',index=sorted(list(set(U.index.get_level_values(-1)))),columns=['units']),
            MI['a']: pd.DataFrame('TJ',index=sorted(list(set(S.index.get_level_values(-1)))),columns=['units']),
            MI['f']: pd.DataFrame('TJ',index=V.index,columns=['units']),
            MI['k']: pd.DataFrame('TJ',index=E.index,columns=['units']),
            }
        
        sut = mario.Database(table='SUT',Z=Z,Y=Y_ca,V=V_ca,E=E_ca,EY=EY,units=units)
     
        return sut










