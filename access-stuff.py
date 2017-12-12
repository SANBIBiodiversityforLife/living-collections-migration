# To get pandas working you have to pip install six
# and install numpy by downloading the whl from http://www.lfd.uci.edu/~gohlke/pythonlibs/ and pip installing the whl
import pandas as pd
import pypyodbc
import functions as f
import re

# This is the main path where the project files are
main_path = 'C:\\Users\\johaadienr\\Documents\\Projects\\brahms\\living-collections\\'

# I have cached the merged access tables because it takes forever to run this script, change this var to reload everything
load_from_cache = False

if not load_from_cache:
    print('Loading from access')
    # SQl query for everything accessions related
    sql = 'select tblaccession.casgdn, tblaccession.casyr, tblaccession.casno, tblaccession.casext, tblaccession.genno, ' \
          'tblaccession.spno, tblaccession.tmpname, tblaccession.donor, tblaccession.detby, tblaccession.detmn, ' \
          'tblaccession.detyr, tblaccession.spmnno, tblaccession.colldy, tblaccession.collmn, tblaccession.collyr, ' \
          'tblaccession.regioncode, tblaccession.gridref, tblaccession.latitude, tblaccession.latns, tblaccession.longitude, ' \
          'tblaccession.longew, tblaccession.horizconflevelcode, tblaccession.loc, tblaccession.alt, ' \
          'tblaccession.aspectcode, tblaccession.soilcode, tblaccession.substrcode, tblaccession.moisturecode, ' \
          'tblaccession.vegcode, tblaccession.newvegbiome, tblaccession.newvegbioregion, tblaccession.newvegveg, ' \
          'tblaccession.bioeffectcode, tblaccession.exposurecode, tblaccession.lithologycode, tblaccession.occurrencecode, ' \
          'tblaccession.ht, tblaccession.flowercode, tblaccession.fruitcode, tblaccession.fl_01, tblaccession.fl_02, ' \
          'tblaccession.fl_03, tblaccession.fl_04, tblaccession.fl_05, tblaccession.fl_06, tblaccession.fl_07, ' \
          'tblaccession.fl_08, tblaccession.fl_09, tblaccession.fl_10, tblaccession.fl_11, tblaccession.fl_12, ' \
          'tblaccession.fr_01, tblaccession.fr_02, tblaccession.fr_03, tblaccession.fr_04, tblaccession.fr_05, ' \
          'tblaccession.fr_06, tblaccession.fr_07, tblaccession.fr_08, tblaccession.fr_09, tblaccession.fr_10, ' \
          'tblaccession.fr_11, tblaccession.fr_12, tblaccession.flowerdescription, ' \
          'tblaccession.origincode, tblaccession.slopecode, tblaccession.landownership, tblaccession.landisconserved, ' \
          'tblaccession.notes as accessionnotes, tblaccession.generalnotes, tblaccessionflowercolour.flowercolour, ' \
          'tblaccessiongrowthform.grfrmcd, tblaccessionhabitat.habcd, tblaccessionmaterial.strmaterial, ' \
          'tblaccessionmaterial.intquantity, tblaccessionmaterial.notes as materialnotes, tblaccessionmaterialother.strmaterialother, ' \
          'tblaccessionmaterialother.notes as materialothernotes, tblspeciesdetailcache.keycomposite, tblspeciesdetailcache.famno, ' \
          'tblspeciesdetailcache.genno, tblspeciesdetailcache.spno, tblspeciesdetailcache.family, ' \
          'tblspeciesdetailcache.genus, tblspeciesdetailcache.spname, tblspeciesdetailcache.sspname, ' \
          'tblspeciesdetailcache.varname, tblspeciesdetailcache.othname, tblspeciesdetailcache.speciesdesc, ' \
          'tblspeciesdetailcache.curflg, tblspeciesdetailcache.countofaccessionid, tblspeciesdetailcache.national_fa_status,' \
          'tblaccession.accessionid, tblaccession.gardenspeciesid, tblgardenspecies.cultvr, tblgardenspecies.selecname,' \
          'tblgardenspecies.hybrdtls, tblgardenspecies.taxonnotes' \
          ' from ((((((tblaccession' \
          ' left join tblaccessionmaterial on tblaccession.accessionid = tblaccessionmaterial.accessionid)' \
          ' left join tblgardenspecies on tblaccession.gardenspeciesid = tblgardenspecies.gardenspeciesid)' \
          ' left join tblaccessionmaterialother on tblaccession.accessionid = tblaccessionmaterialother.accessionid)' \
          ' left join tblaccessionflowercolour on tblaccession.accessionid = tblaccessionflowercolour.accessionid)' \
          ' left join tblaccessiongrowthform on tblaccession.accessionid = tblaccessiongrowthform.accessionid)' \
          ' left join tblaccessionhabitat on tblaccession.accessionid = tblaccessionhabitat.accessionid)' \
          ' left join tblspeciesdetailcache on (tblaccession.genno = tblspeciesdetailcache.genno and ' \
          'tblaccession.spno = tblspeciesdetailcache.spno);'

    # Dealing with the collectors separately
    collectors_sql = 'select tblaccessioncollector.spmnno, tblaccessioncollector.accessionid, tblcollector.name, ' \
                     'tblcollector.maidenname, tblaccession.casgdn from ((tblaccessioncollector' \
                     ' left join tblcollector on tblaccessioncollector.collectorid = tblcollector.collectorid)' \
                     ' left join tblaccession on tblaccession.accessionid = tblaccessioncollector.accessionid);'

    # Accessions and collectors holding lists
    accessions = []
    collectors = []

    # Iterate through each of the garden dbs
    garden_folders = ['freestate', 'haroldporter', 'karoo', 'kirstenbosch', 'kwazulunatal', 'lowveld', 'pretoria', 'waltersisulu']
    for garden_folder in garden_folders:
        connection = pypyodbc.connect('Driver={Microsoft Access Driver (*.mdb)};DBQ=' + main_path + '\\gardens-november-2015\\'
                                      + garden_folder + '\\GA_garden.mdb;PWD=', )

        # Get the accessions
        results = pd.read_sql(sql, connection)
        print('coming up... this many duplicates of accession id ' + str(len(results[results.duplicated('accessionid')])))
        # Ok I don't know why this is happening frankly. Same thing happens if you execute sql in access
        # Left joins should not produce duplicates.
        # Apparently it can happen if there are duplicates... let's just drop the duplicates, who knows what they are
        results = results.drop_duplicates('accessionid')

        # Make sure each garden code is correct and generate a unique id
        results['casgdn'] = results['casgdn'].unique()[0]
        results['unique_a_id'] = results['casgdn'] + '_' + results['accessionid'].map(str)
        accessions.append(results)

        # Get the collectors
        collectors_results = pd.read_sql(collectors_sql, connection)
        collectors_results['casgdn'] = collectors_results['casgdn'].unique()[0]
        collectors_results['unique_a_id'] = collectors_results['casgdn'] + '_' + collectors_results['accessionid'].map(str)
        collectors.append(collectors_results)

        print(garden_folder + ' - accession records added:' + str(len(results)) + ' | collector records added: ' +
              str(len(collectors_results)))

    # Concatenate all the accessions & collectors
    accessions = pd.concat(accessions, ignore_index=True)
    accessions.fillna('')
    collectors = pd.concat(collectors, ignore_index=True)
    collectors.fillna('')

    # Rebuild the CSV cache
    accessions.to_pickle('cache_ac.pkl')
    collectors.to_pickle('cache_co.pkl')
