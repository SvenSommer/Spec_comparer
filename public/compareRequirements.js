document.addEventListener('DOMContentLoaded', function () {
  fetch('/api/requirements')
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById('requirements-container');
      const table = document.createElement('table');
      table.id = 'requirementsTable'; // Give the table an ID for the DataTables initialization
      table.className = 'table table-striped table-bordered';

      // Create the table header
      const thead = table.createTHead();
      const headerRow = thead.insertRow();
      const headers = [
        'combined Number',
        'ePA Requirement Number',
        'ePA Title',
        'ePA Description',
        'eRP Requirement Number',
        'eRP Title',
        'eRP Description',
        'Comparison Method',
        'Title Similarity Score',
        'Description Similarity Score'
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
        cell.textContent = item.combined_identifier;

        // ePA Requirement Number
        cell = row.insertCell();
        cell.textContent = item.epa_requirement_number;

        // ePA Title
        cell = row.insertCell();
        cell.textContent = item.epa_title;
        colorizeCellBackground(cell, item.title_similarity_score);

        // ePA Description
        cell = row.insertCell();
        cell.textContent = item.epa_description;
        colorizeCellBackground(cell, item.description_similarity_score);

        cell = row.insertCell();
        cell.textContent = item.erp_requirement_number;


        // eRP Title
        cell = row.insertCell();
        cell.textContent = item.erp_title;
        colorizeCellBackground(cell, item.title_similarity_score);
        // eRP Description
        cell = row.insertCell();
        cell.textContent = item.erp_description;
        colorizeCellBackground(cell, item.description_similarity_score);
        // comparison_method
        cell = row.insertCell();
        cell.textContent = item.comparison_method;

        // Title Similarity Score
        cell = row.insertCell();
        // Format the score to two decimal places
        cell.textContent = parseFloat(item.title_similarity_score).toFixed(2);

        // Description Similarity Score
        cell = row.insertCell();
        // Format the score to two decimal places
        cell.textContent = parseFloat(item.description_similarity_score).toFixed(2);
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