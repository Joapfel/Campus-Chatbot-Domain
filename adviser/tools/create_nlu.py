import argparse
import os
import json

"""
This script generates inform and request rules based on the binary topics in the ontology.

Usage:
python create_nlu.py /path/to/ontology_file.json /path/to/nlu_file.nlu

TODO: could also be implemented as interactive tool in future
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('ontology', type=str, help='path to the ontology file')
    parser.add_argument('nlu', type=str, help='path to the nlu file')
    
    args = parser.parse_args()

    if not os.path.isfile(args.nlu):
        print('Path to nlu file is invalid.')
        exit(1)
    if not os.path.isfile(args.ontology):
        print('Path to ontology file is invalid.')
        exit(1)

    ##
    # generate templates
    ##

    # read informables, requestables, etc from ontology
    topics = []
    requestables = []
    binaries = set()

    with open(args.ontology, 'r', encoding='utf-8') as f:
        ontology_json = json.load(f)
        for k in ontology_json['informable'].keys():
            topics.append(k)
        for k in ontology_json['requestable']:
            requestables.append(k)
        for k in ontology_json['binary']:
            binaries.add(k)

    with open(args.nlu, 'a') as f:
        
        # write inform rules to the nlu file
        line_break = '\n\n'
        for topic in topics:
            # only consider binary topics for now since they are hard to scale by hand
            # other informables can still be handcrafted since they are limited in number
            if topic not in binaries: continue 

            human_readable_topic = ' '.join(topic.split('_'))
            inform_rule = f'{line_break}rule inform({topic}) \
                \n\tif {topic} = "true" \
                \n\t\t"I am interested in {human_readable_topic}"  \
                \n\t\t"I would like to take a course about {human_readable_topic}" \
                \n\t\t"Show me courses about {human_readable_topic}" \
                \n\tif {topic} = "false" \
                \n\t\t"I am not interested in {human_readable_topic}"  \
                \n\t\t"I would not like to take a course about {human_readable_topic}" \
                \n\t\t"Dont show me courses about {human_readable_topic}"\n' # last line needs a linebreak
            line_break = '\n'
            f.write(inform_rule)

        # write request rules to the nlu file
        line_break = '\n\n' 
        for requestable in requestables:
            human_readable_requestable = ' '.join(requestable.split('_'))
            request_rule = f'{line_break}rule request({requestable})'

            # differentiate between binaries and non-binaries
            #
            # in the campus_courses domain binaries are mostly topics 
            # and hence the user can ask whether a course is about (or contains) a certain topic
            #
            # while the non-binaries are values as the course description, the semester hours etc
            # that the user might want to show to him
            if requestable in binaries:
                request_rule += f'\n\t"is it about {human_readable_requestable}"\n'
            else:
                request_rule += f'\n\t"show me the {human_readable_requestable}"\n'

            line_break = '\n' 
            f.write(request_rule)