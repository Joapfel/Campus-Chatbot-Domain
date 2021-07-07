import json
from utils.domain.jsonlookupdomain import JSONLookupDomain
from utils.campus_api import CampusApi
from typing import Iterable


class JSONLookupDomainAPI(JSONLookupDomain):

    __slots__ = "campus_api", "_registration_info_xpath", "_registration_link_xpath"

    def __init__(self, name: str, json_ontology_file: str = None, sqllite_db_file: str = None, \
                 display_name: str = None):
        super(JSONLookupDomainAPI, self).__init__(name, json_ontology_file, sqllite_db_file, display_name)
        self.campus_api = CampusApi()
        self._registration_info_xpath = "resource/content/cpCourseDetailDto/cpCourseDto/registrationInfoStatus"
        self._registration_link_xpath = "resource/link[@name='CpCourseRegistrationDto']/@href"
        
    def find_info_about_entity(self, entity_id, requested_slots: Iterable):
        """
        Overrides the original entity retrieval to extend one use case.
        For user questions about the registration of a course, live data is fetched from the Campus API,
        and used in the system response.

        For other use cases the information is fetched from the DB as before.
        """
        if requested_slots and "registration" in requested_slots.keys():
            try:
                query = 'SELECT id FROM {} WHERE {}="{}";'.format(
                    self.get_domain_name(), self.get_primary_key(), entity_id)
                res = self.query_db(query)
                course_id = res[0]["id"]
                course_xml = self.campus_api.get_course_by_id(course_id)
                registration_infos = course_xml.xpath(self._registration_info_xpath)
                registration_link = "The link could not be found."

                if not len(registration_infos) > 0:
                    return [{"registration": "not_found"}]
                else:
                    try:
                        registration_link = course_xml.xpath(self._registration_link_xpath)[0]
                    except Exception:
                        pass

                    registration_info = registration_infos[0].text
                    if registration_info == "RUNNING":
                        return [{"registration": "True", "link": f"{registration_link}"}]
                    if registration_info == "NONE":
                        return [{"registration": "False", "link": f"{registration_link}"}]

                    # in case there are unknown status
                    return [{"registration": "unexpected_status", "status": f"{registration_info}", "course_id": f"{course_id}"}]

            except Exception:
                return [{"registration": "exception"}]
            
        # default case
        return super(JSONLookupDomainAPI, self).find_info_about_entity(entity_id, requested_slots)
        