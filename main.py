import os
import pandas as pd 
import numpy as np
from scipy.stats import zscore


folder2223_path = '/Users/as/Personal projects/FootballProjects/2223/1'
folder2324_path = '/Users/as/Personal projects/FootballProjects/2324/1'
folder2425_path = '/Users/as/Personal projects/FootballProjects/2425/1'

def process_data_sets():
    df_2223 = pd.DataFrame()
    for root, dirs, files in os.walk(folder2223_path):
        for file in files:
            if file.endswith('.xlsx'):
                file_path = os.path.join(root, file)
                df1 = pd.read_excel(file_path, engine='openpyxl')
                df_2223 = pd.concat([df_2223, df1], ignore_index=True)
    df_2223.insert(2, 'Season', '22/23')

    df_2324 = pd.DataFrame()
    for root, dirs, files in os.walk(folder2324_path):
         for file in files:
            if file.endswith('.xlsx'):
                file_path = os.path.join(root, file)
                df2 = pd.read_excel(file_path, engine='openpyxl')
                df_2324 = pd.concat([df_2324, df2], ignore_index=True)
    df_2324.insert(2, 'Season', '23/24')


    df_2425 = pd.DataFrame()
    for root, dirs, files in os.walk(folder2425_path):
         for file in files:
            if file.endswith('.xlsx'):
                file_path = os.path.join(root, file)
                df3 = pd.read_excel(file_path, engine='openpyxl')
                df_2425 = pd.concat([df_2425, df3], ignore_index=True)
    df_2425.insert(2, 'Season', '24/25')

    global df
    df = pd.concat([df_2223, df_2324, df_2425], ignore_index=True)
    df = df.drop_duplicates(subset=['Player', 'Minutes played'])
process_data_sets()


def position_clean():
    df['Position'] = df['Position'].str.split(',').str[0]
    gk_pos = 'GK'
    cb_pos = 'CB'
    fb_pos = ('RB', 'LB')
    cm_pos = ('DM', 'CM', 'AMF')
    wide_pos = ('LWB', 'RWB', 'RM', 'LM', 'LAMF', 'RAMF', 'RW', 'LW')
    st_pos = ('CF', 'ST')
    df.loc[df['Position'].str.contains(gk_pos), 'Position'] = 'GK'
    df.loc[df['Position'].str.contains(cb_pos), 'Position'] = 'CB'
    df.loc[df['Position'].str.contains('|'.join(fb_pos)), 'Position'] = 'FB'
    df.loc[df['Position'].str.contains('|'.join(cm_pos)) & ~df['Position'].str.contains('|'.join(wide_pos + st_pos)), 'Position'] = 'CM'
    df.loc[df['Position'].str.contains('|'.join(wide_pos)), 'Position'] = 'WIDE'
    df.loc[df['Position'].str.contains('|'.join(st_pos)), 'Position'] = 'FW'
position_clean()

def extra_stats():
    df['xG/shot'] = np.where((df['xG per 90'] == 0) | (df['Shots per 90'] == 0), 0, df['xG per 90'] / df['Shots per 90'])
    df['xG performance'] = np.where((df['Goals per 90'] == 0) | (df['xG per 90'] == 0), 0, df['Goals per 90'] - df['xG per 90'])
    df['Successful dribbles per 90'] = df['Successful dribbles, %'] * df['Dribbles per 90']
    df['Successful crosses per 90'] = df['Accurate crosses, %'] * df['Crosses per 90']
    df['Successful shots per 90'] = df['Shots per 90'] * df['Shots on target, %']
    df['xA/box entry'] = np.where((df['xA per 90'] == 0) | (df['Passes to penalty area per 90'] == 0), 0, df['xA per 90'] / df['Passes to penalty area per 90'])
    df['xA/shot assist'] = np.where((df['xA per 90'] == 0) | (df['Shot assists per 90'] == 0), 0, df['xA per 90'] / df['Shot assists per 90'])
    df['Shot/box touch'] = np.where((df['Shots per 90'] == 0) | (df['Touches in box per 90'] == 0), 0, df['Shots per 90'] / df['Touches in box per 90'])
    df['Passes to final third per 90'] *= df['Accurate passes to final third, %'] 
    df['Passes to penalty area per 90'] *= df['Accurate passes to penalty area, %'] 
    df['Through passes per 90'] *= df['Accurate through passes, %'] 
    df['Dangerous attacking actions per 90'] = df['Successful dribbles per 90'] + df['Shot assists per 90'] + df['Key passes per 90'] + df['Smart passes per 90'] + df['Through passes per 90'] + df['Deep completions per 90'] + df['Successful shots per 90']

extra_stats()

