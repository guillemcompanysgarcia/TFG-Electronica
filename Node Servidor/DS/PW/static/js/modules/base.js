function initializePage(data) {
  updateTable(data);
  load_form_options();
  updateIdentifierOptions();
}

function get_headers_from_form(){
  const form = document.querySelector('form');
  var keys = [];
  for (var i = 0; i < form.elements.length; i++) {
    var element = form.elements[i];
    if (element.type !== "submit") {
      keys.push(element.name);
    }
  }
  return keys;
}

function createHeader() {
  const headersToAdd = get_headers_from_form();
  const additional_headersToAdd = ["Accions"]
  const allHeaders = [...new Set([...headersToAdd, ...additional_headersToAdd])];

  const table = document.createElement('table');
  table.setAttribute('id', 'mastertable');
  const thead = document.createElement('thead');
  const tr = document.createElement('tr');
  
  allHeaders.forEach(header => {
      const th = document.createElement('th');
      th.appendChild(document.createTextNode(header));
      tr.appendChild(th);
  });
  
  thead.appendChild(tr);
  table.appendChild(thead);
  
  const container = document.querySelector('#main');
  const mainDiv = document.createElement('div');
  let config_type = window.location.pathname.split('/').pop().split('_')[0];
  let pageTitle = 'Configuració ' + config_type;
  mainDiv.setAttribute('id', 'maindiv');
  mainDiv.innerHTML = `
      <h2>${pageTitle}</h2>
      <table id="mastertable">
          <thead>
              <tr>${allHeaders.map(header => `<th>${header}</th>`).join('')}</tr>
          </thead>
          <tbody id="tbody">
          </tbody>
      </table>
      <button id="sendbutton" onclick="sendtoDevice()">Guardar canvis</button>
  `;
  container.insertBefore(mainDiv, container.firstChild);
}
function sortTableRowsById() {
  const table = document.querySelector('#mastertable');
  if (table) {
    const tbody = table.querySelector('tbody');
    if (tbody) {
      const rows = Array.from(tbody.querySelectorAll('tr'));

      rows.sort((a, b) => {
        const idA = a.cells[1].innerText;
        const idB = b.cells[1].innerText;
        return idA.localeCompare(idB, undefined, {numeric: true});
      });

      // clear existing rows
      while (tbody.firstChild) {
        tbody.firstChild.remove();
      }

      // re-add rows in sorted order
      rows.forEach(row => tbody.appendChild(row));
    }
  }
}

function updateTable(stringData) {
  if (stringData !== "[]" && stringData !== "None") {
    const table = document.querySelector("#mastertable");

    if (table === null) {
      createHeader();
    }

    const sensorsObject = JSON.parse(stringData);

    sensorsObject.forEach((obj) => {
      addRow(obj);
    });
  }
}

function addRowFromFormAndUpdate(event, form) {
  event.preventDefault();
  
  const obj = getDataFromForm(form);
  
  addRow(obj);
  
  updateIdentifierOptions();

}

function getDataFromForm(form){
  const formData = new FormData(form);
  const obj = {};
  for (let key of formData.keys()) {
    obj[key] = formData.get(key);
  }
  return obj;
}

function addRow(obj) {
  if (!document.querySelector('#mastertable')) {
    createHeader();
  }

  const dataKeys = Object.keys(obj);
  let tbodyRef = document.querySelector('#mastertable tbody');
  if (!tbodyRef) {
    const table = document.getElementById('mastertable');
    tbodyRef = table.appendChild(document.createElement('tbody'));
  }

  const newRow = tbodyRef.insertRow(-1);

  for (const key of dataKeys) {
    const newCell = newRow.insertCell();
    const newdata = obj[key] !== undefined && obj[key] !== null ? obj[key] : document.getElementById(key).value;
    newCell.appendChild(document.createTextNode(newdata));
  }
  
  const newCell = newRow.insertCell();
  const newbutton = document.createElement('button');
  newbutton.innerHTML = "&#10060;";
  newbutton.classList.add("delete-row-button");
  newbutton.onclick = () => deleteRowAndUpdate(newbutton);
  newCell.appendChild(newbutton);

  sortTableRowsById();
}

function deleteRowAndUpdate(btn) {
  deleteRow(btn);
  updateIdentifierOptions();
  enableDataElements();
}

function deleteRow(btn) {
  const table = document.getElementById('mastertable');
  const count = table.rows.length;
  if (count === 2) {
    const mainDiv = document.getElementById('maindiv');
    if (mainDiv) {
      mainDiv.parentNode.removeChild(mainDiv);
    }
    sendtoDevice();
  } else {
    const row = btn.parentNode.parentNode;
    row.parentNode.removeChild(row);
  }
}

