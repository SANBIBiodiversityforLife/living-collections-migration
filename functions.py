import pandas as pd
import re

'''
' Collectors... yikes.
'''
def clean_collectors(cs, multiple_rows=True):
    # We have names with different patterns that we have to handle
    # Firstname [initials]?.? Surname
    # Surname, Firstname [initial]?.?
    # Surname [initials].
    # NAME (presumably surname)
    # [initials].Surname

    # Find all the titles that we can - note that sometimes they are in brackets
    titles_regex = '(mr?s|mr|misse?s?|dr|rev|prof\.?|messrs|professor|esq|lady|sir|officer|sister|brother|doctor|' \
            'captain|sergeant|archdeacon|major|madame|curator|senator|sen\.hon\.|st\.|lady\s+dow\.|br\.)'
    regex = '(^|\s+)\(?' + titles_regex + '([\)\s\.,]|$)\)?' # The end \) is to get rid of Mrs.) type things
    regex = re.compile(regex, re.IGNORECASE)

    # Extract the titles and insert into a titles column
    #print(cs['name'].str.extract(regex)[1].unique())
    cs['title'] = cs['name'].str.extract(regex)[1]

    # TODO standardise the titles with Brenda's CSV
    titles = ['Sir', 'Mrs', 'Miss', 'Dr.', 'Rev.', 'Mlle', 'Prof.', 'Mme', 'Jr.', 'Rear-Adm.', 'Second Lt.', 'Mr.', 'Sister', 'Fr.', 'Ms.', 'Earl of', 'Baron', 'Capt.', 'Brig.-Gen.', 'Mr.  Mrs.', 'Brother', 'Lord', 'Frere', 'Prof. Dr.', 'Major', 'Comm.', 'Admiral', 'Pater', 'Abbe', 'Pere', 'Esq.', 'Lady', 'Sen. Hon.', 'Messrs']

    # Remove the titles in the names
    cs['name'] = cs.apply(lambda x: regex.sub('', x['name']), axis=1)

    # List all of the stuff in brackets
    #print(cs[cs['name'].str.contains('[\(\)]')]['name'].unique())

    # \s&\sCo\. and ,\s+jr$ and & Son replace
    cs['name'].replace(to_replace='\s+&\s+Co\.?', value=' ', regex=True, inplace=True)
    cs['name'].replace(to_replace=',\s+jr$', value=' ', regex=True, inplace=True)
    cs['name'].replace(to_replace='\s+&\s+[sS]on', value=' ', regex=True, inplace=True)

    # Get rid of dates, they are useless
    cs['name'].replace(to_replace='\s*\([\d\-\s]+\)\s*', value='', regex=True, inplace=True)
    cs['name'].replace(to_replace='\?', value='', regex=True, inplace=True)
    cs['name'].replace(to_replace='[\(\)]', value='', regex=True, inplace=True)

    # Some strings we want to remove
    cs['name'].replace(to_replace='[pP]ietermaritzburg', value='', regex=True, inplace=True)

    # Let's do a little bit of standardisation to make things easier

    # Now we have a lot of "the" from "the captain" or whatever, so ...
    cs['name'].replace(to_replace='(^|\s+)[tT]he(\s|$)', value='', regex=True, inplace=True)

    # Remove all double spaces and replace with singles
    cs['name'].replace(to_replace='\s+', value=' ', regex=True, inplace=True)

    # Sometimes a string ends with a comma for no reason, get rid of it
    cs['name'].replace(to_replace='\s*[\.,]\s*$', value='', regex=True, inplace=True)

    # NBG turns into 'NBG Expedition' before we do the next set
    cs.loc[cs['name'] == 'NBG', 'name'] = 'NBG Expedition'

    # We now have some really cryptic cs eg "AB" that nobody knows who they are, so set them to Unknown
    cs.loc[(cs['name'].str.len() < 4)]['name'].unique()
    cs.loc[(cs['name'].str.len() < 4) &
                   (cs['name'].str.contains('Nel|Uys|Vos|Bok|Bar|Val|Key', case=False) == False), 'name'] = 'Unknown'
    cs.loc[cs['name'] == 'Donation by Mrs X.', 'name'] = 'Unknown'

    # All the anonymous type names are going to be stored as names in the surname field in the people table, as agreed
    # We don't know who 'the director', 'administrator', 'magistrate', 'Cons. Of Forests' are
    # or 'native comissioner' or 'unknown' or 'collector' or 'forests'
    regex = '(donor|director|unknown|administrator|native\s+commissioner|magistrate|forests?|collector|station\s+master)'
    #print(cs[cs['name'].str.contains(regex, case=False)]['name'].unique())
    cs.loc[cs['name'].str.contains(regex, case=False), 'name'] = \
        cs.loc[cs['name'].str.contains(regex, case=False), 'name'].replace(to_replace='[\.,\(\)]', value='', regex=True)
    cs.loc[cs['name'].str.contains(regex, case=False), 'name'] = \
        cs.loc[cs['name'].str.contains(regex, case=False), 'name'].replace(to_replace='\s+', value='xx', regex=True)

    # All of the gardens & nurseries & expeditions will get put in the surname field in the people table and need to be standardised
    regex = '(ex\short|research|arboretum|harbour|city|municipality|conservator|school|corporation|organisation|consulate|' \
            'laboratory|kirstenbosch|council|nursery|botanic|garden|expdtn|expedition|museum|university|univ\.|uct|dept|dpt|\sparks\s|durban|' \
            'pretoria|convent|kew\s+garden|of\s+forests|\s+club(\s+|$)|group|botany|division|[Ss]urvey|services|nat\.?\sres\.?|herb(\.|$)|' \
            'company|seeds|donor|nature\sreserve|farmers assoc|department|district|forest|conservation|nature|herbarium|bot\sgdn|seed)'
    #print(cs[cs['name'].str.contains(regex, case=False)]['name'].unique())
    cs.loc[cs['name'].str.contains(regex, case=False), 'name'] = \
        cs.loc[cs['name'].str.contains(regex, case=False), 'name'].replace(to_replace='[\.,\(\)]', value='', regex=True)
    cs.loc[cs['name'].str.contains(regex, case=False), 'name'] = \
        cs.loc[cs['name'].str.contains(regex, case=False), 'name'].replace(to_replace='\s+', value='xx', regex=True)

    # cs = cs[cs['name'].str.contains(regex, case=False) == False] - Do not drop

    # Ok now we need to look for Van De Wyk type surnames and concatenate them with xx temporarily
    regex = '(^|[\s\.])(v[ao]n)\s+((de[rn]?)?)\s*([a-z]+)'
    cs[cs['name'].str.contains(regex, case=False)]['name'].unique()
    regex = re.compile(regex, re.IGNORECASE)
    cs['name'] = cs.apply(lambda x: regex.sub(r'\g<1>\g<2>xx\g<3>xx\g<5>', x['name']), axis=1)

    # Do the De Waal/Du Plessis surnames separately to make the regex simpler
    regex = '(\s|^)(d[aeu])\s([a-z]+)'
    cs[cs['name'].str.contains(regex, case=False)]['name'].unique()
    regex = re.compile(regex, re.IGNORECASE)
    cs['name'] = cs.apply(lambda x: regex.sub(r'\g<1>\g<2>xx\g<3>', x['name']), axis=1)

    # Last pesky one to take care of
    cs['name'].replace(to_replace='De la Bat', value='DexxlaxxBat', inplace=True)

    if multiple_rows:
        # Ampersands have to be turned into multiple rows, luckily there only seem to be &s.
        cs[cs['name'].str.contains('(\s+and\s+|&)', case=False)]['name'].unique()

        # See http://stackoverflow.com/questions/17116814/pandas-how-do-i-split-text-in-a-column-into-multiple-rows
        # Simple test first
        simple = cs[cs['name'].str.contains('&', case=False)][0:5]
        s = simple['name'].str.split('&').apply(pd.Series, 1).stack()
        s.index = s.index.droplevel(-1)
        s.name = 'name'
        del simple['name']
        simple = simple.join(s)

        # Ok that seems to work... let's go for it
        split_cs = cs['name'].str.split('&').apply(pd.Series, 1).stack()
        split_cs.index = split_cs.index.droplevel(-1)
        split_cs.name = 'name'
        del cs['name']
        cs = cs.join(split_cs)

    # Get rid of the trailing spaces
    cs['name'].replace(to_replace='(^\s+|\s+$)', value='', regex=True, inplace=True)

    # Starting the initials! First get rid of the annoying 3
    cs['name'].replace(to_replace=',\s+M-J', value=', M.J.', regex=True, inplace=True)
    cs['name'].replace(to_replace=',\s+H-J', value=', H.J.', regex=True, inplace=True)
    cs['name'].replace(to_replace=',\s+J-G', value=', J.G.', regex=True, inplace=True)

    # Look for e.g. J.B.Smith or J B Smith or J. B. Smith, and then remove them from name
    regex = '^(([A-Za-z][\.\s]\s*)+)'
    cs['new_initials'] = cs.name.str.extract(regex)[0]
    cs['name'].replace(to_replace=regex, value='', regex=True, inplace=True)

    # Look for e.g. Smith J.B. or Smith J.B, and then remove them from name (don't overwrite previous initials)
    regex = ',?[\s\.](([A-Za-z]\.\s*)*[A-Za-z]?)$'
    cs.loc[pd.isnull(cs.new_initials), 'new_initials'] = cs.loc[pd.isnull(cs.new_initials), 'name'].str.extract(regex)[0]
    cs['name'].replace(to_replace=regex, value='', regex=True, inplace=True)

    # One surname is left which is clearly an initial, let's get rid of this guy
    cs.loc[(cs['name'].str.len() < 4) & (pd.isnull(cs['new_initials']) == False)]['name'].unique()
    cs = cs[cs['name'] != 'M']

    # If there are any I. type initials in the middle of the name string shove it in the initials
    regex = '(?=[a-zA-Z])\s+(([a-zA-Z][\s|\.])+)\s*(?=[a-zA-Z]+)'
    cs.loc[pd.isnull(cs.new_initials), 'new_initials'] = cs.loc[pd.isnull(cs.new_initials),
                                                                                        'name'].str.extract(regex)[0]
    cs['name'].replace(to_replace=regex, value='', regex=True, inplace=True)

    # Check to see what .s there are left
    cs[cs['name'].str.contains('\.')]['name'].unique()
    cs['name'].replace(to_replace='\.', value=' ', regex=True, inplace=True)

    # If we have any commas they are probably surname and firstname(s)/initials (search for capital letters first)
    regex = '([^,]+),\s*([A-Z\s\.]+)'
    cs.loc[cs['name'].str.contains(','), 'new_initials'] = \
        cs[cs['name'].str.contains(',')]['name'].str.extract(regex)[1]
    cs.loc[cs['name'].str.contains(','), 'name'] = \
        cs[cs['name'].str.contains(',')]['name'].str.extract(regex)[0]

    # Things start complaining about NAs, so stick this in
    cs.fillna('', inplace=True)

    # Now search for names (capital letter followed by lowercase letters)
    regex = '([^,]+),\s*([A-Z][a-z]+)'
    cs.loc[cs['name'].str.contains(','), 'firstname'] = \
        cs.loc[cs['name'].str.contains(','), 'name'].str.extract(regex)[1]
    cs.loc[cs['name'].str.contains(','), 'name'] = \
        cs.loc[cs['name'].str.contains(',')]['name'].str.extract(regex)[0]

    # Finally! We can tackle William Peter Uprichard Jackson and John Ward-Hilton types, i.e. firstnames!
    # test = pd.DataFrame({'name': ['John Ward-Hilton', 'William Peter Uprichard Jackson']})
    regex = '(([^\s]+\s+)+)'
    cs.loc[:, 'firstname'] = cs['name'].str.extract(regex)[0]
    cs['name'].replace(to_replace=regex, value='', regex=True, inplace=True)

    # Undo the xx's for van der type surnames
    cs['name'].replace(to_replace='xxxx', value=' ', inplace=True, regex=True)
    cs['name'].replace(to_replace='xx', value=' ', inplace=True, regex=True)

    # Some of these I am just fixing manually
    cs.loc[cs['firstname'] == 'Hilhorst', 'name'] = 'Hilhorst'
    cs.loc[cs['firstname'] == 'Hilhorst', 'firstname'] = ''
    cs.loc[cs['firstname'] == 'Davies', 'name'] = 'Davies'
    cs.loc[cs['firstname'] == 'Davies', 'firstname'] = ''
    cs.loc[cs['firstname'] == 'Esterhuizen', 'name'] = 'Esterhuizen'
    cs.loc[cs['firstname'] == 'Esterhuizen', 'firstname'] = ''
    cs.loc[cs['firstname'] == 'McQuillan', 'name'] = 'McQuillan'
    cs.loc[cs['firstname'] == 'McQuillan', 'firstname'] = 'Monique'
    # Can't find De Wet Bosenberg

    # We now need to insert initials where there are none
    cs['firstname'].replace(to_replace=',', value='', inplace=True)
    cs.loc[:, 'new_initials'] = cs['new_initials'].map(str)
    cs.loc[:, 'firstname'] = cs['firstname'].map(str)
    cs.loc[cs['new_initials'] == '', 'new_initials'] = \
        cs.loc[cs['new_initials'] == ''].apply(lambda x: ''.join(re.findall('[A-Z]', x['firstname'])), axis=1)
    cs['new_initials'].replace(to_replace='(\.|\s+)', value='', regex=True, inplace=True)

    # Get rid of the trailing spaces
    cs['name'].replace(to_replace='(^\s+|\s+$)', value='', regex=True, inplace=True)
    cs['firstname'].replace(to_replace='(^\s+|\s+$)', value='', regex=True, inplace=True)
    cs['new_initials'].replace(to_replace='(^\s+|\s+$)', value='', regex=True, inplace=True)

    # Get rid of the nans! Don't know how to make these go away...
    cs['firstname'].replace(to_replace='nan', value='', regex=False, inplace=True)

    return cs



