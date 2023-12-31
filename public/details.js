document.addEventListener('DOMContentLoaded', function () {
  // Funktion, um den Threshold aus der URL zu holen
  const thresholdValue = parseFloat(getURLParameter('threshold')) || 0.5; // Standardwert, falls nicht in URL vorhanden

  const spec1Id = getURLParameter('spec1_id');
  const spec2Id = getURLParameter('spec2_id');
  const spec1Name = getURLParameter('spec1_name');
  const spec2Name = getURLParameter('spec2_name');

  function getURLParameter(name) {
    return new URLSearchParams(window.location.search).get(name);
  }

  function createAndFillTable(threshold) {
    fetch('/api/requirements?spec1Id=' + spec1Id + '&spec2Id=' + spec2Id)
      .then(response => response.json())
      .then(data => {
        const container = document.getElementById('requirements-container');
        container.innerHTML = '';
        createAndAppendTable(container, data, spec1Name, spec2Name, threshold);

        if ($.fn.dataTable.isDataTable('#gTable')) {
          $('#gTable').DataTable().destroy();
        }
        $('#gTable').DataTable({
          "scrollX": true,
          "autoWidth": false
        });

        new $.fn.dataTable.ColReorder('#gTable');
      })
      .catch(error => console.error('Error fetching the requirements:', error));
  }

  // Initialisiere die Seite mit dem Threshold-Wert aus der URL
  createAndFillTable(thresholdValue);

  // Funktion, um den Wert des Sliders aus der URL zu setzen
  function setSliderValueFromURL() {
    const slider = document.getElementById('similarityThreshold');
    const sliderValueDisplay = document.getElementById('thresholdValue');
    slider.value = thresholdValue;
    sliderValueDisplay.textContent = thresholdValue;
  }

  setSliderValueFromURL();

  function debounce(func, wait) {
    let timeout;
    return function (...args) {
      const context = this;
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(context, args), wait);
    };
  }

  // Event-Listener für den Slider, um auf Änderungen zu reagieren, mit Debounce
  function onSliderChange() {
    const slider = document.getElementById('similarityThreshold');
    const debouncedFillTable = debounce(function (event) {
      const newThresholdValue = event.target.value;
      const sliderValueDisplay = document.getElementById('thresholdValue');
      sliderValueDisplay.textContent = newThresholdValue;

      // Aktualisiere die Tabelle mit dem neuen Schwellenwert
      createAndFillTable(parseFloat(newThresholdValue));
    }, 500); // Warte 500 ms nach der letzten Änderung des Sliders, bevor die Tabelle aktualisiert wird

    slider.addEventListener('input', debouncedFillTable);
  }

  onSliderChange();
});

  function setSliderValueFromURL() {
    const thresholdValue = getURLParameter('threshold');
    if (thresholdValue) {
      const slider = document.getElementById('similarityThreshold');
      const sliderValueDisplay = document.getElementById('thresholdValue');
      slider.value = thresholdValue;
      sliderValueDisplay.textContent = thresholdValue;
    }
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

  function createAndAppendTable(container, data, spec1Name, spec2Name, threshold) {
    const table = document.createElement('table');
    table.id = 'gTable';
    table.className = 'table table-striped table-bordered';

    const thead = table.createTHead();
    const specHeaderRow = thead.insertRow();

    [spec1Name, spec2Name, 'Titel Similarity Score', 'Beschreibung Similarity Score'].forEach((name, index) => {
      specHeaderRow.appendChild(createTableHeaderWithColspan(name, index < 2 ? 6 : 1));
    });

    thead.appendChild(createTableHeaderRow([
      'ID', 'Quelle', 'Titel', 'Beschreibung', 'Verbindlichkeit', 'Prüfverfahren',
      'ID', 'Quelle', 'Title', 'Beschreibung', 'Verbindlichkeit', 'Prüfverfahren',
      '', ''
    ]));

    const tbody = table.createTBody();
    data.forEach(item => createAndPopulateRow(tbody, item, threshold));

    container.appendChild(table);
  }

  function createAndPopulateRow(tbody, item, threshold) {
    if (parseFloat(item.description_similarity_score) >= threshold) {
      let row = tbody.insertRow();
      populateRowWithCells(row, item);
    }
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

  $(document).ready(function() {
    var table = $('#gTable').DataTable({
      responsive: true,
      "autoWidth": false
    });
  
    // Spaltenfilter - Dropdowns erstellen
    table.columns().every(function() {
      var column = this;
      var select = $('<select><option value=""></option></select>')
        .appendTo($(column.footer()).empty())
        .on('change', function() {
          var val = $.fn.dataTable.util.escapeRegex($(this).val());
          column.search(val ? '^' + val + '$' : '', true, false).draw();
        });
  
      column.data().unique().sort().each(function(d, j) {
        select.append('<option value="' + d + '">' + d + '</option>')
      });
    });
  });
  