function getDisabledFields(configType) {
  switch (configType) {
    case 'sensors':
      return {
        'Unitat': 'Unitat',
        'Adreça': 'Adreça',
        'NºRegistres': 'NºRegistres'
      };
    case 'actuators':
      return {
        'Model': 'Model'
      };
    default:
      return {};
  }
}

function getClientNameAndConfigType() {
  const parts = window.location.pathname.split('/');
  const clientName = parts[2];
  const configType = parts.pop().split('_')[0];

  return { clientName, configType };
}

function enableDataElements() {
  const { configType } = getClientNameAndConfigType();
  const placeholders = getDisabledFields(configType);

  document.querySelector('form').reset();

  document.querySelectorAll('#data input, #data select, #data button').forEach(el => { 
    el.disabled = false;

    if (placeholders[el.name]) {
      if (el.tagName === 'SELECT') {
        el.innerHTML = `<option value="" disabled selected hidden>${placeholders[el.name]}</option>`;
      } else if (el.tagName === 'INPUT') {
        el.placeholder = placeholders[el.name];
      }
      el.disabled = true;
    }
  });
}

function showAlert(message, alertType) {
  const alertWrapper = document.createElement('div');
  alertWrapper.classList.add('alert-wrapper');

  const alertBox = document.createElement('div');
  alertBox.classList.add('alert', alertType);
  alertBox.textContent = message;

  alertWrapper.appendChild(alertBox);
  document.body.appendChild(alertWrapper);

  setTimeout(() => {
    alertWrapper.remove();
  }, 3000);
}

function sendtoDevice() {
  const { clientName, configType } = getClientNameAndConfigType();
  const table = document.getElementById("mastertable");
  const alarmsContainer = document.querySelector(".alarms-container");
  let data = "[]";

  if (table) {
    data = JSON.stringify(tableToJson(table));
  } else if (alarmsContainer) {
    data = JSON.stringify(tablesToJson(alarmsContainer));
  }

  const saveRequest = new XMLHttpRequest();
  saveRequest.open('POST', `/download/${clientName}/${configType}`);
  saveRequest.setRequestHeader('Content-Type', 'application/json');
  saveRequest.send(data);
  saveRequest.onload = function() {
    if (saveRequest.status === 200) {
      showAlert("Configuració guardada correctament", "alert-success");
    } else {
      showAlert("Error enviant la configuració al dispositiu", "alert-danger");
    }
  }
}

function tableToJson(table) {
  if (!table || !table.rows || table.rows.length === 0) {
    return [];
  }

  const headers = get_headers_from_form();
  const data = [];

  for (let i = 1; i < table.rows.length; i++) {
    const tableRow = table.rows[i];
    const rowData = {};

    for (let j = 0; j < headers.length; j++) {
      rowData[headers[j]] = tableRow.cells[j].innerHTML;
    }

    data.push(rowData);
  }

  return data;
}

function load_form_options() {
  for (const dropdown of dropdowns) {
    const select = document.querySelector(`#${dropdown.id}`);
    const options = Array.isArray(dropdown.options) ? dropdown.options.reduce((acc, cur) => ({...acc, [cur]: cur}), {}) : dropdown.options;

    for (const [optionValue, optionText] of Object.entries(options)) {
      const option = new Option(optionText, optionValue);
      select.add(option);
    }
    
    if (dropdown.disabled) {
      select.disabled = true;
    }
  }
}

function disableForm() {
  document.querySelectorAll('#data input, #data select, #data button').forEach(el => el.disabled = true);
}

function createOption(value, text) {
  const option = document.createElement("option");
  option.value = value;
  option.text = text;
  return option;
}

function updateIdentifierOptions() {
  const identifierSelect = document.querySelector("#Identificador");
  const mastertable = document.getElementById("mastertable");
  const usedIdentifiers = mastertable
    ? Array.from(document.querySelectorAll('#mastertable td:nth-child(2)'), td => parseInt(td.textContent, 10))
    : Array.from(document.querySelectorAll('.card-table tr:nth-child(2) td:last-child'), td => parseInt(td.textContent.trim(), 10));

  const availableIdentifiers = identifiers.filter(id => !usedIdentifiers.includes(id));

  // Clear the select options
  identifierSelect.innerHTML = '<option value="" disabled selected hidden>Identificador</option>';

  // Add available identifiers as options
  availableIdentifiers.forEach(id => identifierSelect.add(createOption(id, id)));

  // Disable form if no identifiers are left
  if (availableIdentifiers.length === 0) {
    disableForm();
  }
}