else:
    print('Loading from cache file')
    accessions = pd.read_pickle(main_path + 'python\\cache_ac.pkl')
    collectors = pd.read_pickle(main_path + 'python\\cache_co.pkl')
    # collectors['name'] = str(collectors['name'])


print("Accessions concatenated! Total number : " + str(len(accessions)))
print("Collectors concatenated! Total number : " + str(len(collectors)))

'''
' Cleaning
'''

# Making copies
acold = accessions.copy()
oc = collectors.copy()

# Read in the latest brahms people table for collectors + detbys
brahms_people = pd.read_csv(main_path + 'python\\PEOPLE_02-10-2015_at_15-10-42.CSV')
brahms_people = brahms_people.fillna('')
brahms_people['SURNAME'] = brahms_people['SURNAME'].str.lower()
brahms_people['INITIALS'] = brahms_people['INITIALS'].str.lower()

# Cleaning the collectors (hellish)
collectors['original_name'] = collectors['name']
print('Cleaning collectors:')
collectors = f.clean_collectors(collectors)
print('Finished cleaning collectors:')

# Rename collector columns so they are proper
list(collectors)
renamed_columns = {'spmno': 'collections_number',
                   'maidenname': 'people_altname',
                   'name': 'people_surname',
                   'new_initials': 'people_initial',
                   'firstname': 'people_firstname'}
