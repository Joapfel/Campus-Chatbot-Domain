import argparse
import os
import json


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('ontology', type=str, default='../adviser/resources/ontologies/campus_courses.json',
                        help='path to the ontology file')
    parser.add_argument('nlg', type=str, default='../adviser/resources/nlg_templates/campus_coursesMessages.nlg',
                        help='path to the nlg file')
    args = parser.parse_args()

    if not os.path.isfile(args.nlg):
        print('Path to nlg file is invalid.')
        exit(1)
    if not os.path.isfile(args.ontology):
        print('Path to ontology file is invalid.')
        exit(1)

    # get the list of requestable slots
    with open(args.ontology, 'r', encoding='utf-8') as file:
        requestable_list = json.load(file)['requestable']

    with open(args.nlu, 'a', encoding='utf-8') as file:
        file.write('\n# ------------------------System Requestable Topics-------------------------------#\n\n')
        for slot in requestable_list[requestable_list.index('american_literature_culture'):]:
            file.write(f'template request({slot})\n')
            file.write(f'\tShall the course be related to {slot}?\n\n')
