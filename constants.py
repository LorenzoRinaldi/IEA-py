# -*- coding: utf-8 -*-
"""
@author: 
    Lorenzo Rinaldi, Department of Energy, Politecnico di Milano, Italy
"""


sets = {
    'Balances': {
        'Total Energy Supply': [
            'Production',
            'Imports',
            'Exports',
            'International marine bunkers',
            'International aviation bunkers', 
            'Stock changes'
            ],
        'Transformation': [
            'Transfers',
            'Statistical differences',
            'Electricity plants',
            'CHP plants',
            'Heat plants',
            'Gas works',
            'Oil refineries',
            'Coal transformation',
            'Liquefication plants',
            'Other transformation',
            'Energy industry own use',
            'Losses'
            ],
        'Total Final Consumption': [
            'Industry',
            'Transport',
            'Residential',
            'Commercial and public services',
            'Agriculture / forestry',
            'Fishing',
            'Non-specified',
            'Non-energy use'
            ],
        'Flows': [
            'Coal',
            'Crude oil',
            'Oil products',
            'Natural gas',
            'Nuclear',
            'Hydro',
            'Wind, solar, etc.',
            'Biofuels and waste',
            'Electricity',
            'Heat'
            ]
        },
    'Electricity': {
        'Total production': [
            'Coal',
            'Oil',
            'Natural gas',
            'Biofuels',
            'Waste',
            'Nuclear',
            'Hydro',
            'Geothermal',
            'Solar PV',
            'Solar thermal',
            'Wind',
            'Tide',
            'Other sources',
            'Municipal Waste',
            'Waste (renewable)'
            ],
        'Intermediate use': [
            'Imports',
            'Exports',
            'Domestic supply',
            'Statistical differences',
            'Transformation',
            'Electricity plants',
            'Heat plants',
            'Energy industry own use',
            'Losses'
            ],
        'Final Consumption': [
            'Industry',
            'Transport',
            'Residential',
            'Commercial and public services',
            'Agriculture / forestry',
            'Fishing',
            'Other non-specified',
            'Other Renewables'
            ],
        },
    }


flow_commodity_map = {
    'Electricity': {
        'Coal': 'Coal',
        'Oil': 'Oil products',
        'Natural gas': 'Natural gas',
        'Biofuels': 'Biofuels and waste',
        'Waste': 'Biofuels and waste',
        'Nuclear': 'Nuclear',
        'Hydro': 'Hydro',
        'Geothermal': 'Wind, solar, etc.',
        'Solar PV': 'Wind, solar, etc.',
        'Solar thermal': 'Wind, solar, etc.',
        'Wind': 'Wind, solar, etc.',
        'Tide': 'Wind, solar, etc.',
        'Other sources': 'Wind, solar, etc.',
        'Municipal Waste': 'Biofuels and waste',
        'Waste (renewable)': 'Biofuels and waste',
        } 
    }


index_acts_dict = {
    'Mining': [
        'Coal',
        'Crude oil',
        'Natural gas',
        'Nuclear',
        ],
    'Electricity production': [
        'Coal',
        'Oil products',
        'Natural gas',
        'Nuclear',
        'Hydro',
        'Wind, solar, etc.',
        'Biofuels and waste',
        ],
    'Heat production': [
        'Coal',
        'Oil products',
        'Natural gas',
        'Nuclear',
        'Hydro',
        'Wind, solar, etc.',
        'Biofuels and waste',
        ],   
    'Biofuels and waste': [
        'Forestry and logging',
        'Waste treatment service',
        ],
    'Refinery': [
        'Coal transformation',
        'Oil refineries',
        'Gas works',
        'Liquefication plants',
        'Other transformation',
        ]
    }


index_find_dict = {
    'Total Final Consumption': [
        'Industry',
        'Transport',
        'Residential',
        'Commercial and public services',
        'Agriculture / forestry',
        'Fishing',
        'Non-specified',
        'Non-energy use',
        ],
    'Losses': [
        'Energy industry own use',
        'Losses',
        ],
    'Trades': [
        'Imports',
        'Exports',
        ],
    'Stocks': [
        'International marine bunkers',
        'International aviation bunkers',
        'Stock changes',
        ],
    'Stats and transfer': [
        'Transfers',
        'Statistical differences',
        ]
    }

index_sats = ['Coal','Crude oil','Natural gas','Nuclear','Hydro','Wind, solar, etc.','Biofuels and waste']