collectors.rename(columns=renamed_columns, inplace=True)

# Merge the fruiting & flowering months
accessions['merged_flowering_months'] = accessions.apply(f.concatenate_months, args=('fl',), axis=1)
accessions['merged_fruiting_months'] = accessions.apply(f.concatenate_months, args=('fr',), axis=1)

# Locations
accessions = f.clean_locations(main_path=main_path, accessions=accessions)

# Flower descriptions
accessions = f.clean_flower_descriptions(accessions)

# Determined by stuff
accessions['detby'] = accessions['detby'].astype('str')

# Some detbys are getting manually corrected by Hannelie
h_detbys = pd.read_csv(main_path + 'python\\weird_detbys.csv')
#to_drop = h_detbys.loc[h_detbys['Drop?'] == 'Y']
accessions = accessions.merge(h_detbys, left_on='detby', right_on='Name', how='left')
accessions.loc[accessions['Drop?'] == 'Y', 'detby'] = 'Unknown'
accessions.loc[pd.isnull(accessions['Drop?']) == False, 'detby'] = accessions.loc[pd.isnull(accessions['Drop?']) == False, 'Drop?']
del accessions['Drop?']
del accessions['Name']

# Save the original detby name because we use it later on when we overwrite detbys with a corrected csv from Hannelie
accessions['original_detby'] = accessions['detby']

# Detbys need to be turned into proper people
accessions['detby'].replace(to_replace="\(coll '79\)", value="", regex=True)
temp = accessions['detby']
detbys = pd.DataFrame(data={'name': temp, 'detby': temp})
detbys = f.clean_collectors(detbys, multiple_rows=False)

# Join detbys onto the current brahms people table
# Additional columns title         name new_initials   firstname
missing_detbys = pd.DataFrame(data={'original_name': detbys['detby'], 'people_surname': detbys['name'],
                                    'people_initial': detbys['new_initials'], 'people_firstname': detbys['firstname']})
missing_detbys.drop_duplicates(inplace=True, subset=['people_surname', 'people_initial'])
missing_detbys['people_surname'] = missing_detbys['people_surname'].str.lower()
missing_detbys['people_initial'] = missing_detbys['people_initial'].str.lower()
m_d = missing_detbys.merge(brahms_people, left_on=['people_surname', 'people_initial'], right_on=['SURNAME', 'INITIALS'], how='left')
m_d.loc[pd.isnull(m_d['SURNAME'])].drop_duplicates().to_csv('detbys_new.csv')

# Drop some columns
# accessions['detby'] = accessions['name'] + ', ' + accessions['new_initials']
# detbys.drop(['name', 'new_initials', 'firstname', 'title'], axis=1, inplace=True)

