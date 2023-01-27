import os
import re
import requests

ENDPOINT = 'https://ttp.cbp.dhs.gov'


def get_slots_for_location(location_id):
    params = {
        'orderBy': 'soonest',
        'minimum': 1,
        'limit': 3,
        'locationId': location_id,
    }
    rsp = requests.get(f'{ENDPOINT}/schedulerapi/slots', params)
    return rsp.json()


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


def any_appointment_slots_open():
    location_ids = os.environ['LOCATION_IDS']
    if not location_ids or not re.match(r'^(\d+,)*(\d+)$', location_ids):
        raise ValueError(f'Bad location IDs: {location_ids}')
    location_ids = [int(x) for x in location_ids.split(',')]

    locations = get_locations()
    locations_by_id = {location['id']: location for location in locations}
    valid_location_ids = locations_by_id.keys()

    for location_id in location_ids:
        if location_id not in valid_location_ids:
            raise ValueError(f'Unknown location ID {location_id}')

    all_slots = {location_id: get_slots_for_location(location_id)
                 for location_id in location_ids}

    has_slots_open = False
    for location_id, slots in all_slots.items():
        location_name = locations_by_id[location_id]['name']
        print(f'Location {location_name} (ID {location_id}) has {len(slots)} slots')
        for slot in slots:
            print(f"* {slot['startTimestamp']} - {slot['endTimestamp']} ({slot['duration']} minutes)")

            has_slots_open = True

    return has_slots_open


def main():
    found_appointment = False
    try:
        found_appointment = any_appointment_slots_open()
    except ValueError as ex:
        # We want configuration errors to still be apparent -- it's worse to be
        # quietly expecting an email, rather than being bombarded with emails
        # telling you it's not configured correctly
        print(ex)
        exit(1)
    except Exception as ex:
        print(ex)
    finally:
        # Fail if an appointment was found
        exit(1 if found_appointment else 0)


if __name__ == '__main__':
    main()
