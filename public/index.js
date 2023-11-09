document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/specifications')
      .then(response => response.json())
      .then(specifications => {
        const specContainer = document.getElementById('specifications-container');
        specifications.forEach(spec => {
            console.log(spec)
          // Erstelle ein Container-Div für jede Spezifikation
          const specDiv = document.createElement('div');
          specDiv.className = 'specification';
  
          // Checkbox für die Spezifikation
          const checkbox = document.createElement('input');
          checkbox.type = 'checkbox';
          checkbox.id = 'check-' + spec.name.replace(/\s+/g, ''); // Verwende spec.name für die ID und entferne Leerzeichen
          checkbox.dataset.specName = spec.name; // Verwende spec.name für das dataset
          checkbox.onchange = handleCheckboxChange; // Funktion zum Verarbeiten der Auswahl
  
          // Label für die Checkbox
          const label = document.createElement('label');
          label.htmlFor = 'check-' + spec.name.replace(/\s+/g, ''); // Verwende spec.name für das Label und entferne Leerzeichen
          label.textContent = spec.name;
  
          // Dropdown-Menü für die Versionen
          const select = document.createElement('select');
          select.id = 'select-' + spec.name.replace(/\s+/g, ''); // Verwende spec.name für die ID und entferne Leerzeichen
          select.disabled = true; // Anfangs deaktiviert, wird durch Checkbox aktiviert
          select.dataset.specName = spec.name; // Verwende spec.name für das dataset
  
          // Optionen für das Dropdown-Menü
          spec.versions.forEach((version, index) => {
            // Erstelle eine Option für jede Version und setze die ID als Wert
            const option = new Option(version, spec.ids[index]);
            select.add(option);
          });
  
          // Hinzufügen der Elemente zum Container-Div
          specDiv.appendChild(checkbox);
          specDiv.appendChild(label);
          specDiv.appendChild(select);
  
          // Hinzufügen des Container-Divs zum Hauptcontainer
          specContainer.appendChild(specDiv);
        });
      })
      .catch(error => {
        console.error('Error loading the specifications:', error);
      });
  });
  
  function handleCheckboxChange(event) {
    // Hole den Namen der Spezifikation aus den Daten-Attributen der Checkbox
    const specName = event.target.dataset.specName;
    // Aktiviere oder deaktiviere das entsprechende Dropdown-Menü
    const select = document.getElementById('select-' + specName.replace(/\s+/g, ''));
    select.disabled = !event.target.checked;
  }
  
  function redirectToMatrix(event) {
    event.preventDefault(); // Verhindere das normale Absenden des Formulars.
  
    // Sammle alle ausgewählten Spezifikations-IDs.
    const selectedSpecs = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
      .map(checkbox => {
        const selectElement = document.getElementById('select-' + checkbox.dataset.specName.replace(/\s+/g, ''));
        return selectElement.value;
      });

    // Erstelle eine Abfragezeichenkette mit den ausgewählten IDs.
    const queryString = selectedSpecs.map(id => `ids=${id}`).join('&');
    console.log("queryString",queryString )
    // Leite den Benutzer an die matrix.html Seite weiter, inklusive der Abfragezeichenkette.
    window.location.href = `matrix.html?${queryString}`;
  }