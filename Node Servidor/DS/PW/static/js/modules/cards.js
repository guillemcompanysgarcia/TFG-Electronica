function addCard(form) {
    const card = createCardWithContent();
    const requiredFields = getRequiredFields(form);
    const conditionText = generateConditionText(requiredFields);
    const table = createTable(form, requiredFields, conditionText);
  
    card.querySelector(".card-content").appendChild(table);
    const cardsContainer = document.querySelector(".alarms-container");
    cardsContainer.appendChild(card);
    addButtons(card, cardsContainer);
  
    if (cardsContainer.children.length === 1) {
      addTitle();
    }
  }
  
  function addTitle() {
    const title = document.createElement("h2");
    title.textContent = "Configuració Alarmes";
    title.classList.add("alarms-title");
  
    const container = document.querySelector(".container");
    const alarmsContainer = document.querySelector(".alarms-container");
  
    container.insertBefore(title, alarmsContainer);
}
  
function removeTitle() {
    const title = document.querySelector(".alarms-title");
  
    if (title) {
      title.remove();
    }
}

function createCardWithContent() {
    const card = document.createElement("div");
    card.classList.add("card");
  
    const cardContent = document.createElement("div");
    cardContent.classList.add("card-content");
    card.appendChild(cardContent);
  
    return card;
}
  
function getRequiredFields(form) {
    let requiredFields = Array.from(form.querySelectorAll("input[required], select[required]"));
    const additionalCommentsInput = form.querySelector("input[name='Comentaris Addicionals']");
    if (additionalCommentsInput.value) {
      requiredFields.push(additionalCommentsInput);
    }
    return requiredFields;
}
  
function createTable(form, requiredFields, conditionText) {
    const table = document.createElement("table");
    table.classList.add("card-table");
    const alarmName = form.querySelector("input[name='Nom de l\\'Alarma']").value;
    const tableTitle = document.createElement("caption");
    tableTitle.textContent = alarmName;
    tableTitle.style.fontWeight = "bold"; // Add this line to make the title bold
    table.appendChild(tableTitle);
  
    let actuators = [];
    let actionRow;
  
    for (let i = 0; i < requiredFields.length; i++) {
      const field = requiredFields[i];
      if (shouldSkipField(field.name)) {
        continue;
      }
  
      if (field.name === "Actuador Associat") {
        actuators.push(field.value);
        continue;
      }
  
      const row = createTableRow(form, field, conditionText);
      if (field.name === "Acció") {
        actionRow = row;
      }
      table.appendChild(row);
    }
  
    if (actuators.length > 0) {
      const row = document.createElement("tr");
      const labelCell = document.createElement("td");
      labelCell.innerHTML = `<strong>${actuators.length > 1 ? "Actuadors Associats" : "Actuador Associat"}:</strong>`;
      const valueCell = document.createElement("td");
      valueCell.innerHTML = actuators.join("<br>");
      row.appendChild(labelCell);
      row.appendChild(valueCell);
  
      if (actionRow) {
        table.insertBefore(row, actionRow.nextSibling);
      } else {
        table.appendChild(row);
      }
    }
  
    return table;
}
  
  
function shouldSkipField(fieldName) {
    return fieldName.startsWith("Nom de l'Alarma") || fieldName.startsWith("Sensor Associat") || fieldName.startsWith("Operació") || fieldName.startsWith("Valor Llindar") || fieldName.startsWith("Nº cicles") || fieldName === "Interval comprovació (seg)";
}
  
function createTableRow(form, field, conditionText) {
    const row = document.createElement("tr");
    const labelCell = document.createElement("td");
    labelCell.innerHTML = `<strong>${field.placeholder || field.name}:</strong>`;
    const valueCell = document.createElement("td");
  
    if (field.name === "Desencadenant" && field.value === "Alarma recurrent") {
      const intervalInput = form.querySelector("input[name='Interval comprovació (seg)']");
      valueCell.textContent = `${field.value} (${intervalInput.value} segons)`;
    } else if (field.name === "Desencadenant" && field.value === "Quan es compleixi la condició") {
      valueCell.innerHTML = `${conditionText}`;
    } else {
      valueCell.textContent = field.value;
    }
  
    row.appendChild(labelCell);
    row.appendChild(valueCell);
    return row;
}
  
