# -*- coding: utf-8 -*-
"""
@authors: 
    Lorenzo Rinaldi, Department of Energy, Politecnico di Milano, Italy
"""


import pandas as pd
from ieapy.constants import (
    sets,
    index_acts_dict,
    index_find_dict,
    index_sats,
    flow_commodity_map,
    )
import copy

sN = slice(None)

def sut_empty(
        instance,
        net_export,
        ):
    
    region = instance.region
    index_coms = copy.deepcopy(sets['Balances']['Flows'])
    
    index_acts = []
    for i,acts in index_acts_dict.items():
        for a in acts:
            index_acts += [f"{i} - {a}"]
    index_find = []
    for i,fds in index_find_dict.items():
        for f in fds:
            index_find += [f"{i} - {f}"]
    
    if net_export:
        index_fp = ['None']
    else:
        index_fp = ['Imports']
        

    U = pd.DataFrame(
        0,
        index   = pd.MultiIndex.from_arrays([[region for i in range(len(index_coms))],['Commodity'for i in range(len(index_coms))],index_coms]),
        columns = pd.MultiIndex.from_arrays([[region for i in range(len(index_acts))],['Activity'for i in range(len(index_acts))],index_acts]),
        )

    S = copy.deepcopy(U).T
    Y = pd.DataFrame(
        0,
        index   = pd.MultiIndex.from_arrays([[region for i in range(len(index_coms))],['Commodity'for i in range(len(index_coms))],index_coms]),
        columns = pd.MultiIndex.from_arrays([[region for i in range(len(index_find))],['Consumption category'for i in range(len(index_find))],index_find]),
        )

    E = pd.DataFrame(
        0,
        index   = index_sats,
        columns = pd.MultiIndex.from_arrays([[region for i in range(len(index_acts))],['Activity'for i in range(len(index_acts))],index_acts]),
        )

    V = pd.DataFrame(
        0,
        index   = index_fp,
        columns = pd.MultiIndex.from_arrays([[region for i in range(len(index_coms))],['Commodity'for i in range(len(index_coms))],index_coms]),
        )

    empty_matrices = {
        'U':U,
        'S':S,
        'Y':Y,
        'E':E,
        'V':V,
        }
    
    return empty_matrices



def fill_S(
        instance,
        S:pd.DataFrame(),
        )->pd.DataFrame():
    
    "Mining"
    acts = [f"Mining - {a}" for a in index_acts_dict['Mining']]
    for act in acts:
        flow = act.split(' - ')[-1]
        S.loc[(sN,sN,act),(sN,sN,flow)] += instance.data['Balances']['Total Energy Supply'].loc['Production',flow]
        
    "Electricity production"
    acts = [f"Electricity production - {a}" for a in index_acts_dict['Electricity production']]
    for act in acts:
        flow = act.split(' - ')[-1]
        prod_ee = copy.deepcopy(instance.data['Electricity']['Total production'])
        prod_ee.reset_index(inplace=True)
        prod_ee['Flows mapped'] = prod_ee['Flows'].map(flow_commodity_map['Electricity'])
        prod_ee.set_index(['Flows','Flows mapped'],inplace=True)
        prod_ee = prod_ee.groupby(level='Flows mapped').sum()
        prod_ee.index.names = ['Flows']
        S.loc[(sN,sN,act),(sN,sN,'Electricity')] += prod_ee.loc[flow,"Total production"]
    
    "Heat production"
    acts = [f"Heat production - {a}" for a in index_acts_dict['Heat production']]
    for act in acts:
        flow = act.split(' - ')[-1]
        prod_heat = copy.deepcopy(instance.data['Heat']['Total production'])
        prod_heat.reset_index(inplace=True)
        prod_heat['Flows mapped'] = prod_heat['Flows'].map(flow_commodity_map['Electricity'])
        prod_heat.set_index(['Flows','Flows mapped'],inplace=True)
        prod_heat = prod_heat.groupby(level='Flows mapped').sum()
        prod_heat.index.names = ['Flows']
        S.loc[(sN,sN,act),(sN,sN,'Heat')] += prod_heat.loc[flow,"Total production"]
    
    "Biofuels and waste"
    acts = [f"Biofuels and waste - {a}" for a in index_acts_dict['Biofuels and waste']]
    for act in acts:
        if "Waste treatment" in act:
            prod_waste = (instance.data['Electricity']['Total production'].loc[["Municipal Waste","Waste (renewable)"],"Total production"] + instance.data['Heat']['Total production'].loc[["Municipal Waste","Waste (renewable)"],"Total production"]).sum()  
            S.loc[(sN,sN,act),(sN,sN,'Biofuels and waste')] = prod_waste
        else:
            prod_bio = instance.data['Balances']['Total Energy Supply'].loc['Production','Biofuels and waste'] - (instance.data['Electricity']['Total production'].loc[["Municipal Waste","Waste (renewable)"],"Total production"] + instance.data['Heat']['Total production'].loc[["Municipal Waste","Waste (renewable)"],"Total production"]).sum()  
            S.loc[(sN,sN,act),(sN,sN,'Biofuels and waste')] += prod_bio
    
    "Refinery"
    acts = [f"Refinery - {a}" for a in index_acts_dict['Refinery']]
    for act in acts:
        refined_prod = instance.data['Balances']['Transformation'].loc[[i.split(" - ")[-1] for i in [act]],:]
        refined_prod = refined_prod.clip(lower=0)
        for flow in refined_prod.columns:
            if refined_prod.loc[act.split(' - ')[-1],flow] >0:
                S.loc[(sN,sN,act),(sN,sN,flow)] += refined_prod.loc[act.split(' - ')[-1],flow]  
    
    return S
        


