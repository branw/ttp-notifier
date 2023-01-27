from collections import defaultdict

import requests

ENDPOINT = 'https://ttp.cbp.dhs.gov'


def get_locations(
        temporary=False,
        invite_only=False,
        operational=True,
        service_name='Global Entry'):
    params = {
        'temporary': temporary,
        'inviteOnly': invite_only,
        'operational': operational,
        'serviceName': service_name,
    }
    rsp = requests.get(f'{ENDPOINT}/schedulerapi/locations/', params)
    return rsp.json()


def main():
    locations = get_locations()

    locations_by_country_and_state = defaultdict(lambda: defaultdict(list))
    for location in locations:
        country = location['countryCode']
        state = location['state']
        locations_by_country_and_state[country][state].append(location)

    for country in sorted(locations_by_country_and_state.keys()):
        print(f'### {country}')
        locations_by_state = locations_by_country_and_state[country]
        for state in sorted(locations_by_state.keys()):
            if state:
                print(f'#### {state}')
            print()
            print('| ID | Name | City | Address |')
            print('|----|------|------|---------|')

            locations_in_state = sorted(locations_by_state[state],
                                        key=lambda loc: loc['id'])
            for location in locations_in_state:
                print(f"|{location['id']}|{location['name']}|{location['city']}|{location['address']}|")
            print()


if __name__ == '__main__':
    main()
