import unittest
import sys
from unittest.mock import Mock, patch
sys.path.append('../controller')

from RequirementProcessor import RequirementProcessor

class TestRequirementProcessor(unittest.TestCase):
    def setUp(self):
        # Setup that runs before each test method
        self.processor = RequirementProcessor(':memory:')

    def tearDown(self):
        # Teardown that runs after each test method
        self.processor.close()

    def test_init(self):
        # Test the __init__ method
        self.assertIsNotNone(self.processor.conn)
        self.assertIsNotNone(self.processor.cursor)

    def test_dict_factory(self):
        # Test the dict_factory method
        mock_cursor = Mock()
        mock_cursor.description = [('field1',), ('field2',)]
        row = ('value1', 'value2')
        expected_dict = {'field1': 'value1', 'field2': 'value2'}
        result = self.processor.dict_factory(mock_cursor, row)
        self.assertEqual(result, expected_dict)

    def test_preprocess_text(self):
        # Test the preprocess_text method
        # Note: You should mock the stopwords.words and SnowballStemmer for a unit test,
        # to avoid dependency on external libraries and make the test faster
        text = "ePA-Frontend example E-Rezept-FdV text with 123 numbers."
        processed_text = self.processor.preprocess_text(text)
        expected_text = "exampl text with numb"  # assuming stopwords and stemming are applied correctly
        self.assertEqual(processed_text, expected_text)

       
# This allows the test to be run from the command line
if __name__ == '__main__':
    unittest.main()
