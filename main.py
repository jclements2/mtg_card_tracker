import shutil
import sys
import os

import requests


def get_image(url):
    session = requests.session()
    response = session.get(url, stream=True)
    return response


def get_more(url):
    session = requests.session()
    response = session.get(url)
    return response


def get_set_details(search_uri):
    session = requests.session()
    url = search_uri
    response = session.get(url)
    return response


def get_set(set_name):
    session = requests.session()
    url = f'https://api.scryfall.com/sets/{set_name}'
    response = session.get(url)
    return response


def main():
    set_name = sys.argv[1]
    optional_arg = None
    if len(sys.argv) == 3:
        optional_arg = sys.argv[2]

    card_count = 1
    file_name = f'set_list_{set_name}.csv'
    image_dir = os.path.join('./', f'{set_name}_images')
    if os.path.exists(image_dir):
        shutil.rmtree(image_dir)
    os.mkdir(image_dir)
    output_file = os.path.join('./', file_name)
    if os.path.exists(output_file):
        os.remove(output_file)
    out_stream = open(output_file, 'a')
    out_stream.write(f'Collector Number,Card Name,Rarity,Type,Mana Cost,CMC,Power,Toughness,Keywords,Price\n')
    print(f'Set name: {set_name}')
    set_info = get_set(set_name)
    set_info_json = set_info.json()
    set_search_uri = set_info_json["search_uri"]
    set_details = get_set_details(set_search_uri)
    set_details_json = set_details.json()
    total_cards = set_details_json["total_cards"]
    print(f'Total cards: {total_cards}')
    has_more = set_details_json["has_more"]
    next_page = set_details_json["next_page"]
    while has_more:
        has_more = set_details_json["has_more"]
        if has_more:
            next_page = set_details_json["next_page"]
        for item in set_details_json["data"]:
            keywords = ''
            card_name = item["name"]
            rarity = item["rarity"]
            type_line = item["type_line"]
            mana_cost = item["mana_cost"]
            img_link = item["image_uris"]["png"]
            cmc = item["cmc"]
            try:
                power = item["power"]
            except KeyError as ke:
                power = 'none'
            try:
                toughness = item["toughness"]
            except KeyError as ke:
                toughness = 'none'
            colors = item["colors"]
            color_identity = item["color_identity"]
            for keyword in item["keywords"]:
                keywords = keywords + f' {keyword}'
            oracle_text = item["oracle_text"]
            oracle_text = oracle_text.replace("\n", "-->")
            if item["prices"]["usd"] is not None:
                price = f'${item["prices"]["usd"]}'
            elif item["prices"]["usd_foil"] is not None:
                price = f'${item["prices"]["usd_foil"]}'
            else:
                price = 'Not Available'
            collector_number = item["collector_number"]
            print(f'Retrieving "{card_name}": {collector_number}')
            out_stream.write(f'{collector_number},"{card_name}",{rarity},{type_line},{mana_cost},{cmc},{power},{toughness},{keywords},{price}\n')
            if optional_arg != '--no-img':
                img_response = get_image(img_link)
                img_filename = os.path.join(image_dir, f'{card_name}_{collector_number}.png')
                with open(img_filename, 'wb') as f:
                    shutil.copyfileobj(img_response.raw, f)
                print(f'Image {card_count} of {total_cards} Downloaded: ', img_filename)
            card_count += 1
        set_details = get_more(next_page)
        set_details_json = set_details.json()
    out_stream.close()


if __name__ == '__main__':
    main()
