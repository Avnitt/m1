import json


def process_event_data(input_data):
    processed = []
    
    for entry in input_data.get('data', []):
        event_info = entry.get('event', {})
        catalogue_info = entry.get('catalogue', {})

        runners = []
        for runner in catalogue_info.get('runners', []):
            processed_runner = {
                "name": runner.get('name'),
                "backOdds": (runner.get('backOdds', [])[0]).get('price'), 
                "layOdds": (runner.get('layOdds', [])[0]).get('price')
            }
            runners.append(processed_runner)
        
        processed_entry = {
            "event_id": event_info.get('id'),
            "event_name": event_info.get('name'),
            "openDate": event_info.get('openDate'),
            "runners": json.dumps(runners)
        }
        
        processed.append(processed_entry)
    return processed

def process_market_data(input_data):
    processed = {'bookMaker': [],
                 'fancy': []}
    
    runner = []

    for entry in input_data.get('fancy', []):
        marketId = entry.get('marketId')
        marketName = entry.get('marketName')
        statusName = entry.get('statusName')
        runsNo = entry.get('runsNo')
        runsYes = entry.get('runsYes')
        oddsNo = entry.get('oddsNo')
        oddsYes = entry.get('oddsYes')
        minSetting = entry.get('minSetting')
        maxSetting = entry.get('maxSetting')
        sortingOrder = entry.get('sortingOrder')
        catagory = entry.get('catagory')

        processed_entry = {
            'marketId': marketId,
            'marketName': marketName,
            'statusName': statusName,
            'runsNo': runsNo,
            'runsYes': runsYes,
            'oddsNo': oddsNo,
            'oddsYes': oddsYes,
            'minSetting': minSetting,
            'maxSetting': maxSetting,
            'sortingOrder': sortingOrder,
            'catagory': catagory
        }
        processed.get('fancy').append(processed_entry)

    bookMaker = input_data.get('bookMaker', [])
    for entry in bookMaker:
        selectionName = entry.get('selectionName')
        selectionStatus = entry.get('selectionStatus')
        backOdds = entry.get('backOdds')
        layOdds = entry.get('layOdds')

        processed_runner = {
            'selectionName': selectionName,
            'selectionStatus': selectionStatus,
            'backOdds': backOdds,
            'layOdds': layOdds 
        }
        runner.append(processed_runner)

    processed_bookmaker = {
        'marketId': bookMaker[0].get('marketId'),
        'marketName': bookMaker[0].get('marketName'),
        'statusName': bookMaker[0].get('statusName'),
        'minSetting': bookMaker[0].get('minSetting'),
        'maxSetting': bookMaker[0].get('maxSetting'),
        'sortPeriority': bookMaker[0].get('sortPeriority'),
        'runners': runner
    }
    processed.get('bookMaker').append(processed_bookmaker)
    return processed