def fill_U(
        instance,
        U:pd.DataFrame(),
        )->pd.DataFrame():
    
     "Mining"
     acts = [f"Mining - {a}" for a in index_acts_dict['Mining']]
     avoid_in_own_use = []
     for act in acts:
         flow = act.split(' - ')[-1]
         U.loc[(sN,sN,flow),(sN,sN,act)] += -instance.data['Balances']['Transformation'].loc['Energy industry own use',flow]
         if -instance.data['Balances']['Transformation'].loc['Energy industry own use',flow] > 0:
             avoid_in_own_use += [flow]    
    
     "Electricity production"
     acts = [f"Electricity production - {a}" for a in index_acts_dict['Electricity production']]
     for act in acts:
         flow = act.split(' - ')[-1]
         try:
             U.loc[(sN,sN,flow),(sN,sN,act)] += -instance.data['Balances']['Transformation'].loc['Electricity plants',flow]
         except:
             pass
    
     "Heat production"
     acts = [f"Heat production - {a}" for a in index_acts_dict['Heat production']]
     for act in acts:
         flow = act.split(' - ')[-1]
         try:
             U.loc[(sN,sN,flow),(sN,sN,act)] += -instance.data['Balances']['Transformation'].loc['Heat plants',flow]
         except:
             pass
    
     "Refinery"
     acts = [f"Refinery - {a}" for a in index_acts_dict['Refinery']]
     for act in acts:
         refined_prod = instance.data['Balances']['Transformation'].loc[[i.split(" - ")[-1] for i in [act]],:]
         for flow in refined_prod.columns:
             if refined_prod.loc[act.split(' - ')[-1],flow] <0:
                 U.loc[(sN,sN,flow),(sN,sN,act)] += -refined_prod.loc[act.split(' - ')[-1],flow]
    
     return (
         U, 
         avoid_in_own_use,
         )