function addButtons(card, cardsContainer) {
    addDeleteButton(card);
    if (cardsContainer.children.length === 1) {
      addSaveChangesButton();
    }
}
  
function addDeleteButton(card) {
    const deleteButton = document.createElement("button");
    deleteButton.innerHTML = "&#10060;";
    deleteButton.classList.add("delete-card-button");
    deleteButton.classList.add("top-right");
    deleteButton.addEventListener("click", () => deleteCard(card));
    card.querySelector(".card-content").appendChild(deleteButton);
}
  
function addSaveChangesButton() {
    const saveChangesButton = document.createElement("button");
    saveChangesButton.textContent = "Guardar canvis";
    saveChangesButton.onclick = sendtoDevice;
    saveChangesButton.classList.add("save-changes-button");
  
    const saveChangesContainer = document.getElementById("saveChangesContainer");
    saveChangesContainer.appendChild(saveChangesButton);
}
  
function deleteCard(card) {
    const alarmsContainer = document.querySelector(".alarms-container");
  
    if (alarmsContainer.children.length === 1) {
      // If there's only one card left, remove the card and the "Guardar cambios" button
      alarmsContainer.removeChild(card);
      removeTitle();
      const saveChangesContainer = document.getElementById("saveChangesContainer");
      const saveChangesButton = saveChangesContainer.querySelector(".save-changes-button");
      saveChangesContainer.removeChild(saveChangesButton);
  
      // Send the data to the device
      sendtoDevice();
  
    } else {
      // Remove the card
      alarmsContainer.removeChild(card);
    }
  
    // Update the identifier options
    updateIdentifierOptions();
    enableDataElements();
} 
  
function addCard_Update(event, form) { //WIP
    event.preventDefault();
    addCard(form);
    resetAlarmsForm();
}
  
function resetAlarmsForm() {
    // Reset input elements
    document.getElementById('name').value = '';
    document.getElementById('Identificador').selectedIndex = -1;
    document.getElementById('action').selectedIndex = -1;
    document.getElementById('mode').selectedIndex = -1;
    document.getElementById('photoAction').selectedIndex = -1;
    document.getElementById('correlationAction').selectedIndex = -1;
    document.getElementById('sensorEmail').selectedIndex = -1;
    document.getElementById('lastNSamples').value = '';
    document.getElementById('triggerType').selectedIndex = -1;
    document.getElementById('period').value = '';
    document.getElementById('comments').value = '';
  
    // Obtain the containers of conditions and actuators
    let conditionsContainer = document.getElementById('conditionContainer');
    let actuatorContainer = document.getElementById('actuatorContainer');
  
    // Remove all conditions and actuators, except the first one (original)
    while (conditionsContainer.children.length > 1) {
      conditionsContainer.removeChild(conditionsContainer.lastChild);
    }
    
    while (actuatorContainer.children.length > 1) {
      actuatorContainer.removeChild(actuatorContainer.lastChild);
    }
  
    let actuatorselect = document.getElementById("actuators");
    actuatorselect.selectedIndex = -1;
    updateActuatorOptions();
    
    // Hide dynamic sections
    document.getElementById('actuatorContainer').style.display = 'none';
    document.getElementById('modeOptions').style.display = 'none';
    document.getElementById('photoOptions').style.display = 'none';
    document.getElementById('correlationOptions').style.display = 'none';
    document.getElementById('emailOptions').style.display = 'none';
    document.getElementById('periodContainer').style.display = 'none';
  
    // Call the respective functions to update the form
    showTriggerOptions();
    showActuatorOptions();
    updateIdentifierOptions();
}
  