# Merge the detbys back into the accessions table
accessions['detby'] = detbys['name'].map(str) + ', ' + detbys['new_initials'].map(str)

# Hannelie has sent the corrected detbys over, overwrite all work done on detbys previously
h_detbys = pd.read_csv(main_path + 'python\\detbys_new_fixed.csv')
accessions = accessions.merge(h_detbys, left_on='original_detby', right_on='original_name', how='left')

# For the ones she has told us to drop, put Unknown
accessions.loc[accessions['DROP'] == 'Yes', 'detby'] = 'Unknown'
accessions.drop(['DROP', 'original_detby', 'row'], axis=1, inplace=True)

# Join with the people table and get the proper person's name
accessions = accessions.merge(brahms_people, left_on='BRAHMSNUMBER', right_on='ID', how='left')
accessions.loc[pd.isnull(accessions['BRAHMSNUMBER']) == False, 'detby'] = \
    accessions.loc[pd.isnull(accessions['BRAHMSNUMBER']) == False, 'SURNAME'].map(str) + ', ' + \
    accessions.loc[pd.isnull(accessions['BRAHMSNUMBER']) == False, 'INITIALS'].map(str)
accessions.drop(['BRAHMSNUMBER', 'SURNAME', 'INITIALS', 'FIRST'], axis=1, inplace=True)

# Plant names
accessions = f.clean_plant_names(main_path=main_path, accessions=accessions)
accessions.drop(['genno', 'spno'], axis=1, inplace=True)

# Fix rank1 for ssp and var
accessions['rank1'] = ''
accessions['sp2'] = ''
accessions.loc[pd.isnull(accessions['sspname']) == False, 'rank1'] = 'subsp.'
accessions.loc[pd.isnull(accessions['varname']) == False, 'rank1'] = 'var.'
accessions.loc[pd.isnull(accessions['sspname']) == False, 'sp2'] = accessions.loc[pd.isnull(accessions['sspname']) == False, 'sspname']
accessions.loc[pd.isnull(accessions['sspname']) == False, 'sp2'] = accessions.loc[pd.isnull(accessions['sspname']) == False, 'varname']
del accessions['sspname']
del accessions['varname']

print("Non BRAHMS plant names cleaned up! Total number of accessions: " + str(len(accessions)))

'''
' Joining collectors
'''

# Hannelie has provided a partially-complete list of collectors that should be renamed
hc = pd.read_csv(main_path + 'python\\hannelie_corrected_collectors.csv')
hc = hc.fillna('')
c = collectors.copy()

# Join H's list to the BRAHMS people table using the brahmsnumber hannelie has input
hcb = hc.copy()  # hc[pd.isnull(hc['brahmsnumber']) == False]
hcb['test_h'] = hcb['people_surname'].str.lower() + '_' + hcb['people_initial'].str.lower()
brahms_people['test_b'] = brahms_people['SURNAME'].str.lower() + '_' + brahms_people['INITIALS'].str.lower()
hcb = hcb.merge(brahms_people, left_on='brahmsnumber', right_on='ID', how='left')

# To stop us getting confused, we now only need cases where the brahms surname & initial does not equal the c surname & initial
# changed = hcb.loc[(hcb['test_h'] != hcb['test_b']) & (pd.isnull(hcb['test_b']) == False)]
changed = hcb.copy()

# Join it up to the collectors based on the incorrect/out of date surname + initial (test_h)
c['test_c'] = c['people_surname'].str.lower() + '_' + c['people_initial'].str.lower().str.lower()
nc = c.merge(changed, left_on='test_c', right_on='test_h', how='left')

