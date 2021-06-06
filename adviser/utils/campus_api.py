from typing import Union
import requests
from lxml import etree
from loguru import logger


BASE_URL = "https://campus.uni-stuttgart.de/cusonline/ee/rest/slc.tm.cp/student/courses"


class CampusApi:
    """
    The Campus API allows for
        - querying individual courses by their id
        - querying for all courses using the skip/top mechanism

    The skip/top mechanism is handled by the objects state. The client
    can just keep calling get_next_batch_of_courses()-method until it returns None.

    The API returns parsed lxml types (https://lxml.de/tutorial.html#the-parse-function).
    """

    def __init__(self, step=25) -> None:
        if step >= 100:
            logger.info("Step size must be < 100. Reducing it to 50. Continuing...")
            step = 50

        self.step = step
        self.skip = 0
        self.top = step
        self.total_courses = None
        self.finished = False
    
    @classmethod
    def get_course_by_id(cls, id) -> etree._Element:
        r = requests.get(BASE_URL + f"/{id}")
        return etree.fromstring(r.content)

    def get_next_batch_of_courses(self) -> Union[list, None]:
        """
        Returns the next n courses.

        Can be called until it returns None, which means that all courses have been returned.
        """
        if self.finished:
            return None

        rval = []

        r = requests.get(BASE_URL + f"?$skip={self.skip}&$top={self.top}")
        root = etree.fromstring(r.content)
        ids = self._get_course_ids_from_batch(root.findall("resource"))
        for id in ids:
            rval.append(self.get_course_by_id(id))

        if not self.total_courses:
            self.total_courses = self._get_total_number_of_courses(root)

        self.skip += self.step
        if self.skip > self.total_courses and self.total_courses is not None:
            self.finished = True

        return rval

    def _get_total_number_of_courses(self, root) -> int:
        return int(root[0].text)

    def _get_course_ids_from_batch(self, batch) -> list:
        ids = []
        for resource in batch:
            try:
                ids.append(int(resource.xpath('content/cpCourseDto/id')[0].text))
            except Exception:
                logger.debug(f"Retrievning course id failed. Continuing...")

        return ids


# example of how to use the api
if __name__ == "__main__":
    # get a specific course by id
    course_xml = CampusApi.get_course_by_id(266549)

    # get all courses in batches
    api = CampusApi(5)
    batch = api.get_next_batch_of_courses()
    courses_count = 0

    while batch is not None:
        # printing start
        courses_count += len(batch)
        print(f"{courses_count} courses have been downloaded.")
        print("Titles of new courses:")
        for course in batch:
            print(f"\t{course.xpath('resource/content/cpCourseDetailDto/cpCourseDto/courseTitle/value')[0].text}")
        # printing end

        batch = api.get_next_batch_of_courses()