function displayTablesFromJson(json) {
    const alarmsContainer = document.querySelector(".alarms-container");
    const alarmsData = JSON.parse(json);
  
    const loadingIcon = document.getElementById('loading-icon');
    alarmsData.forEach(alarm => {
      if (alarmsContainer.children.length < 1) {
        addTitle();
      }
      const card = createCardWithContent();
      const table = createTableFromAlarmData(alarm);
  
      card.querySelector(".card-content").appendChild(table);
      alarmsContainer.appendChild(card);
      addButtons(card, alarmsContainer);
    });
  
    loadingIcon.style.display = 'none';
  
    updateIdentifierOptions();
}
  
function createTableFromAlarmData(alarmData) {
    const table = document.createElement("table");
    table.classList.add("card-table");
    const tableTitle = document.createElement("caption");
    tableTitle.textContent = alarmData["Nom de l'Alarma"];
    tableTitle.style.fontWeight = "bold";
    table.appendChild(tableTitle);
  
    let actuators = [];
    let actionRow;
  
    for (const key in alarmData) {
      if (key === "Nom de l'Alarma" || key === "Interval" || key === "Condicions") {
        continue;
      }
    
      /*if (key === "Actuadors Associats") {
        actuators = alarmData[key];
        continue;
      }*/
      
      const row = createTableRowFromAlarmData(key, alarmData[key], alarmData);
      if (key === "Acció") {
        actionRow = row;
      }
      table.appendChild(row);
    }
  
    if (actuators.length > 0) {
      const row = document.createElement("tr");
      const labelCell = document.createElement("td");
      labelCell.innerHTML = `<strong>${actuators.length > 1 ? "Actuadors Associats" : "Actuador Associat"}:</strong>`;
      const valueCell = document.createElement("td");
      valueCell.innerHTML = actuators.join("<br>");
      row.appendChild(labelCell);
      row.appendChild(valueCell);
  
      if (actionRow) {
        table.insertBefore(row, actionRow.nextSibling);
      } else {
        table.appendChild(row);
      }
    }
  
    return table;
}
  
function createTableRowFromAlarmData(key, value, alarmData) {
    const row = document.createElement("tr");
    const labelCell = document.createElement("td");
    labelCell.innerHTML = `<strong>${key}:</strong>`;
    const valueCell = document.createElement("td");
  
    if (key === "Desencadenant" && value.startsWith("Alarma Recurrent")) {
      const intervalInput = alarmData["Interval"];
      valueCell.textContent = `Alarma Recurrent (${intervalInput})`;
    } else if (key === "Desencadenant" && value === "Condició") {
      const conditions = alarmData["Condicions"];
  
      const sensorDropdown = dropdowns.find(dropdown => dropdown.id === "sensor");
      const sensorOptions = sensorDropdown.options;
  
      // Check all conditions to see if sensors are configured in the system
      const allSensorsConfigured = conditions.every(condition => {
        let sensor = condition["Sensor Associat"];
        const matchingOption = sensorOptions.find(option => option.startsWith(sensor));
        return matchingOption !== undefined;
      });
  
      if (allSensorsConfigured) {
        // Generate conditions text
        valueCell.innerHTML = generateConditionText(conditions);
      } else {
        valueCell.innerHTML = generateConditionText(conditions) + " ⚠️ Un o més sensors associats amb l'alarma no estan configurats al sistema ⚠️";
      }
  
    } else if (key === "Actuadors Associats" || key === "Actuador Associat") {
      const actuators = Array.isArray(value) ? value : [value];
      const actuatorsObject = dropdowns.find(dropdown => dropdown.id === "actuators");
      const actuatorsOptions = actuatorsObject.options;
  
      // Check all actuators to see if they are configured in the system
      const allActuatorsConfigured = actuators.every(actuator => {
        const matchingOption = actuatorsOptions.find(option => option.startsWith(actuator));
        return matchingOption !== undefined;
      });
  
      if (allActuatorsConfigured) {
        valueCell.innerHTML = actuators.join(", ");
      } else {
        valueCell.innerHTML = actuators.join(", ") + " ⚠️ Un o més actuadors associats amb l'alarma no estan configurats al sistema ⚠️";
      }
    
  
    } else {
      valueCell.textContent = value;
    }
  
    row.appendChild(labelCell);
    row.appendChild(valueCell);
    return row;
}
  
  
function updateForm() {
    const allActuatorOptions = dropdowns.find(dropdown => dropdown.id === "actuators").options;
    const allSensorOptions = dropdowns.find(dropdown => dropdown.id === "sensor").options;
  
    const triggerTypeSelect = document.querySelector('#triggerType');
    const noSensorsConditionOption = triggerTypeSelect.querySelector('option[value="Quan es compleixi la condició"]');
    const actionSelect = document.querySelector('#action');
    const activateActuatorOption = actionSelect.querySelector('option[value="Activar actuador"]');
    const deactivateActuatorOption = actionSelect.querySelector('option[value="Desactivar actuador"]');
    const sendEmailOption = actionSelect.querySelector('option[value="Enviar un correu electrònic"]');
  
    if (allSensorOptions.length === 0) {
      noSensorsConditionOption.disabled = true;
      sendEmailOption.disabled = true;
    } else {
      noSensorsConditionOption.disabled = false;
      sendEmailOption.disabled = false;
    }
  
    if (allActuatorOptions.length === 0) {
      activateActuatorOption.disabled = true;
      deactivateActuatorOption.disabled = true;
    } else {
      activateActuatorOption.disabled = false;
      deactivateActuatorOption.disabled = false;
    }
}
  