'''
' Merging the fruiting & flowering concatenated months
'''
def concatenate_months(row, prefix):
    months = []

    # This is a list of the flowering month columns in excel
    month_columns = {'_01': 'January', '_02': 'February', '_03': 'March', '_04': 'April', '_05': 'May', '_06': 'June',
                     '_07': 'July', '_08': 'August', '_09': 'September', '_10': 'October', '_11': 'November',
                     '_12': 'December'}

    # Iterate over each of the month columns and add it to the array if it is marked as flowering in that month
    for month_number, month_name in month_columns.items():
        if row[prefix + month_number]:
            months.append(month_name)

    # Return the concatenated months
    return ', '.join(months)


'''
' Checking the people listed in detby
'''
def clean_detbys(accessions):
    # Look at all of the people who are 4 characters or less as nobody knows who they are (e.g. EGHO)
    # Force detby to be a string

    # Remove all full stops and standardise spaces
    accessions['detby'] = accessions['detby'].replace(to_replace='\s*\.\s*', value=' ', regex=True)

    # Remove extra and trailing spaces
    accessions['detby'] = accessions['detby'].replace(to_replace='\s+', value=' ', regex=True)
    accessions['detby'] = accessions['detby'].map(str.strip)

    # Remove titles such as Ms, Dr, etc
    titles = ['Ms', 'Dr', 'Mrs', 'Miss', 'Mr', 'Professor', 'Prof']
    for title in titles:
          accessions['detby'] = accessions['detby'].replace(to_replace=title + ' ', value='')

    # View all of the names with less than 5 characters
    mask = (accessions['detby'].str.len() < 5) & (accessions['detby'] != 'None')
    accessions.loc[mask]['detby'].unique()
    # Note: could also do accessions[(accessions.detby.str.len() < 5) & (accessions.detby != 'None')]['detby'] and add .unique()

    # Let's set them to None because nobody can work out who the heck they are/were
    # accessions['detby'][(accessions.detby.str.len() < 5)] = 'None'
    # accessions['detby'][(accessions.detby == 'None')] = ''
    #accessions.loc[accessions['detby'].str.len() < 5, 'detby'] = ''

    # This is what's left
    #accessions.loc[accessions['detby'].str.len() > 0]['detby']

    return accessions


