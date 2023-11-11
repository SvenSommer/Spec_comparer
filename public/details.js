document.addEventListener('DOMContentLoaded', function () {
  function getURLParameter(name) {
    return new URLSearchParams(window.location.search).get(name);
  }

  function createTableHeaderWithColspan(text, colspan) {
    let th = document.createElement('th');
    th.textContent = text;
    th.setAttribute('colspan', colspan.toString());
    return th;
  }

  function createTableHeaderRow(headers) {
    let headerRow = document.createElement('tr');
    headers.forEach(text => {
      let th = document.createElement('th');
      th.textContent = text;
      headerRow.appendChild(th);
    });
    return headerRow;
  }

  function createAndAppendTable(container, data, spec1Name, spec2Name) {
    const table = document.createElement('table');
    table.id = 'requirementsTable';
    table.className = 'table table-striped table-bordered';

    const thead = table.createTHead();
    const specHeaderRow = thead.insertRow();

    [spec1Name, spec2Name, 'Vergleichsalgorithmus', 'Titel Similarity Score', 'Beschreibung Similarity Score'].forEach((name, index) => {
      specHeaderRow.appendChild(createTableHeaderWithColspan(name, index < 2 ? 6 : 1));
    });

    thead.appendChild(createTableHeaderRow([
      'ID', 'Quelle', 'Titel', 'Beschreibung', 'Verbindlichkeit', 'Prüfverfahren',
      'ID', 'Quelle', 'Title', 'Beschreibung', 'Verbindlichkeit', 'Prüfverfahren',
      '', '', '' //, ''
    ]));

    const tbody = table.createTBody();
    data.forEach(item => createAndPopulateRow(tbody, item));

    container.appendChild(table);
  }

  function createAndPopulateRow(tbody, item) {
    let row = tbody.insertRow();
    populateRowWithCells(row, item);
  }

  

  function populateRowWithCells(row, item) {
    function addCell(row, text, score) {
      let cell = row.insertCell();
      cell.textContent = text;
      if (score !== undefined) {
        colorizeCellBackground(cell, score);
      }
    }
  
    function addComparisonCell(row, spec1Value, spec2Value) {
      let cell = row.insertCell();
      cell.textContent = spec1Value;
      colorizeComparisonCells(cell, spec1Value, spec2Value);
    }
  
    addCell(row, item.req1_requirement_number);
    addCell(row, item.req1_source);
    addCell(row, item.spec1_title, item.title_similarity_score);
    addCell(row, item.spec1_description, item.description_similarity_score);
    addComparisonCell(row, item.spec1_obligation, item.spec2_obligation);
    addComparisonCell(row, item.spec1_test_procedure, item.spec2_test_procedure);
  
    addCell(row, item.req2_requirement_number);
    addCell(row, item.req2_source);
    addCell(row, item.spec2_title, item.title_similarity_score);
    addCell(row, item.spec2_description, item.description_similarity_score);
  
    addComparisonCell(row, item.spec2_obligation, item.spec1_obligation);
    addComparisonCell(row, item.spec2_test_procedure, item.spec1_test_procedure);
  
    addCell(row, item.comparison_method);
    addCell(row, parseFloat(item.title_similarity_score).toFixed(2), item.title_similarity_score);
    addCell(row, parseFloat(item.description_similarity_score).toFixed(2), item.description_similarity_score);
 // addCell(row, item.combined_identifier);
  }

  function colorizeCellBackground(cell, score) {
    const normalizedScore = parseFloat(score);
    const hexRatio = Math.round(normalizedScore * 255).toString(16).padStart(2, '0');
    cell.style.backgroundColor = `#000e52${hexRatio}`;
    cell.style.color = normalizedScore > 0.5 ? 'white' : 'black';
  }

  function colorizeComparisonCells(cell, value1, value2, maxPossibleDifference = 1) {
    const difference = Math.abs(value1 - value2);
    const normalizedDifference = value1 === value2 ? 0 : difference / maxPossibleDifference;
    const hexRatio = Math.round((1 - normalizedDifference) * 255).toString(16).padStart(2, '0');
    cell.style.backgroundColor = `#000e52${hexRatio}`;
    cell.style.color = normalizedDifference < 0.5 ? 'white' : 'black';
  }

  const spec1Id = getURLParameter('spec1_id');
  const spec2Id = getURLParameter('spec2_id');
  const spec1Name = getURLParameter('spec1_name');
  const spec2Name = getURLParameter('spec2_name');

  fetch('/api/requirements?spec1Id=' + spec1Id + '&spec2Id=' + spec2Id)
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById('requirements-container');
      createAndAppendTable(container, data, spec1Name, spec2Name);

      $('#similarityMatrixTable').DataTable({
        "scrollX": true,
        "autoWidth": false
      });

      new $.fn.dataTable.ColReorder('#similarityMatrixTable');
    })
    .catch(error => console.error('Error fetching the requirements:', error));
});
