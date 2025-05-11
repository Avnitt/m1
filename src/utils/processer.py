import json

def process_event_data(input_data):
    processed = []
    if not input_data or 'data' not in input_data:
        return processed

    for entry in input_data.get('data', []):
        event_info = entry.get('event', {})
        catalogue_info = entry.get('catalogue', {})

        runners = []
        for runner in catalogue_info.get('runners', []):
            processed_runner = {
                "name": runner.get('name'),
                "backOdds": (runner.get('backOdds', [{}])[0]).get('price'),
                "layOdds": (runner.get('layOdds', [{}])[0]).get('price')
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
    processed = {'bookMaker': [], 'fancy': []}
    if not input_data:
        return processed

    # Process fancy markets
    for entry in input_data.get('fancy', []):
        processed_entry = {
            'marketId': entry.get('marketId'),
            'marketName': entry.get('marketName'),
            'statusName': entry.get('statusName'),
            'runsNo': entry.get('runsNo'),
            'runsYes': entry.get('runsYes'),
            'oddsNo': entry.get('oddsNo'),
            'oddsYes': entry.get('oddsYes'),
            'minSetting': entry.get('minSetting'),
            'maxSetting': entry.get('maxSetting'),
            'sortingOrder': entry.get('sortingOrder'),
            'catagory': entry.get('catagory')
        }
        processed['fancy'].append(processed_entry)

    # Process bookmaker markets
    bookMaker = input_data.get('bookMaker', [])
    if bookMaker:
        runners = []
        for entry in bookMaker:
            processed_runner = {
                'selectionName': entry.get('selectionName'),
                'selectionStatus': entry.get('selectionStatus'),
                'backOdds': entry.get('backOdds'),
                'layOdds': entry.get('layOdds')
            }
            runners.append(processed_runner)

        first_entry = bookMaker[0]
        processed_bookmaker = {
            'marketId': first_entry.get('marketId'),
            'marketName': first_entry.get('marketName'),
            'statusName': first_entry.get('statusName'),
            'minSetting': first_entry.get('minSetting'),
            'maxSetting': first_entry.get('maxSetting'),
            'sortPeriority': first_entry.get('sortPeriority'),
            'runners': runners
        }
        processed['bookMaker'].append(processed_bookmaker)

    return processed