'''
' Locations
'''
def clean_locations(main_path, accessions):
    # Read in the regions csv that Hannelie gave us to get strings for all these weird regions
    precis_regions = pd.read_csv(main_path + '\\python\\precis-regions.csv', encoding='cp1252')

    # Left join this table onto the main accessions table
    accessions = accessions.merge(right=precis_regions, how='left', left_on='regioncode', right_on='CODE')

    # Test to see if it's joined up properly
    accessions[['NAME', 'regioncode', 'CODE']]

    # First do country as it's super easy
    accessions['country'] = accessions['CNTRYNAME'].str.title()

    # Then region, which is everything in the name minus the country
    def remove_country(row):
        return re.sub(pattern=',?\s*' + re.escape(str(row['CNTRYNAME'])), repl='', string=str(row['NAME']), flags=re.IGNORECASE)

    accessions['gaz.major'] = accessions.apply(remove_country, axis=1)

    # Drop unecessary columns
    accessions.drop(['regioncode', 'CODE', 'CNTRYNAME', 'TERRCD', 'NOTES', 'ISOCD', 'NAME'], axis=1, inplace=True)

    return accessions


'''
' Flower description
'''
def clean_flower_descriptions(accessions):
    # Flower description sometimes contains flowering months
    # Let's take a look at all of them which mention a month (7570 of them)
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November',
              'December']
    months_regex = '|'.join(months)
    accessions['flowerdescription'] = accessions['flowerdescription'].astype('str')
    accessions[accessions['flowerdescription'].str.contains(months_regex)]['flowerdescription']

    # Patterns we need to look for
    # Flower(s|ing)\s(during|in|from|within|\:)?
    # Flower(ing)? time:?
    # Flower in habitat in? [month]
    # Flower in [month] in habitat

    # What we actually need to do is remove all the extra words so that we can just extract the months without any fuss
    flowering_regex = re.compile(r'[Ff]lower(ing)?\s+(period|time|in)\:?\s+(habitat\s+((in|from)\s+)?)?')
    accessions['flowerdescription'] = accessions['flowerdescription'].replace(to_replace=flowering_regex, value='', regex=True)

    # When we extract months be careful to look for "[month(s)] in habitat." trailing stuff - [44520:44529]
    # Month spans
    month_spans_regex = '((' + months_regex + ')\s*(\-|to|\:|&)\s*(' + months_regex + '))'

    # What we ideally want to do here is check to see if there is any overlap between what's input in description and
    # what's ticked in months. And then also separate the month spans out into individual months. But right now no time.
    accessions['merged_flowering_months'] = accessions['merged_flowering_months'].map(str) + ', ' + \
                                            accessions.flowerdescription.str.extract(month_spans_regex, re.IGNORECASE)[0]

    # Instead let's delete the month spans from flowerdescription
    accessions['flowerdescription'] = accessions['flowerdescription'].replace(
        to_replace=month_spans_regex + '\s*(\s+in\s+habitat\.?)?\.?\s*', value='', regex=True)

    # Now we need to do individual months
    accessions['merged_flowering_months'] = accessions['merged_flowering_months'].map(str) + ', ' + \
                                            accessions.flowerdescription.str.extract('(' + months_regex + ')', re.IGNORECASE)
    accessions['flowerdescription'] = accessions['flowerdescription'].replace(
        to_replace='(' + months_regex + ')\s*(\s+in\s+habitat\.?)?\.?\s*', value='', regex=True)

    # Ok check and see if there are any month mentions left
    accessions[accessions['flowerdescription'].str.contains(months_regex)]['flowerdescription']

    # TODO Remove 'flower colours?:?\s*'
    # TODO Get list of standard colour codes (pull this from Brahms), search for them, extract them (copy them to FLRCD field)

    # Drop unecessary columns
    accessions.drop(['fl_01', 'fl_02', 'fl_03', 'fl_04', 'fl_05', 'fl_06', 'fl_07', 'fl_08', 'fl_09', 'fl_10', 'fl_11', 'fl_12',
                     'fr_01', 'fr_02', 'fr_03', 'fr_04', 'fr_05', 'fr_06', 'fr_07', 'fr_08', 'fr_09', 'fr_10', 'fr_11', 'fr_12'],
                    axis=1, inplace=True)

    return accessions