#def possession_adjust_def():
   # possession_adjust_def = df['PAdj Interceptions'] / df['Interceptions per 90']
    #stats_for_adjust_def = ['Defensive duels per 90', 'Aerial duels per 90', 'Shots blocked per 90', 'Successful defensive actions per 90']
    
    #for stat in stats_for_adjust_def:
        #df[stat] = df[stat] * possession_adjust_def

#possession_adjust_def()

#def possession_adjust_att():
    #stats_for_adjust_att = ['Successful dribbles per 90', 'Progressive runs per 90', 'Accelerations per 90']
    #for stat in stats_for_adjust_att:
       # df[stat] = df[stat] / df['Received passes per 90']

#possession_adjust_att()

def zscore_manipulate():
    global columns1
    columns1 = df.columns[10:]
    df[columns1] = df.groupby('Position', group_keys=False)[columns1].apply(lambda x: x.apply(zscore))
zscore_manipulate()

def sigmoid(x):
    return 100 / (1 +np.exp(-x))

def sigmoid_manipulate():
    scaled_ratings = df[columns1].apply(sigmoid)
    df[columns1] = scaled_ratings
sigmoid_manipulate()

def positional_scores():
        df['Aerial'] = df['Aerial duels won, %'] * 0.7 + df['Aerial duels per 90'] * 0.3
        df['Duel dominance'] = df['Defensive duels won, %'] * 0.8 + df['Successful defensive actions per 90'] * 0.2
        df['Duel volume'] = df['Successful defensive actions per 90'] * 0.4 + df['Defensive duels per 90'] * 0.6
        df['Reading'] = df['PAdj Interceptions'] * 0.6 + df['Shots blocked per 90'] * 0.4
        df['Tidy on ball'] = df['Accurate progressive passes, %'] * 0.5 + df['Accurate short / medium passes, %'] * 0.25 + df['Accurate forward passes, %'] * 0.125 + df['Accurate long passes, %'] * 0.125
        df['Progressive via pass'] = df['Progressive passes per 90'] * 0.6 + df['Short / medium passes per 90'] * 0.2 + df['Passes to final third per 90'] * 0.2
        df['Progressive via carry'] = df['Progressive runs per 90'] * 0.5 + df['Successful dribbles per 90'] * 0.3 + df['Accelerations per 90'] * 0.2
        df['1v1 attacking ability'] = df['Successful dribbles per 90'] * 0.5 + df['Progressive runs per 90'] * 0.2 + df['Accelerations per 90'] * 0.2 + df['Fouls suffered per 90'] * 0.1
        df['Crossing'] = df['Successful crosses per 90'] * 0.7 + df['Accurate crosses, %'] * 0.3
        df['Chance creation'] = df['xA per 90'] * 0.4 + df['Shot assists per 90'] * 0.2 + df['Key passes per 90'] * 0.2 + df['Smart passes per 90'] * 0.2
        df['Attack progression via pass'] = df['Passes to final third per 90'] * 0.4 + df['Passes to penalty area per 90'] * 0.4 + df['Through passes per 90'] * 0.1 + df['Deep completions per 90'] * 0.1
        df['Goal threat'] = df['xG per 90'] * 0.7 + df['xG/shot'] * 0.2 + df['Touches in box per 90'] * 0.1
        df['Clinical'] = df['xG performance'] * 0.5 + df['Shots on target, %'] * 0.5
        df['CB Rating'] = df['Duel dominance'] * 0.4 + df['Aerial'] * 0.15 + df['Reading'] * 0.1 + df['Tidy on ball'] * 0.2 + df['Progressive via pass'] * 0.15
        df['WCB Rating'] = df['Duel dominance'] * 0.25 + df['Aerial'] * 0.075 + df['Reading'] * 0.075 + df['Tidy on ball'] * 0.2 + df['Progressive via pass'] * 0.175 + df['Progressive via carry'] * 0.225
        df['WB Rating'] = df['Duel dominance'] * 0.3 + df['Progressive via pass'] * 0.1 + df['Progressive via carry'] * 0.15 + df['Crossing'] * 0.15 + df['Tidy on ball'] * 0.1 + df['Chance creation'] * 0.15 + df['Attack progression via pass'] * 0.05
        df['Winger Rating'] = df['1v1 attacking ability'] * 0.3 + df['Crossing'] * 0.25 + df['Chance creation'] * 0.3 + df['Goal threat'] * 0.1 + df['Clinical'] * 0.05
        df['Wide Forward Rating'] = df['1v1 attacking ability'] * 0.3 + df['Chance creation'] * 0.3 + df['Goal threat'] * 0.325 + df['Clinical'] * 0.075
        df['Deep-lying playmaker Rating'] = df['Tidy on ball'] * 0.35 + df['Progressive via pass'] * 0.35 + df['Duel dominance'] * 0.15 + df['Duel volume'] * 0.15
        df['Defensive midfielder Rating'] = df['Duel dominance'] * 0.4 + df['Duel volume'] * 0.1 + df['Aerial'] * 0.1 + df['Tidy on ball'] * 0.25 + df['Progressive via pass'] * 0.15
        df['Ball-winning midfielder Rating'] = df['Duel volume'] * 0.5 + df['Duel dominance'] * 0.1 + df['Tidy on ball'] * 0.25 + df['Progressive via pass'] * 0.15
        df['Box-to-box midfielder Rating'] = df['Duel volume'] * 0.2 + df['Reading'] * 0.08 + df['Tidy on ball'] * 0.12 + df['Progressive via pass'] * 0.12 + df['Chance creation'] * 0.12 + df['Progressive via carry'] * 0.12 + df['Attack progression via pass'] * 0.12 + df['Goal threat'] * 0.12
        df['Attacking midfielder/Deep-lying Forward Rating'] = df['Chance creation'] * 0.3 + df['1v1 attacking ability'] * 0.2 + df['Goal threat'] * 0.2 + df['Attack progression via pass'] * 0.3
        df['Target man Rating'] = df['Aerial'] * 0.4 + df['Goal threat'] * 0.2 + df['Clinical'] * 0.2 + df['Chance creation'] * 0.2
        df['Goalscoring 9 Rating'] = df['Goal threat'] * 0.5 + df['Clinical'] * 0.5 
