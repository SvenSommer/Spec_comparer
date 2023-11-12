document.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(window.location.search);
  const selectedSpecIds = [...params].filter(([key]) => key.startsWith('ids')).map(([, value]) => value);

  fetchMatrixData(selectedSpecIds);

  const debouncedFetchMatrixData = debounce(fetchMatrixData, 500);

  document.getElementById('similarityThreshold').addEventListener('input', function (event) {
    const thresholdValue = event.target.value;
    document.getElementById('thresholdValue').textContent = thresholdValue;
    // Verwende die debounced Funktion, um unnötige API-Aufrufe zu vermeiden, während der Schieberegler bewegt wird
    debouncedFetchMatrixData(selectedSpecIds, thresholdValue);
  });
});

function debounce(func, wait) {
  let timeout;
  return function (...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

function fetchMatrixData(selectedSpecIds, threshold = 0.75) {
  // Fügen Sie den Threshold-Wert dem Query-String hinzu
  const query = `/api/matrix?ids=${selectedSpecIds.join('&ids=')}&threshold=${threshold}`;

  fetch(query)
    .then(response => response.ok ? response.json() : Promise.reject(`Network response was not ok ${response.statusText}`))
    .then(data => {
      const specs = new Set(data.flatMap(({ spec1_name, spec1_version, spec2_name, spec2_version }) =>
        [`${spec1_name} V${spec1_version}`, `${spec2_name} V${spec2_version}`]));
      createMatrixTable([...specs], data, threshold);
    })
    .catch(error => console.error('There has been a problem with your fetch operation:', error));
}

const fetchSpecDetails = (selectedSpecIds) => {
  const specDetailsQuery = `/api/specs?ids=${selectedSpecIds.join('&ids=')}`;
  fetch(specDetailsQuery)
    .then(response => response.json())
    .then(specDetails => {
      const specsDetailsSet = new Set(specDetails.map(({ name, version }) => `${name} V${version}`));
      createPlaceholderTable([...specsDetailsSet]);
    })
    .catch(error => console.error('Error fetching specification details:', error));
};

const getColorForSimilarity = (similarity, maxSimilarity) => {
  const ratio = (similarity / maxSimilarity);
  const hexRatio = Math.round(ratio * 255).toString(16).padStart(2, '0');
  return {
    backgroundColor: `#000e52${hexRatio}`,
    textColor: ratio > 0.5 ? 'white' : 'black'
  };
};

const createTableElement = (specsArray, createCellContent) => {
  const table = document.createElement('table');
  table.id = 'gTable';
  table.className = 'table table-striped table-bordered';

  table.appendChild(createTableHead(specsArray));
  table.appendChild(createTableBody(specsArray, createCellContent));

  document.body.appendChild(table);
};

const createTableHead = (specsArray) => {
  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  headerRow.appendChild(document.createElement('th')); // Empty top-left cell
  specsArray.forEach(spec => {
    const th = document.createElement('th');
    th.textContent = spec;
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);
  return thead;
};

const createTableBody = (specsArray, createCellContent) => {
  const tbody = document.createElement('tbody');
  specsArray.forEach(spec1 => {
    const tr = document.createElement('tr');
    const th = document.createElement('th');
    th.textContent = spec1;
    tr.appendChild(th);
    specsArray.forEach(spec2 => {
      const td = document.createElement('td');
      td.classList.add('hover-cell');
      createCellContent(td, spec1, spec2);
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  return tbody;
};

const createPlaceholderTable = (specsArray) => {
  const container = document.getElementById('matrix-container');
  // Entfernen Sie alle Kindelemente vom Container
  while (container.firstChild) {
    container.removeChild(container.firstChild);
  }

  createTableElement(specsArray, (td, spec1, spec2) => {
    console.log("spec1", spec1)
    console.log("spec2", spec2)
    td.textContent = spec1 === spec2 ? '-' : '0';
  });
};

const createMatrixTable = (specs, data, threshold) => {
  let table = document.getElementById('gTable');


  if (!table) {
    createPlaceholderTable(specs);
    table = document.getElementById('gTable');
  }

  // Update the cells of the existing table.
  for (let i = 1; i < table.rows.length; i++) {
    for (let j = 1; j < table.rows[i].cells.length; j++) {
      const td = table.rows[i].cells[j];
      // Skip the diagonal
      if (i === j) {
        td.textContent = '-';
        continue;
      }

      const spec1 = table.rows[i].cells[0].textContent;
      const spec2 = table.rows[0].cells[j].textContent;
      const similarity = data.find(({ spec1_name, spec1_version, spec2_name, spec2_version }) =>
        (`${spec1_name} V${spec1_version}` === spec1 && `${spec2_name} V${spec2_version}` === spec2) ||
        (`${spec1_name} V${spec1_version}` === spec2 && `${spec2_name} V${spec2_version}` === spec1)
      );

      if (similarity) {
        // Determine if we are above or below the diagonal and update text content accordingly
        let uniqueRequirements;
        let totalRequirements;
        if (j > i) {
          // Above the diagonal
          uniqueRequirements = similarity.spec1_unique_requirements;
          totalRequirements = similarity.spec1_req_count;
          td.textContent = `${uniqueRequirements} von ${totalRequirements}`;
        } else {
          // Below the diagonal
          uniqueRequirements = similarity.spec2_unique_requirements;
          totalRequirements = similarity.spec2_req_count;
          td.textContent = `${uniqueRequirements} von ${totalRequirements}`;
        }
        const ratio = totalRequirements > 0 ? uniqueRequirements / totalRequirements : 0;
        const { backgroundColor, textColor } = getColorForSimilarity(ratio, 0.55);
        td.style.backgroundColor = backgroundColor;
        td.style.color = textColor;
        td.title = 'Click to see details';
        td.style.cursor = 'pointer';
        td.onclick = () => {
          window.location.href = `details.html?spec1_name=${encodeURIComponent(similarity.spec1_name + ' ' + similarity.spec1_version)}&spec2_name=${encodeURIComponent(similarity.spec2_name + ' ' + similarity.spec2_version)}&spec1_id=${encodeURIComponent(similarity.spec1_id)}&spec2_id=${encodeURIComponent(similarity.spec2_id)}&threshold=${encodeURIComponent(threshold)}`;
        };
      } else {
        td.textContent = '-';
        td.style.backgroundColor = '';
        td.style.color = '';
        td.title = '';
        td.style.cursor = 'default';
        td.onclick = null;
      }

    }
  }
};