def fill_Y(
        instance,
        Y:pd.DataFrame(),
        avoid_in_own_use:list,
        net_export:bool,
        )->pd.DataFrame():

    "Total Final Consumption"
    fds = [f"Total Final Consumption - {f}" for f in index_find_dict['Total Final Consumption']]
    for fd in fds:
        f = fd.split(' - ')[-1]
        for flow in instance.data['Balances']['Total Final Consumption'].columns:
            try:
                Y.loc[(sN,sN,flow),(sN,sN,fd)] = instance.data['Balances']['Total Final Consumption'].loc[f,flow]
            except:
                Y.loc[(sN,sN,'Electricity'),(sN,sN,fd)] += instance.data['Balances']['Total Final Consumption'].loc[f,flow]
    
    "Losses"
    fds = [f"Losses - {f}" for f in index_find_dict['Losses']]
    for fd in fds:
        f = fd.split(' - ')[-1]
        for flow in instance.data['Balances']['Transformation'].columns:
            if flow not in avoid_in_own_use:
                try:
                    Y.loc[(sN,sN,flow),(sN,sN,fd)] += -instance.data['Balances']['Transformation'].loc[f,flow]
                except:
                    pass
    
    Y.loc[(sN,sN,'Electricity'),(sN,sN,'Losses - Energy industry own use')] += -instance.data['Balances']['Transformation'].loc['Heat plants','Electricity']
    Y.loc[(sN,sN,'Heat'),(sN,sN,'Losses - Energy industry own use')] += -instance.data['Balances']['Transformation'].loc['Electricity plants','Heat']
    
    "Trades"
    fds = [f"Trades - {f}" for f in index_find_dict['Trades']]
    for fd in fds:
        f = fd.split(' - ')[-1]
        for flow in instance.data['Balances']['Total Energy Supply'].columns:
            try:
                if flow=='Imports':
                    if net_export==False:
                        pass
                else:
                    Y.loc[(sN,sN,flow),(sN,sN,fd)] += -instance.data['Balances']['Total Energy Supply'].loc[f,flow]
            except:
                pass
    
    "Stocks"
    fds = [f"Stocks - {f}" for f in index_find_dict['Stocks']]
    for fd in fds:
        f = fd.split(' - ')[-1]
        for flow in instance.data['Balances']['Total Energy Supply'].columns:
            try:
                Y.loc[(sN,sN,flow),(sN,sN,fd)] += -instance.data['Balances']['Total Energy Supply'].loc[f,flow]
            except:
                pass        
    
    "Stats and transfers"
    fds = [f"Stats and transfer - {f}" for f in index_find_dict['Stats and transfer']]
    for fd in fds:
        f = fd.split(' - ')[-1]
        for flow in instance.data['Balances']['Transformation'].columns:
            try:
                Y.loc[(sN,sN,flow),(sN,sN,fd)] += -instance.data['Balances']['Transformation'].loc[f,flow]
            except:
                pass       
    
    return Y
    



def fill_E(
        instance,
        E:pd.DataFrame(),
        U:pd.DataFrame(),
        efficiency:pd.DataFrame(),
        )->pd.DataFrame():

    "Biofuels and waste"
    acts = [f"Biofuels and waste - {a}" for a in index_acts_dict['Biofuels and waste']]
    for act in acts:
        if "Waste treatment" in act:
            prod_waste = (instance.data['Electricity']['Total production'].loc[["Municipal Waste","Waste (renewable)"],"Total production"] + instance.data['Heat']['Total production'].loc[["Municipal Waste","Waste (renewable)"],"Total production"]).sum()  
            E.loc['Biofuels and waste',(sN,sN,act)] += prod_waste
        else:
            prod_bio = instance.data['Balances']['Total Energy Supply'].loc['Production','Biofuels and waste'] - (instance.data['Electricity']['Total production'].loc[["Municipal Waste","Waste (renewable)"],"Total production"] + instance.data['Heat']['Total production'].loc[["Municipal Waste","Waste (renewable)"],"Total production"]).sum()  
            E.loc['Biofuels and waste',(sN,sN,act)] += prod_bio
    
    "Mining"
    acts = [f"Mining - {a}" for a in index_acts_dict['Mining']]
    for act in acts:
        flow = act.split(' - ')[-1]
        try:
            E.loc[flow,(sN,sN,act)] += instance.data['Balances']['Total Energy Supply'].loc['Production',flow] - U.loc[:,(sN,sN,act)].sum().sum()
        except:
            pass
    
    "Electricity production"
    acts = [f"Electricity production - {a}" for a in index_acts_dict['Electricity production']]
    for act in acts:
        flow = act.split(' - ')[-1]
        if flow in ['Hydro','Wind, solar, etc.']:
            try:
                E.loc[flow,(sN,sN,act)] += -instance.data['Balances']['Transformation'].loc['Electricity plants',flow]*efficiency.loc['Electricity plants',flow]
            except:
                pass
    
    "Heat production"
    acts = [f"Heat production - {a}" for a in index_acts_dict['Heat production']]
    for act in acts:
        flow = act.split(' - ')[-1]
        try:
            E.loc[flow,(sN,sN,act)] += -instance.data['Balances']['Transformation'].loc['Heat plants',flow]*efficiency.loc['Heat plants',flow]
        except:
            pass
    
    return E

           

def fill_V(
        instance,
        V:pd.DataFrame(),
        net_export:bool,
        )->pd.DataFrame():
    

    "Trades"
    if net_export:
        return V
    else:
        for flow in instance.data['Balances']['Total Energy Supply'].columns:
            V.loc['Imports',(sN,sN,flow)] += instance.data['Balances']['Total Energy Supply'].loc['Imports',flow]
        return V