'''
' Fixing plant names
'''
def clean_plant_names(main_path, accessions):
    # Read in the csv with all of the plant names which need replacing which Hannelie gave us
    bad_plants = pd.read_csv(main_path + 'python\\access-species-names-not-in-brahms.csv')
    bad_plants = bad_plants.fillna('')

    # Original precis fields = 'family', 'genus', 'spname', 'sspname', 'varname', 'othname'
    # We need to replace these if they occur in the bad_plants
    # Join them together first
    accessions = accessions.merge(right=bad_plants, how='left', on=['family', 'genus', 'spname', 'sspname', 'varname'])

    # Test to see if it's joined up properly
    accessions[pd.isnull(accessions.brahms_family) == False][['family', 'brahms_family', 'genus', 'brahms_genus', 'spname', 'brahms_species', 'sspname', 'brahms_subspecies', 'varname', 'brahms_variety']]

    # Seems to be.. so go ahead and change the values
    accessions.loc[pd.isnull(accessions['brahms_family']) == False, 'family'] = accessions.loc[pd.isnull(accessions['brahms_family']) == False, 'brahms_family']
    accessions.loc[pd.isnull(accessions['brahms_family']) == False, 'genus'] = accessions.loc[pd.isnull(accessions['brahms_family']) == False, 'brahms_genus']
    accessions.loc[pd.isnull(accessions['brahms_family']) == False, 'spname'] = accessions.loc[pd.isnull(accessions['brahms_family']) == False, 'brahms_species']
    accessions.loc[pd.isnull(accessions['brahms_family']) == False, 'sspname'] = accessions.loc[pd.isnull(accessions['brahms_family']) == False, 'brahms_subspecies']
    accessions.loc[pd.isnull(accessions['brahms_family']) == False, 'varname'] = accessions.loc[pd.isnull(accessions['brahms_family']) == False, 'brahms_variety']

    # Drop the unecessary cols
    accessions.drop(['brahms_family', 'brahms_genus', 'brahms_species', 'brahms_subspecies', 'brahms_variety'], axis=1, inplace=True)

    # 15/01/2016 We need to add cultivar + variety + selection + hybrid info
    accessions['receivedas'] = accessions['tmpname'].map(str)
    #accessions.loc[accessions['gardenspeciesid'] != 0, 'receivedas'] += ' | ADDITIONAL_TAXA_INFO: '
    #accessions.loc[pd.isnull(accessions['cultvr']) == False, 'receivedas'] += ' Cultivar: ' + accessions['cultvr'].map(str)
    #accessions.loc[pd.isnull(accessions['selecname']) == False, 'receivedas'] += ' Selection: ' + accessions['selecname'].map(str)
    #accessions.loc[pd.isnull(accessions['hybrdtls']) == False, 'receivedas'] += ' Hybrid: ' + accessions['hybrdtls'].map(str)
    #accessions.loc[pd.isnull(accessions['taxonnotes']) == False, 'receivedas'] += ' Taxon notes: ' + accessions['taxonnotes'].map(str)
    # 29/01 Brenda wants these things in linked data fields...................



    # Drop the unecessary cols - well these all get dropped later anyways
    # accessions.drop(['gardenspeciesid', 'cultvr', 'selecname', 'hybrdtls', 'taxonnotes'], axis=1, inplace=True)
    # accessions.drop(['gardenspeciesid'], axis=1, inplace=True)

    return accessions



