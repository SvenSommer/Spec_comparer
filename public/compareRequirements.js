document.addEventListener('DOMContentLoaded', function () {
  fetch('/api/requirements')
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById('requirements-container');
      const table = document.createElement('table');
      table.id = 'requirementsTable';
      table.className = 'table table-striped table-bordered';


      const spec1Name = data.length > 0 ? `${data[0].spec_name}` : 'ePA';
      const spec2Name = data.length > 0 ? `${data[0].spec_name}` : 'eRP';


      // Create the table header
      const thead = table.createTHead();
      const headerRow = thead.insertRow();
      const headers = [
        `${spec1Name} Requirement Number`,
        `${spec1Name} Source`,
        `${spec1Name} Title`,
        `${spec1Name} Description`,
        `${spec1Name} Obligation`,
        `${spec1Name} Test Procedure`,
        `${spec2Name} Requirement Number`,
        `${spec2Name} Source`,
        `${spec2Name} Title`,
        `${spec2Name} Description`,
        `${spec2Name} Obligation`,
        `${spec2Name} Test Procedure`,
        'Comparison Method',
        'Title Similarity Score',
        'Description Similarity Score',
        'Combined Number',
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
      $('#requirementsTable').DataTable({
        "scrollX": true, // Enables horizontal scrolling
        "autoWidth": false // Allows manual resizing of columns
      });

      // Make columns adjustable by the ColReorder plugin
      new $.fn.dataTable.ColReorder('#requirementsTable');
    })
    .catch(error => console.error('Error fetching the requirements:', error));
});

// Function to colorize cell based on similarity score
function colorizeCellBackground(cell, score) {
  const normalizedScore = parseFloat(score);
  // HSL values for a softer green
  let hue = 120; // Green color
  let saturation = 20; // Lower saturation for a softer color
  let lightness = 90 - (normalizedScore * 40); // Decrease lightness based on score; higher score, darker color

  cell.style.backgroundColor = `hsl(${hue}, ${saturation}%, ${lightness}%)`;

  // If the background is dark (which means high similarity), make the text white for better contrast
  if (normalizedScore > 0.7) {
    cell.style.color = 'white';
  } else {
    cell.style.color = 'black'; // For lighter backgrounds, use black text
  }
}

// Function to colorize cell based on equality
function colorizeComparisonCells(cell, value1, value2) {
  let saturation = 20; // Lower saturation for a softer color
  let lightness = 90 - (0.5 * 40); // Decrease lightness based on score; higher score, darker color
  if (value1 === value2) {
    cell.style.backgroundColor = `hsl(${120}, ${saturation}%, ${lightness}%)`;
  } else {
    cell.style.backgroundColor = `hsl(${60}, ${90}%, ${90}%)`;
  }
}