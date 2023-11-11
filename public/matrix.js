document.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(window.location.search);
  const selectedSpecIds = [...params].filter(([key]) => key.startsWith('ids')).map(([, value]) => value);

  console.log("selectedSpecIds", selectedSpecIds);
  const query = `/api/matrix?ids=${selectedSpecIds.join('&ids=')}`;

  fetch(query)
    .then(response => response.ok ? response.json() : Promise.reject(`Network response was not ok ${response.statusText}`))
    .then(data => {
      const specs = new Set(data.flatMap(({ spec1_name, spec1_version, spec2_name, spec2_version }) =>
        [`${spec1_name} V${spec1_version}`, `${spec2_name} V${spec2_version}`]));
      specs.size === 0 && selectedSpecIds.length > 0 ? fetchSpecDetails(selectedSpecIds) : createMatrixTable([...specs], data);
    })
    .catch(error => console.error('There has been a problem with your fetch operation:', error));
});

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
  const ratio = similarity / maxSimilarity;
  const hexRatio = Math.round(ratio * 255).toString(16).padStart(2, '0');
  return {
    backgroundColor: `#000e52${hexRatio}`,
    textColor: ratio > 0.5 ? 'white' : 'black'
  };
};

const createTableElement = (specsArray, createCellContent) => {
  const table = document.createElement('table');
  table.id = 'similarityMatrixTable';
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
  createTableElement(specsArray, (td, spec1, spec2) => {
    td.textContent = spec1 === spec2 ? '-' : '0';
  });
};

const createMatrixTable = (specs, data) => {
  const maxSimilarity = Math.max(...data.map(item => item.similarity_count));
  createTableElement(specs, (td, spec1, spec2) => {
    const similarity = data.find(({ spec1_name, spec1_version, spec2_name, spec2_version }) =>
      (`${spec1_name} V${spec1_version}` === spec1 && `${spec2_name} V${spec2_version}` === spec2) ||
      (`${spec1_name} V${spec1_version}` === spec2 && `${spec2_name} V${spec2_version}` === spec1)
    );
    if (similarity) {
      td.textContent = similarity.similarity_count;
      const { backgroundColor, textColor } = getColorForSimilarity(similarity.similarity_count, maxSimilarity);
      td.style.backgroundColor = backgroundColor;
      td.style.color = textColor;
      td.title = 'Click to see details';
      td.style.cursor = 'pointer';
      td.onclick = () => {
        window.open(`details.html?spec1_name=${encodeURIComponent(similarity.spec1_name + ' ' + similarity.spec1_version)}&spec2_name=${encodeURIComponent(similarity.spec2_name + ' ' + similarity.spec2_version)}&spec1_id=${encodeURIComponent(similarity.spec1_id)}&spec2_id=${encodeURIComponent(similarity.spec2_id)}`, '_blank');
      };
    } else {
      td.textContent = '-';
    }
  });
};