# Ok, now where we have a correction to the name + surname + initial we need to replace the details in the collector file
nc.loc[pd.isnull(nc['SURNAME']) == False, ['SURNAME', 'INITIALS', 'people_surname_x', 'people_initial_x']]  # Just taking a look...
nc.loc[pd.isnull(nc['SURNAME']) == False, 'people_surname_x'] = nc.loc[pd.isnull(nc['SURNAME']) == False, 'SURNAME']
nc.loc[pd.isnull(nc['SURNAME']) == False, 'people_initial_x'] = nc.loc[pd.isnull(nc['SURNAME']) == False, 'INITIALS']
nc.loc[pd.isnull(nc['SURNAME']) == False, 'people_firstname_x'] = nc.loc[pd.isnull(nc['SURNAME']) == False, 'FIRST']

# Now we can drop all the unecessary columns and rename the _x ones
nc.drop(['test_c', 'ugh', 'spmnno_y', 'accessionid_y', 'people_altname_y', 'casgdn_y', 'unique_a_id_y', 'people_surname_y', 'people_initial_y',
         'people_firstname_y', 'brahmsnumber', 'test_h', 'ID', 'SURNAME', 'INITIALS', 'FIRST', 'test_b'], axis=1, inplace=True)
nc.columns = ['spmnno', 'accessionid', 'people_altname', 'casgdn', 'unique_a_id', 'original_name', 'title', 'people_surname', 'people_initial', 'people_firstname']

# We now have a list of collectors nc with H's corrections. Now we must find collectors who are not in the brahms people table
missing_collectors = nc.copy()
missing_collectors.drop_duplicates(inplace=True, subset=['people_surname', 'people_initial'])
missing_collectors['people_surname'] = missing_collectors['people_surname'].str.lower()
missing_collectors['people_initial'] = missing_collectors['people_initial'].str.lower()
brahms_people['SURNAME'] = brahms_people['SURNAME'].str.lower()
brahms_people['INITIALS'] = brahms_people['INITIALS'].str.lower()
surname_collectors = missing_collectors.merge(brahms_people, left_on=['people_surname', 'people_initial'], right_on=['SURNAME', 'INITIALS'], how='left')
surname_collectors.loc[pd.isnull(surname_collectors['SURNAME'])].drop_duplicates().to_csv('surname_collectors_new.csv')
# s_c = missing_collectors.merge(brahms_people, left_on='people_surname', right_on='SURNAME', how='left')

# Collectors currently are like this:
# KBG-21345 John Doe
# KBG-21345 Jane Doe
# KBG-21346 Whoever Else
# And we need to make John Doe and Jane Doe be on the same line like this Doe, John; Doe, Jane
# single_line_collectors = collectors.copy()
single_line_collectors = nc.copy()
single_line_collectors['name'] = single_line_collectors['people_surname'].map(str) + ', ' + single_line_collectors['people_initial'].map(str)
single_line_collectors['name'].replace(to_replace=', $', value='', regex=True, inplace=True)
single_line_collectors.drop(['people_altname', 'people_initial', 'people_firstname', 'people_surname'], axis=1, inplace=True)
grouped = single_line_collectors.groupby(single_line_collectors.unique_a_id).apply(lambda x: '; '.join(x['name'].map(str)))
grouped.name = 'collectors'

# Now we can merge these grouped collectors with accessions
ac = accessions.join(grouped, on='unique_a_id')

# Clean up provtype/origincode
ac.loc[ac['origincode'] == 'From wild', 'origincode'] = 'W'  # Accession of wild source
ac.loc[ac['origincode'] == 'Ex hort', 'origincode'] = 'G'  # Accession not of wild source
ac.loc[ac['origincode'] == 'Unknown', 'origincode'] = 'U'  # Insufficient data to determine which of the above categories apply
ac.loc[ac['origincode'] == '  Not recorded', 'origincode'] = 'U'  # Insufficient data to determine which of the above categories apply
ac.loc[ac['origincode'] == '    See Notes', 'origincode'] = 'U'  # Insufficient data to determine which of the above categories apply
ac.loc[ac['origincode'] == ' See Notes', 'origincode'] = 'U'  # Insufficient data to determine which of the above categories apply

'''
' Cleaning up the columns
'''

