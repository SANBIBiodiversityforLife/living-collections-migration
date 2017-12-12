# To get pandas working you have to pip install six
# and install numpy by downloading the whl from http://www.lfd.uci.edu/~gohlke/pythonlibs/ and pip installing the whl
import pandas as pd
import pypyodbc
from datetime import datetime
import functions as f
import re

# This is the main path where the project files are
main_path = 'C:\\Users\\johaadienr\\Documents\\Projects\\brahms\\living-collections\\'

# I have cached the merged access tables because it takes forever to run this script, change this var to reload everything
load_from_cache = False

if not load_from_cache:
    print('Loading from access')
    # SQl query for everything plantings related
    sql = 'select tblplanting.plantingid, tblbed.strbedgroup, tblplanting.accessionid, ' \
          'tblbed.strbed, tblplanting.strmaterial,' \
          'tblplanting.dteplanted, tblplanting.strunits, tblplanting.intquantity, tblplanting.dtedied, ' \
          'tblplanting.notes, tblaccession.casgdn, tblaccession.casyr, tblaccession.casno ' \
          'from ((tblplanting ' \
          'left join tblaccession on tblplanting.accessionid = tblaccession.accessionid)' \
          'left join tblbed on tblbed.bedid = tblplanting.bedid);'

    # Plantings
    plantings = []

    # Iterate through each of the garden dbs
    garden_folders = ['freestate', 'haroldporter', 'karoo', 'kirstenbosch', 'kwazulunatal', 'lowveld', 'pretoria', 'waltersisulu']
    for garden_folder in garden_folders:
        connection = pypyodbc.connect('Driver={Microsoft Access Driver (*.mdb)};DBQ=' + main_path + '\\gardens-november-2015\\'
                                      + garden_folder + '\\GA_garden.mdb;PWD=sanbi_gardens', )

        # Get the plantings
        results = pd.read_sql(sql, connection)
        plantings.append(results)

        # Print out the counter
        print(garden_folder + ' - planting records added:' + str(len(results)))

    # Concatenate all the accessions & collectors
    plantings = pd.concat(plantings, ignore_index=True)
    plantings.fillna('')

    # Rebuild the CSV cache
    plantings.to_pickle('cache_p.pkl')
else:
    print('Loading from cache file')
    plantings = pd.read_pickle(main_path + 'python\\cache_p.pkl')

print("Plantings concatenated! Total number : " + str(len(plantings)))

# Keep a copy of the original
pl = plantings.copy()

# We need to link these up to accessions using the generated accession id, so gen one for plantings too
pl['accession'] = pl['casgdn'].map(str) + '-' + pl['casno'].map(str) + '-' + pl['casyr'].map(str)
pl.drop(['accessionid', 'casyr', 'casno'], axis=1, inplace=True)

# Mad dates must be made sensible, looks like 1006-06-14 00:00:00
pl.loc[pl['dteplanted'] < datetime(1927, 1, 1, 0, 0, 0, 0), 'dteplanted'] = datetime(2006, 6, 14, 0, 0, 0, 0)

# Ok now for every unique accession id we need to assign a new planting number from 1 to x based on planting date
# So order by planting date asc then order by accession
pl = pl.sort(columns=['accession', 'dteplanted'])
# pl = pl[20:40]
#pl = pl.sort(columns=['accession'])

pl['pid'] = 1
previous_pid = 1
pl['previous_accession'] = pl['accession'].shift(1)

for index, row in pl.iterrows():
    if row.previous_accession == row.accession:
        pl.loc[index, 'pid'] = previous_pid + 1
        previous_pid += 1
    else:
        pl.loc[index, 'pid'] = 1
        previous_pid = 1

pl['plantid'] = pl['accession'] + '*' + pl['pid'].map(str)

pl['plantdd'] = 0
pl['plantmm'] = 0
pl['plantyy'] = 0

try:
    pl.loc[pd.isnull(pl['dteplanted']) == False, 'plantdd'] = pl.loc[pd.isnull(pl['dteplanted']) == False, 'dteplanted'].map(lambda x: x.strftime("%d"))
except ValueError as err:
    print(err)

pl.loc[pd.isnull(pl['dteplanted']) == False, 'plantdd'] = pl.loc[pd.isnull(pl['dteplanted']) == False, 'dteplanted'].map(lambda x: x.strftime("%d"))
pl.loc[pd.isnull(pl['dteplanted']) == False, 'plantmm'] = pl.loc[pd.isnull(pl['dteplanted']) == False, 'dteplanted'].map(lambda x: x.strftime("%m"))
pl.loc[pd.isnull(pl['dteplanted']) == False, 'plantyy'] = pl.loc[pd.isnull(pl['dteplanted']) == False, 'dteplanted'].map(lambda x: x.strftime("%Y"))
pl.loc[pd.isnull(pl['dtedied']) == False, 'lossdd'] = pl.loc[pd.isnull(pl['dtedied']) == False, 'dtedied'].map(lambda x: x.strftime("%d"))
pl.loc[pd.isnull(pl['dtedied']) == False, 'lossmm'] = pl.loc[pd.isnull(pl['dtedied']) == False, 'dtedied'].map(lambda x: x.strftime("%m"))
pl.loc[pd.isnull(pl['dtedied']) == False, 'lossyy'] = pl.loc[pd.isnull(pl['dtedied']) == False, 'dtedied'].map(lambda x: x.strftime("%Y"))


pl.drop(['plantingid', 'previous_accession', 'pid', 'dteplanted', 'dtedied'], axis=1, inplace=True)

# Strunits was supposed to go into 'layout' but I can't work out why so dropping for now
del pl['strunits']

structure = {'strbed': 'bed',
             'casgdn': 'bglocation',  # planted as
             'strbedgroup': 'gardenloc',  # planted as
             'strmaterial': 'plantedas',  # planted as / materfrom 22/01/2016 changed this to plantedas
             'intquantity': 'plantcount',  # Could also  be intquantity? # NOTE changed to plantcount # NOTE why changed? Changed it back to intquantity
             'notes': 'lossnotes'}
pl.rename(columns=structure, inplace=True)

# Print to csv
pl.to_csv(main_path + 'python27\\pl.csv')

print('fin')
#p = pl.copy()
# pl = pl[0:10]

#t = pl.copy()
#test = t.groupby('accession')

# So we are going to say, if the previous accession is different then make it 1, otherwise make it 1 + the previous number
# Store the previous accession number
# pl['previous_accession'] = pl['accession'].shift(1)

#def set_new_planting_id(group):
#    print(group.grouper.indices)
#    return group

#test = pl.groupby('accession').apply(set_new_planting_id)


#grouped = pl.groupby('accession')

#for name, group in grouped:
#    i = 1
#    for item in group:
#        item['pid'] = i
#        i += 1

#print(.grouper)

#pl.loc[:, 'new_pid'] = pl.apply(lambda x: x['previous_accession'] + 1 if x['accession'].shift(1) == x['accession'] else 1, axis=1)

#pl.loc[:, 'new_pid'] = pl.apply(calculate_pid, args=(   )

#unique_accessions = pl['accession'].unique()