function parseCondition(condition) {
  const sensorMatch = condition.match(/del\s+(.*?)\s+\((.*?)\)\s+\((.*?)\)/);
  const sensor = sensorMatch[1];
  const type = sensorMatch[2];
  const unit = sensorMatch[3];

  const comparisonMatch = condition.match(/(inferior|superior|igual)/);
  const comparison = comparisonMatch[1].charAt(0).toUpperCase() + comparisonMatch[1].slice(1);

  const thresholdMatch = condition.match(/a\s+(\d+)/);
  const threshold = thresholdMatch[1];

  const cyclesMatch = condition.match(/durant (\d+) cicle(s)?/);
  const cycles = `${cyclesMatch[1]}`;

  return {
    "Sensor Associat": sensor,
    "Tipus": type,
    "Comparació": comparison,
    "Valor Llindar": threshold,
    "Unitat": unit,
    "Nº cicles": cycles
  };
}
  
function tablesToJson(cardsContainer) {
  const cards = cardsContainer.children;
  const cardsData = [];

  for (let i = 0; i < cards.length; i++) {
    const card = cards[i];
    const tableRows = card.querySelectorAll(".card-table tr");
    const alarmName = card.querySelector(".card-table caption").innerText;
    const cardData = { "Nom de l'Alarma": alarmName };
    let hasWarning = false;

    for (let j = 0; j < tableRows.length; j++) {
      const row = tableRows[j];
      const key = row.querySelector("td:first-child strong").innerText.slice(0, -1); // Remove ':' at the end
      let value = row.querySelector("td:last-child").innerHTML;

      if (key.startsWith("Actuador")) {
        let [actuators, warning] = value.replace(/<br>/g, ", ").split('⚠️');
        cardData[key] = actuators.split(", ").map(actuator => actuator.trim());
      } else if (key === "Desencadenant") {
        cardData["Desencadenant"] = "Condició";
        if (value.startsWith("Si ")) {
          const conditions = value.split(/<br\s*\/?>/);
          cardData["Condicions"] = conditions.map(condition => {
            let [cleanCondition, warning] = condition.split('⚠️');
            cleanCondition = cleanCondition.trim();
            return parseCondition(cleanCondition);
          });
          continue;
        } else {
          const interval = value.match(/\((\d+)\ssegons\)/);
          if (interval) {
            cardData["Desencadenant"] = "Alarma Recurrent";
            cardData["Interval"] = `${interval[1]} segons`;
          }
        }
      } else {
        cardData[key] = value;
      }
    }
    cardsData.push(cardData);
  }

  return cardsData;
}

