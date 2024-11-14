import unittest
from python_xml_json_explorecourses import (
    xml_to_dictionary,
)


class TestExploreCourses(unittest.TestCase):

    def test_python_xml_parsing(self):
        params = {
            "q": "EDUC147",
            "academicYear": "20222023",  # Ensure you match the expected academic year
        }
        result = xml_to_dictionary(**params)

        # Check for specific keys and their expected values
        self.assertEqual(result["subject"], "EDUC")
        self.assertEqual(result["code"], "147")
        self.assertEqual(
            result["title"], "Stanford and Its Worlds: 1885-present (HISTORY 58E)"
        )
        self.assertEqual(result["year"], "2022-2023")
        self.assertEqual(result["grading"], "Letter or Credit/No Credit")
        self.assertEqual(result["term"], ["2022-2023 Spring"])
        self.assertEqual(result["format_of_course"], "LEC")
        self.assertEqual(result["section_units"], "3")
        self.assertEqual(result["unitsMin"], "3")
        self.assertEqual(result["unitsMax"], "3")
        self.assertListEqual(result["days"], ["Monday", "Wednesday"])
        self.assertListEqual(
            result["instructors"], ["Emily Levine", "Mitchell Stevens"]
        )
        self.assertEqual(result["tags"], "Higher_Ed; History; Undergraduate")

        # Check sections
        self.assertEqual(len(result["sections"]), 1)
        self.assertEqual(result["sections"][0]["subject"], "EDUC")
        self.assertEqual(result["sections"][0]["code"], "147")
        self.assertEqual(result["sections"][0]["term"], "2022-2023 Spring")
        self.assertEqual(result["sections"][0]["format_of_course"], "LEC")
        self.assertEqual(result["sections"][0]["sectionNumber"], "01")
        self.assertEqual(result["sections"][0]["section_units"], "3")
        self.assertEqual(result["sections"][0]["unitsMin"], "3")
        self.assertEqual(result["sections"][0]["unitsMax"], "3")
        self.assertEqual(result["sections"][0]["startTime"], "9:30am")
        self.assertEqual(result["sections"][0]["endTime"], "11:20am")
        self.assertEqual(result["sections"][0]["location"], "Ceras 300")
        self.assertEqual(result["sections"][0]["days"], "Monday Wednesday")
        self.assertEqual(
            result["sections"][0]["instructor_name"], "Emily Levine; Mitchell Stevens"
        )

        # Check additional expected values
        self.assertEqual(result["section_count"], 1)
        self.assertTrue(result["course_offered"])
        self.assertTrue(result["course_valid"])
        self.assertEqual(result["program"], [])
        self.assertListEqual(result["category"], ["Higher_Ed", "History"])
        self.assertListEqual(result["audience"], ["Undergraduate"])


if __name__ == "__main__":
    unittest.main()
