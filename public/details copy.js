document.addEventListener('DOMContentLoaded', function () {
  const params = new URLSearchParams(window.location.search);
  const spec1Id = params.get('spec1_id');
  const spec2Id = params.get('spec2_id');
  const spec1Name = params.get('spec1_name');
  const spec2Name = params.get('spec2_name');

  console.log("spec1Id", spec1Id)
  console.log("spec2Id", spec2Id)

  fetch('/api/requirements?spec1Id=' + spec1Id + '&spec2Id=' + spec2Id)
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById('requirements-container');
      const table = document.createElement('table');
      table.id = 'requirementsTable';
      table.className = 'table table-striped table-bordered';


      // Create the table header
      const thead = table.createTHead();
      const headerRow = thead.insertRow();
      const headers = [
        `${spec1Name} ID`,
        `${spec1Name} Quelle`,
        `${spec1Name} Titel`,
        `${spec1Name} Beschreibung`,
        `${spec1Name} Verbindlichkeit`,
        `${spec1Name} Prüfverfahren`,
        `${spec2Name} ID`,
        `${spec2Name} Quelle`,
        `${spec2Name} Title`,
        `${spec2Name} Beschreibung`,
        `${spec2Name} Verbindlichkeit`,
        `${spec2Name} Prüfverfahren`,
        'Vergleichsalgorithmus',
        'Titel Similarity Score',
        'Beschreibung Similarity Score',
        'Identification Number',
      ];
      headers.forEach(text => {
        let th = document.createElement('th');
        th.textContent = text;
        headerRow.appendChild(th);
      });

      // Create the table body
      const tbody = table.createTBody();
      data.forEach(item => {
        let row = tbody.insertRow();
        let cell;
      
        // ePA Requirement Number
        cell = row.insertCell();
        cell.textContent = item.spec1_requirement_number;
      
        // ePA Source
        cell = row.insertCell();
        cell.textContent = item.spec1_source;
        
        // ePA Title
        cell = row.insertCell();
        cell.textContent = item.spec1_title;
        colorizeCellBackground(cell, item.title_similarity_score);
      
        // ePA Description
        cell = row.insertCell();
        cell.textContent = item.spec1_description;
        colorizeCellBackground(cell, item.description_similarity_score);
      
        // ePA Obligation
        cell = row.insertCell();
        cell.textContent = item.spec1_obligation;
        colorizeComparisonCells(cell, item.spec1_obligation, item.spec2_obligation);
      
        // ePA Test Procedure
        cell = row.insertCell();
        cell.textContent = item.spec1_test_procedure;
        colorizeComparisonCells(cell, item.spec1_test_procedure, item.spec2_test_procedure);
      
        // eRP Requirement Number
        cell = row.insertCell();
        cell.textContent = item.spec2_requirement_number;
      
        // eRP Source
        cell = row.insertCell();
        cell.textContent = item.spec2_source;
      
        // eRP Title
        cell = row.insertCell();
        cell.textContent = item.spec2_title;
        colorizeCellBackground(cell, item.title_similarity_score);
      
        // eRP Description
        cell = row.insertCell();
        cell.textContent = item.spec2_description;
        colorizeCellBackground(cell, item.description_similarity_score);
      
        // eRP Obligation
        cell = row.insertCell();
        cell.textContent = item.spec2_obligation;
        colorizeComparisonCells(cell, item.spec1_obligation, item.spec2_obligation);
      
        // eRP Test Procedure
        cell = row.insertCell();
        cell.textContent = item.spec2_test_procedure;
        colorizeComparisonCells(cell, item.spec1_test_procedure, item.spec2_test_procedure);
      
        // Comparison Method
        cell = row.insertCell();
        cell.textContent = item.comparison_method;
      
        // Title Similarity Score
        cell = row.insertCell();
        cell.textContent = parseFloat(item.title_similarity_score).toFixed(2);
        colorizeCellBackground(cell, item.title_similarity_score);
      
        // Description Similarity Score
        cell = row.insertCell();
        cell.textContent = parseFloat(item.description_similarity_score).toFixed(2);
        colorizeCellBackground(cell, item.description_similarity_score);

        // Combined Identifier
        cell = row.insertCell();
        cell.textContent = item.combined_identifier;
      });

      // Append the table to the container
      container.appendChild(table);

      // Initialize DataTables on the created table
      $('#similarityMatrixTable').DataTable({
        "scrollX": true, // Enables horizontal scrolling
        "autoWidth": false // Allows manual resizing of columns
      });

      // Make columns adjustable by the ColReorder plugin
      new $.fn.dataTable.ColReorder('#similarityMatrixTable');
    })
    .catch(error => console.error('Error fetching the requirements:', error));
});

// Function to colorize cell based on similarity score
function colorizeCellBackground(cell, score) {
  const normalizedScore = parseFloat(score); // Assuming score is between 0 and 1
  const hexRatio = Math.round(normalizedScore * 255).toString(16).padStart(2, '0');
  
  // Use the same background color logic as getColorForSimilarity
  cell.style.backgroundColor = `#000e52${hexRatio}`;

  // Set the text color based on the score for better contrast
  cell.style.color = normalizedScore > 0.5 ? 'white' : 'black';
}


// Function to colorize cell based on equality
function colorizeComparisonCells(cell, value1, value2, maxPossibleDifference) {
  // Assuming value1 and value2 are numeric for this example
  const difference = Math.abs(value1 - value2);
  const normalizedDifference = maxPossibleDifference ? (difference / maxPossibleDifference) : (value1 === value2 ? 0 : 1);

  // If there is no difference, we want full blue, otherwise, we fade to white based on the difference
  const hexRatio = Math.round((1 - normalizedDifference) * 255).toString(16).padStart(2, '0');

  // Set the background color
  cell.style.backgroundColor = `#000e52${hexRatio}`;

  // Set the text color for contrast based on the difference
  // If the background is dark (values are the same), use white text; otherwise, use black text
  cell.style.color = normalizedDifference < 0.5 ? 'white' : 'black';
}