# These go in the accession id, so make it and drop them except for the year
ac['accession'] = ac['casgdn'].map(str) + '-' + ac['casno'].map(str) + '-' + ac['casyr'].map(str)
ac['recyy'] = ac['casyr']
ac.drop(['casgdn', 'casyr', 'casno', 'casext'], axis=1, inplace=True)

# Change collectors to collector
ac['collector'] = ac['collectors']
del ac['collectors']

# Species stuff
renamed_columns = {'spname': 'sp1'}
ac.rename(columns=renamed_columns, inplace=True)

# hs and gaz prefixes
renamed_columns = {'spmnno': 'number',  # hs prefix
                    'colldy': 'colldd',  # hs prefix
                    'collmn': 'collmm',  # hs prefix
                    'collyr': 'collyy',  # hs prefix
                    #'gaz.coname': 'conumber',  # gaz prefix, used to be regioncode
                    'gaz.major': 'majorarea',  # doesn't seem to be in the list for some reason
                    'gridref': 'qds',  # hs prefix
                    'latitude': 'lat',  # hs prefix
                    'latns': 'ns',  # hs prefix
                    'longitude': 'long',  # hs prefix
                    'longew': 'ew',  # hs prefix
                    'horizconflevelcode': 'llres',  # hs prefix
                    'loc': 'locnotes'}  # gaz prefix
ac.rename(columns=renamed_columns, inplace=True)

renamed_columns = {#'tmpname': 'receivedas', 2016/01/15 - removing because we need to add cultivar etc stuff in here too, see functions
                    'gaz.major': 'majorarea',
                    'donor': 'donornote',
                    'detby': 'detby',
                    'detmn': 'detmm',
                    'detyr': 'detyy',
                    'aspectcode': 'asp',
                    'soilcode': 'soilcd',
                    'substrcode': 'substrcd',
                    'moisturecode': 'mstcd',
                    'vegcode': 'vegcd',
                    'newvegbiome': 'nwvgbme',
                    'newvegbioregion': 'nwvgbrgn',
                    'newvegveg': 'newvgvg',
                    'bioeffectcode': 'bioeffcd',
                    'exposurecode': 'exposcd',
                    'lithologycode': 'lithcd',
                    'occurrencecode': 'occrcd',
                    'ht': 'ht',
                    'flowercode': 'flrcd',
                    'merged_flowering_months': 'flwrmnth',
                    'merged_fruiting_months': 'frtmnth',
                    'fruitcode': 'frtcd',
                    'flowerdescription': 'flwrdscrip',
                    'origincode': 'provtype',
                    'slopecode': 'slope',
                    'landownership': 'lndwnrtype',
                    'landisconserved': 'iscons',
                    'notes': 'taxonnotes',
                    'generalnotes': 'originnote',
                    'spmnno': 'number',
                    'flowercolour': 'flclrs',
                    #'grfrmcd': 'habit', # sp prefix
                    'habcd': 'habitattxt',
                    'strmaterial': 'suppliedas',
                    'intquantity': 'quantity',
                    'strmaterialother': 'name',  # cc prefix
                    'materialothernotes': 'ihcode'}  # ih prefix
ac.rename(columns=renamed_columns, inplace=True)

# 22/01/2016 specimen and ihcode (strmaterialother + materialothernotes) need to get appended to generalnotes
ac.loc[pd.isnull(ac['name']) == False, 'originnote'] = \
    ac.loc[pd.isnull(ac['name']) == False, 'originnote'].map(str) + ' Herbarium specimen: ' + \
    ac.loc[pd.isnull(ac['name']) == False, 'name'].map(str)
ac.loc[pd.isnull(ac['ihcode']) == False, 'originnote'] = \
    ac.loc[pd.isnull(ac['ihcode']) == False, 'originnote'].map(str) + ' Specimen notes: ' + \
    ac.loc[pd.isnull(ac['ihcode']) == False, 'ihcode'].map(str)

