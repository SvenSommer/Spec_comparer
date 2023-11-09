document.addEventListener('DOMContentLoaded', function () {
  const params = new URLSearchParams(window.location.search);
  const selectedSpecIds = [];

  for (const [key, value] of params) {
    if (key.startsWith('ids')) {
      selectedSpecIds.push(value);
    }
  }

  console.log("selectedSpecIds",selectedSpecIds)
    // Fetch the similarity matrix data from the API
    fetch(`/api/matrix?ids=${selectedSpecIds.join('&ids=')}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
      })
      .then(data => {
        // Process data to create a unique list of specifications
        let specs = new Set();
        data.forEach(row => {
          specs.add(row.spec1_name + ' V' + row.spec1_version);
          specs.add(row.spec2_name + ' V' + row.spec2_version);
        });
        specs = Array.from(specs);

        // Create the matrix table element
        const matrixTable = document.createElement('table');
        matrixTable.id = 'similarityMatrixTable';
        matrixTable.className = 'table table-striped table-bordered';

        // Create the matrix table head
        const matrixThead = document.createElement('thead');
        const matrixHeaderRow = document.createElement('tr');
        matrixHeaderRow.appendChild(document.createElement('th')); // Empty top-left cell
        specs.forEach(spec => {
          const th = document.createElement('th');
          th.textContent = spec;
          matrixHeaderRow.appendChild(th);
        });
        matrixThead.appendChild(matrixHeaderRow);
        matrixTable.appendChild(matrixThead);

        // Create the matrix table body
        const matrixTbody = document.createElement('tbody');
        specs.forEach(spec1 => {
          const tr = document.createElement('tr');
          const th = document.createElement('th');
          th.textContent = spec1;
          tr.appendChild(th);

          specs.forEach(spec2 => {
            const td = document.createElement('td');
            // Find the similarity count for the pair (spec1, spec2) in the data
            const similarity = data.find(row => 
              (row.spec1_name + ' V' + row.spec1_version === spec1 &&
               row.spec2_name + ' V' + row.spec2_version === spec2) ||
              (row.spec1_name + ' V' + row.spec1_version === spec2 &&
               row.spec2_name + ' V' + row.spec2_version === spec1)
            );
            if (similarity) {
                td.textContent = similarity.similarity_count;
                // Farbkodierung hinzufügen
                td.style.backgroundColor = getColorForSimilarity(similarity.similarity_count);
                // Tooltips hinzufügen
                td.title = 'Click to see details';
                td.style.cursor = 'pointer'; // Zeigt den Mauszeiger als Klickzeiger
                // Event-Listener für das Klicken auf die Zelle hinzufügen
                td.addEventListener('click', function() {
                  // Öffnen der Detailseite mit den entsprechenden Parametern
                  window.open(
                    'details.html' +
                    '?spec1_name=' + encodeURIComponent(similarity.spec1_name + ' ' + similarity.spec1_version) +
                    '&spec2_name=' + encodeURIComponent(similarity.spec2_name + ' ' + similarity.spec2_version) +
                    '&spec1_id=' + encodeURIComponent(similarity.spec1_id) +
                    '&spec2_id=' + encodeURIComponent(similarity.spec2_id),
                    '_blank'
                  );
                });
              } else {
                td.textContent = '-';
              }
              tr.appendChild(td);
          });

          matrixTbody.appendChild(tr);
        });
        matrixTable.appendChild(matrixTbody);

        // Append the matrix table to the body of the page
        document.body.appendChild(matrixTable);

        // If you are using DataTables to enhance the table, initialize it here
        // $(matrixTable).DataTable();
      })
      .catch(error => {
        console.error('There has been a problem with your fetch operation:', error);
        // Handle the error, maybe display a message to the user
      });
  });

  function getColorForSimilarity(similarity) {
    if (similarity > 20) return 'green';
    else if (similarity > 10) return 'orange';
    else return 'red';
  }