document.addEventListener('DOMContentLoaded', async () => {
    try {
        const specifications = await fetchSpecifications('/api/specifications');
        populateSpecifications(specifications);
    } catch (error) {
        console.error('Error loading the specifications:', error);
    }
});

// Fetch specifications from the server
async function fetchSpecifications(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
}

function createCollapsibleElement(headerContent, headerType) {
    const containerDiv = document.createElement('div');
    const header = document.createElement(headerType);
    const contentDiv = document.createElement('div');

    header.textContent = headerContent;
    header.className = 'collapsible-header';

    // Pfeil-Element hinzufügen
    const arrow = document.createElement('span');
    arrow.innerHTML = '&#9660;'; // Unicode für nach unten zeigenden Pfeil
    arrow.className = 'collapsible-arrow';
    header.insertBefore(arrow, header.firstChild);

    header.addEventListener('click', function () {
        // Umschalten der aktiven Klasse
        contentDiv.classList.toggle('active');
        // Pfeil-Rotation umschalten
        arrow.classList.toggle('rotated');
    });
    contentDiv.className = 'collapsible-content';

    containerDiv.appendChild(header);
    containerDiv.appendChild(contentDiv);

    // Set up the click handler to toggle the collapsible content
    header.addEventListener('click', function () {
        this.classList.toggle('active');
        const content = this.nextElementSibling;
        if (content.style.display === 'block') {
            content.style.display = 'none';
        } else {
            content.style.display = 'block';
        }
    });

    return { containerDiv, contentDiv };
}

function populateSpecifications(specifications) {
    const specContainer = document.getElementById('specifications-container');
    const fragments = document.createDocumentFragment();

    const groupedByCategory = groupBy(specifications, spec => spec.categories[0]);

    Object.entries(groupedByCategory).forEach(([category, specs]) => {
        const { containerDiv: categoryDiv, contentDiv: categoryContentDiv } = createCollapsibleElement(category, 'h3');
        categoryDiv.className = 'category';

        const groupedByType = groupBy(specs, spec => spec.types[0]);

        Object.entries(groupedByType).forEach(([type, specs]) => {
            const { containerDiv: typeDiv, contentDiv: typeContentDiv } = createCollapsibleElement(type, 'h4');
            typeDiv.className = 'type';

            specs.forEach(spec => {
                const specDiv = createSpecificationDiv(spec);
                typeContentDiv.appendChild(specDiv);
            });

            categoryContentDiv.appendChild(typeDiv);
        });

        fragments.appendChild(categoryDiv);
    });

    specContainer.appendChild(fragments);
}

function groupBy(array, keyGetter) {
    return array.reduce((acc, item) => {
        const key = keyGetter(item);
        if (!acc[key]) {
            acc[key] = [];
        }
        acc[key].push(item);
        return acc;
    }, {});
}


function createDivElement(className, headerContent, headerType) {
    const div = document.createElement('div');
    div.className = className;
    const header = document.createElement(headerType);
    header.textContent = headerContent;
    div.appendChild(header);
    return div;
}


function createSpecificationDiv(spec) {
    const specDiv = document.createElement('div');
    specDiv.className = 'specification';

    const checkbox = createCheckbox(spec);
    const label = createLabel(spec);
    const select = createSelect(spec);

    specDiv.appendChild(checkbox);
    specDiv.appendChild(label);
    specDiv.appendChild(select);

    return specDiv;
}

function createCheckbox(spec) {
    const id = getIdFromName(spec.name);
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = `check-${id}`;
    checkbox.dataset.specName = spec.name;
    checkbox.onchange = toggleSelectEnabled;

    return checkbox;
}

function createLabel(spec) {
    const id = getIdFromName(spec.name);
    const label = document.createElement('label');
    label.htmlFor = `check-${id}`;
    label.textContent = spec.name;

    return label;
}

function createSelect(spec) {
    const id = getIdFromName(spec.name);
    const select = document.createElement('select');
    select.id = `select-${id}`;
    select.disabled = true;
    select.dataset.specName = spec.name;

    spec.versions.forEach((version, index) => {
        const option = new Option(version, spec.ids[index]);
        select.add(option);
    });

    return select;
}

function toggleSelectEnabled(event) {
    const specName = getIdFromName(event.target.dataset.specName);
    const select = document.getElementById(`select-${specName}`);
    select.disabled = !event.target.checked;
}

function getSelectedSpecifications() {
    return Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
        .map(checkbox => {
            const selectElement = document.getElementById(`select-${getIdFromName(checkbox.dataset.specName)}`);
            return selectElement.value;
        });
}

function showMessage(message) {
    const messageElement = document.getElementById('specMessage');
    messageElement.textContent = message;
    messageElement.classList.add('visible');
  }
  
  function hideMessage() {
    const messageElement = document.getElementById('specMessage');
    messageElement.classList.remove('visible');
  }
  
  function redirectToMatrix(event) {
    event.preventDefault();
    const selectedSpecs = getSelectedSpecifications();
  
    if (selectedSpecs.length < 2) {
      showMessage('Bitte wähle mindestens zwei Spezifikationen zum Vergleichen aus.');
      // Wait for 3 seconds before fading out
      setTimeout(hideMessage, 3000);
    } else {
      const queryString = selectedSpecs.map(id => `ids=${id}`).join('&');
      window.location.href = `matrix.html?${queryString}`;
    }
  }
  

function getSelectedSpecificationsQueryString() {
    return Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
        .map(checkbox => {
            const selectElement = document.getElementById(`select-${getIdFromName(checkbox.dataset.specName)}`);
            return `ids=${selectElement.value}`;
        })
        .join('&');
}

function getIdFromName(name) {
    return name.replace(/\s+/g, '');
}