positional_scores()

zscore_manipulate()
sigmoid_manipulate()

def assign_league():
    step1_2223 = ['Aldershot Town', 'Altrincham', 'Barnet', 'Boreham Wood', 'Bromley', 'Chesterfield', 'Dagenham & Redbridge', 'Dorking Wanderers', 'Eastleigh', 'Halifax Town', 'Gateshead', 'Maidenhead United', 'Maidstone United', 'Notts County', 'Oldham Athletic', 'Scunthorpe United', 'Solihull Moors', 'Southend United', 'Torquay United', 'Wealdstone', 'Woking', 'Wrexham', 'Yeovil Town', 'York City']
    step1_2324 = ['Fylde', 'Aldershot Town', 'Altrincham', 'Barnet', 'Boreham Wood', 'Bromley', 'Chesterfield', 'Dagenham & Redbridge', 'Dorking Wanderers', 'Eastleigh', 'Ebbsfleet United', 'Gateshead', 'Halifax Town', 'Hartlepool United', 'Kidderminster Harriers', 'Maidenhead United', 'Oldham Athletic', 'Oxford City', 'Rochdale', 'Solihull Moors', 'Southend United', 'Wealdstone', 'Woking', 'York City']
    step1_2425 = ['Fylde', 'Aldershot Town', 'Altrincham', 'Barnet', 'Boston United', 'Braintree Town', 'Dagenham & Redbridge', 'Eastleigh', 'Ebbsfleet United', 'Forest Green Rovers','Gateshead', 'Halifax Town', 'Hartlepool United', 'Maidenhead United', 'Oldham Athletic', 'Rochdale', 'Solihull Moors', 'Southend United', 'Sutton United', 'Tamworth', 'Wealdstone', 'Woking', 'York City', 'Yeovil Town']
    step2_2223 = ["Fylde", "AFC Telford United", "Alfreton Town", "Banbury United", "Blyth Spartans", "Boston United", "Brackley Town", "Bradford (Park Avenue)", "Buxton", "Chester", "Chorley", "Curzon Ashton", "Darlington 1883", "Farsley Celtic FC", "Gloucester City", "Hereford FC", "Kettering Town", "Kidderminster Harriers", "King's Lynn Town", "Leamington", "Peterborough Sports", "Scarborough Athletic", "Southport", "Spennymoor Town", "Bath City", "Braintree Town", "Chelmsford City", "Cheshunt", "Chippenham Town", "Concord Rangers", "Dartford", "Dover Athletic", "Dulwich Hamlet", "Eastbourne Borough", "Ebbsfleet United", "Farnborough", "Hampton & Richmond", "Havant & Waterlooville", "Hemel Hempstead Town", "Hungerford Town", "Oxford City", "Slough Town", "St. Albans City", "Taunton Town", "Tonbridge Angels", "Welling United", "Weymouth", "Worthing"]
    step2_2324 = ["Alfreton Town", "Banbury United", "Bishop's Stortford", "Blyth Spartans", "Boston United", "Brackley Town", "Buxton", "Chester", "Chorley", "Curzon Ashton", "Darlington 1883", "Farsley Celtic FC", "Gloucester City", "Hereford FC", "King's Lynn Town", "Peterborough Sports", "Rushall Olympic", "Scarborough Athletic", "Scunthorpe United", "South Shields", "Southport", "Spennymoor Town", "Tamworth", "Warrington Town", "Aveley", "Bath City", "Braintree Town", "Chelmsford City", "Chippenham Town", "Dartford", "Dover Athletic", "Eastbourne Borough", "Farnborough", "Hampton & Richmond", "Havant & Waterlooville", "Hemel Hempstead Town", "Maidstone United", "Slough Town", "St. Albans City", "Taunton Town", "Tonbridge Angels", "Torquay United", "Truro City", "Welling United", "Weston-super-Mare", "Weymouth", "Worthing", "Yeovil Town"]
    step2_2425 = ["Alfreton Town", "Brackley Town", "Buxton", "Chester", "Chorley", "Curzon Ashton", "Darlington 1883", "Farsley Celtic FC", "Hereford FC", "King's Lynn Town", 'Marine', 'Needham Market', 'Oxford City', "Peterborough Sports", 'Radcliffe FC', "Rushall Olympic", "Scarborough Athletic", "Scunthorpe United", "South Shields", "Southport", "Spennymoor Town", "Warrington Town", "Aveley", "Bath City", "Boreham Wood", "Chelmsford City", 'Chesham United', "Chippenham Town", 'Dorking Wanderers', "Eastbourne Borough", 'Enfield Town', "Farnborough", "Hampton & Richmond", "Hemel Hempstead Town", 'Hornchurch', "Maidstone United", 'Salisbury', "Slough Town", "St. Albans City", "Tonbridge Angels", "Torquay United", "Truro City", "Welling United", "Weston-super-Mare", "Weymouth", "Worthing"]
    efl_2223 = ["AFC Wimbledon", "Barrow", "Bradford City", "Carlisle United", "Colchester United", "Crawley Town", "Crewe Alexandra", "Doncaster Rovers", "Gillingham", "Grimsby Town", "Harrogate Town", "Hartlepool United", "Leyton Orient", "Mansfield Town", "Newport County", "Northampton Town", "Rochdale", "Salford City", "Stevenage", "Stockport County", "Sutton United", "Swindon Town", "Tranmere Rovers", "Walsall"]
    efl_2324 = ["Accrington Stanley", "AFC Wimbledon", "Barrow", "Bradford City", "Colchester United", "Crawley Town", "Crewe Alexandra", "Doncaster Rovers", "Forest Green Rovers", "Gillingham", "Grimsby Town", "Harrogate Town", "Mansfield Town", "Milton Keynes Dons", "Morecambe", "Newport County", "Notts County", "Salford City", "Stockport County", "Sutton United", "Swindon Town", "Tranmere Rovers", "Walsall", "Wrexham"]
    efl_2425 = ["Accrington Stanley", "AFC Wimbledon", "Barrow", "Bradford City", 'Bromley', 'Cheltenham Town', 'Chesterfield', "Colchester United", "Crewe Alexandra", "Doncaster Rovers", 'Fleetwood Town', "Gillingham", "Grimsby Town", "Harrogate Town", "Milton Keynes Dons", "Morecambe", "Newport County", "Notts County", 'Port Vale', "Salford City", "Swindon Town", "Tranmere Rovers", "Walsall"]
    df['League'] = None

    df.loc[(df['Team within selected timeframe'].isin(step1_2223)) & (df['Season'] == '22/23'), 'League'] = 'Step 1'
    df.loc[(df['Team within selected timeframe'].isin(step1_2324)) & (df['Season'] == '23/24'), 'League'] = 'Step 1'
    df.loc[(df['Team within selected timeframe'].isin(step1_2425)) & (df['Season'] == '24/25'), 'League'] = 'Step 1'
    df.loc[(df['Team within selected timeframe'].isin(step2_2223)) & (df['Season'] == '22/23'), 'League'] = 'Step 2'
    df.loc[(df['Team within selected timeframe'].isin(step2_2324)) & (df['Season'] == '23/24'), 'League'] = 'Step 2'
    df.loc[(df['Team within selected timeframe'].isin(step2_2425)) & (df['Season'] == '24/25'), 'League'] = 'Step 2'
    df.loc[(df['Team within selected timeframe'].isin(efl_2223)) & (df['Season'] == '22/23'), 'League'] = 'League Two'
    df.loc[(df['Team within selected timeframe'].isin(efl_2324)) & (df['Season'] == '23/24'), 'League'] = 'League Two'
    df.loc[(df['Team within selected timeframe'].isin(efl_2425)) & (df['Season'] == '24/25'), 'League'] = 'League Two'
    df.loc[df['Team within selected timeframe'].str.contains('U23|U21|U19|U18'), 'League'] = 'Youth'
    df.loc[df['League'].isnull(), 'League'] = 'Other'

assign_league()

print(df)

df.to_csv('/Users/as/Library/CloudStorage/GoogleDrive-exyhd1@gmail.com/My Drive/Dorking Wanderers FC Scouting/Recruitment/Pipeline/maindata.csv', index=False)
df.to_csv('/Users/as/Personal projects/FootballProjects/maindata.csv', index=False)
