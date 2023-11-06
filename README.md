# Requirements Analysis Script

## Description
This script is designed to process and compare textual requirements from different sources. It imports requirements from CSV files into an SQLite database, processes the text to remove punctuation, numbers, and stopwords, and then compares them using different similarity measures.

## Installation
Before running this script, ensure you have Python installed on your system. Then, install the necessary dependencies using the following command:
\`\`\`bash
pip install nltk spacy scikit-learn sqlite3
\`\`\`

Additionally, you may need to download certain NLTK corpora and the Spacy language model:
\`\`\`python
import nltk
nltk.download('stopwords')
nltk.download('wordnet')

import spacy
spacy.cli.download('de_core_news_md')
\`\`\`

## Usage
To use this script, place your CSV files with the requirements in a directory and adjust the paths in the script accordingly. The `RequirementProcessor` class handles the database operations, while the `RequirementComparer` abstract class and its subclasses are used to compare requirements based on different algorithms.

To run the script, simply execute it in a Python environment:
\`\`\`bash
python requirements_analysis.py
\`\`\`

## Classes and Methods
- `RequirementProcessor`: Initializes the database, imports data, and preprocesses text.
- `RequirementComparer`: An abstract base class for implementing different requirement comparison algorithms.
- `JaccardRequirementComparer`: Implements the Jaccard similarity measure.
- `CosineRequirementComparer`: Implements the cosine similarity measure using TF-IDF.
- `CustomRequirementComparer`: An example class for a custom comparison algorithm.

## Database Configuration
The script assumes an SQLite database. It will create two tables: `requirements` for storing individual requirements and `requirement_similarities` for storing similarity scores between requirements.

## Logging
Logging is configured to provide info level logs to the console, including the progress of comparisons and any errors encountered.

## Extending the Script
You can extend the script by implementing additional subclasses of `RequirementComparer` to introduce new comparison methods.

## Notes
- Ensure CSV files are encoded in UTF-8 to prevent encoding issues.
- The script is set up to handle German text, as indicated by the use of the `de_core_news_md` Spacy model and German stopwords.
- When extending the database schema or comparison methods, ensure consistency in the SQL queries and the associated class methods.
## Results Display
The results of the requirements comparison are displayed in a web interface using `compareRequirements.js`. This JavaScript file makes a fetch request to an API endpoint that returns the compared requirements data in JSON format. It then dynamically generates a table to display the data on the frontend.

The `app.js` sets up an Express.js server and defines the API endpoint `/api/requirements` that queries the SQLite database for the similarity scores and returns them in the response.

Here's a snippet of how the `compareRequirements.js` script processes and displays the data:

```javascript
document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/requirements')
      // ... handle response and data
});
```

And here's how the `app.js` sets up the server and endpoint:

```javascript
const express = require("express");
const app = express();
// ... rest of the server setup
```

These scripts work together to display the results of the requirements analysis in a user-friendly format.