# These two have to concatenate
ac.loc[pd.isnull(ac['materialnotes']) == False, 'donornote'] = \
    ac.loc[pd.isnull(ac['materialnotes']) == False, 'donornote'].map(str) + ' - material notes: ' + \
    ac.loc[pd.isnull(ac['materialnotes']) == False, 'materialnotes'].map(str)
# ac['donornote'] = ac['donornote'].map(str) + ' - material notes: ' + ac['materialnotes'].map(str)
del ac['materialnotes']

# Double checking...
required_cols = pd.read_csv(main_path + 'python27\\structure.csv')
required_cols = list(required_cols['name'])
print(list(ac))
print([obj for obj in list(ac) if obj not in required_cols])
print([obj for obj in required_cols if obj not in list(ac)])
ac.drop([obj for obj in list(ac) if obj not in required_cols], axis=1, inplace=True)

ac.loc[ac['recyy'] > 2015, 'recyy'] = 2015
print('about to enter try')
try:
    # 292 cases where colyy does not precede or equal accessionyear (recyy) when we have a sensible casyr, so set them as casyr
    #ac['collyy'] = ac['collyy'].map('int')
    ac.loc[(ac['collyy'] > ac['recyy']) & (ac['recyy'] > 999), ['collyy', 'recyy']]
    ac.loc[(ac['collyy'] > ac['recyy']) & (ac['recyy'] > 999), 'collyy'] = ac.loc[(ac['collyy'] > ac['recyy']) & (ac['recyy'] > 999), 'recyy']

    # Now we have to clean up the once off cases which break the dbf maker or BRAHMS import thing
    ac.loc[ac['collyy'] == 20152, 'collyy'] = 2015
    ac.loc[ac['collyy'] == 20002, 'collyy'] = 2002
    ac.loc[ac['collyy'] == 19982, 'collyy'] = 1982
    ac.loc[ac['collyy'] == 19990, 'collyy'] = 1999
    ac.loc[ac['collyy'] == 2023, 'collyy'] = 2013
    ac.loc[ac['collyy'] == 3013, 'collyy'] = 2013
    ac.loc[ac['collyy'] == 2103, 'collyy'] = 2013
    ac.loc[ac['collyy'] == 2017, 'collyy'] = 2007
    ac.loc[ac['collyy'] == 2018, 'collyy'] = 2008
    ac.loc[ac['collyy'] == 2978, 'collyy'] = 1978
    ac.loc[ac['colldd'] == 183, 'colldd'] = 18
    ac.loc[ac['colldd'] == 39, 'colldd'] = 29
    ac.loc[ac['collmm'] == 111, 'collmm'] = 11
    ac.loc[ac['collmm'] == 110, 'collmm'] = 10
    ac.loc[ac['collmm'] == 31, 'collmm'] = 11
    # 32 14 22
    ac.loc[ac['collmm'] > 12, 'collmm'] = 12
    ac.loc[ac['collmm'] == 20, 'collmm'] = 2

    ac.loc[ac['alt'] < 0, 'alt'] = 0
    # ac.loc[ac['alt'] > 3500, 'alt'] = 9999
    ac.loc[ac['lat'] < 0, 'ns'] = 'S'
    ac.loc[ac['lat'] >= 0, 'ns'] = 'N'
    ac.loc[ac['long'] < 0, 'long'] = ac.loc[ac['long'] < 0] * -1
    ac.loc[ac['lat'] < 0, 'lat'] = ac.loc[ac['lat'] < 0] * -1


    # RIGHT! Now we have all the columns, correctly named, we need to make a huuuuuuuge CSV


    # Make everything blank = wild
    ac.loc[pd.isnull(ac['provtype']) == True, 'provtype'] = 'W'

    # S has asked recyy to be 0
    ac['recyy'] = 0

    print('making csv')
    ac.to_csv(main_path + 'python27\\ac.csv')
except Exception as inst:
    print(inst)

print('finished')