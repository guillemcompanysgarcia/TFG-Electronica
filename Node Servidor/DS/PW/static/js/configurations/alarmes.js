
const identifiers = Array.from({length: 5}, (_, i) => i + 1)
const actions = {
  "Activar actuador": "Activar actuador",
  "Desactivar actuador": "Desactivar actuador",
  "Prendre una fotografia": "Prendre una fotografia",
  "Enviar un correu electrònic": "Enviar un correu electrònic"
};

const dropdowns = [
  {
    id: "sensor",
    options: [],
    disabled: true,
  },
  {
    id: "actuators",
    options: [],
    disabled: true,
  },
  {
    id: "Identificador",
    options: identifiers,
    disabled: false, 
  },
  {
    id: "action",
    options: actions,
    disabled: false,
  },
  {
    id: "sensorEmail",
    options: [],
    disabled: true,
  },
];

function extractUnit(sensorString) {
  const match = sensorString ? sensorString.match(/\(([^)]+)\)/g) : null;
  return match && match.length > 0 ? match[match.length - 1].slice(1,-1) : '';
}

function generateConditions(input) {
  const sensorDropdown = dropdowns.find(dropdown => dropdown.id === "sensor");
  const sensorOptions = sensorDropdown.options;

  if (input[0] && input[0].name) {
    return input.reduce((acc, field) => {
      if (field.name.startsWith("Sensor Associat")) {
        acc.push({
          sensor: field.value,
          operation: "",
          threshold: "",
          numCycles: ""
        });
      } else if (field.name.startsWith("Operació")) {
        acc[acc.length - 1].operation = field.value.toLowerCase();
      } else if (field.name.startsWith("Valor Llindar")) {
        const numericValue = field.value.match(/\d+\.?\d*/)[0];
        const unit = extractUnit(acc[acc.length - 1].sensor);
        acc[acc.length - 1].threshold = numericValue + ' ' + unit;
      } else if (field.name.startsWith("Nº cicles")) {
        acc[acc.length - 1].numCycles = field.value;
      }
      return acc;
    }, []);
  } else {
    return input.map(condition => {
      const sensorInDropdown = sensorOptions.find(option => option.startsWith(condition["Sensor Associat"]));
      const sensor = sensorInDropdown 
          ? sensorInDropdown 
          : `${condition["Sensor Associat"]} (${condition["Tipus"]}) (${condition["Unitat"]})`;
      const unit = condition["Unitat"];
      return {
        sensor: sensor,
        operation: condition["Comparació"].toLowerCase(),
        threshold: condition["Valor Llindar"]  + ' ' + unit,
        numCycles: condition["Nº cicles"]
      };
    });
  }
}


function generateConditionText(input) {

  const conditions = generateConditions(input);
  let conditionText = "";
  conditions.forEach((condition, index) => {
    conditionText += `Si el valor del ${condition.sensor} és ${condition.operation} a ${condition.threshold} durant `;
    if (condition.numCycles > 1) {
      conditionText += `${condition.numCycles} cicles`;
    } else {
      conditionText += `${condition.numCycles} cicle`;
    }
    if (index < conditions.length - 1) {
      conditionText += ",<br> ";
    } else {
      conditionText += ".";
    }
  });

  return conditionText;
}

function updateThresholdPlaceholder(condition) {
  const sensorSelect = condition.querySelector("#sensor");
  const thresholdInput = condition.querySelector("#threshold");
  const selectedSensor = sensorSelect.options[sensorSelect.selectedIndex].text;
  const placeholderText = sensorSelect.selectedIndex === 0 
      ? "Llindar" 
      : "Llindar (" + extractUnit(selectedSensor) + ")";
  thresholdInput.placeholder = placeholderText;
}

async function getSensorAndActuatorNames(callback) {
  const client_name = window.location.pathname.split('/')[2];
  const response = await fetch(`/get_sensors_and_actuators/${client_name}`);
  if (response.ok) {
    const data = await response.json();
    dropdowns[0].options = data.sensors;
    dropdowns[0].disabled = data.sensors.length === 0;
    dropdowns[1].options = data.actuators;
    dropdowns[1].disabled = data.actuators.length === 0;
    dropdowns[4].options = data.sensors;
    dropdowns[4].disabled = data.sensors.length === 0;

    if (typeof callback === "function") {
      callback(data);
    }
    return { sensors: data.sensors, actuators: data.actuators };
  }
  console.error('Failed to fetch sensor and actuator names');
  return { sensors: [], actuators: [] };
}

function updateActuatorOptions() {
  const actuators = Array.from(document.querySelectorAll(".actuatorSelect"));
  const selectedActuators = actuators.map(actuator => actuator.value);
  const allActuatorOptions = dropdowns.find(dropdown => dropdown.id === "actuators").options;

  actuators.forEach((actuator, i) => {
    const currentActuator = actuator.value;
    const availableOptions = allActuatorOptions.filter(opt => !selectedActuators.includes(opt) || opt === currentActuator);

    actuator.innerHTML = "";
    if (!availableOptions.includes(currentActuator)) {
      let placeholder = document.createElement("option");
      placeholder.value = "";
      placeholder.text = "Actuador Associat";
      placeholder.disabled = true;
      placeholder.selected = true;
      placeholder.hidden = true;
      actuator.appendChild(placeholder);
    }
    availableOptions.forEach(option => {
      let opt = document.createElement("option");
      opt.value = option;
      opt.text = option;
      if (option === currentActuator) {
        opt.selected = true;
      }
      actuator.appendChild(opt);
    });
  });
}

function showHideContainers(containers, value) {
  containers.forEach(container => container.style.display = value);
}

function showActuatorOptions() {
  const action = document.getElementById("action").value;
  const inputFields = ["actuators", "mode", "photoAction", "sensorEmail", "lastNSamples", "correlationAction"].map(id => document.getElementById(id));
  const containers = ["actuatorContainer", "modeOptions", "photoOptions", "emailOptions", "correlationOptions"].map(id => document.getElementById(id));
  
  inputFields.forEach(field => {
    field.required = false;
    field.selectedIndex = 0;
  });
  showHideContainers(containers, "none");

  switch(action) {
    case "Activar actuador":
    case "Desactivar actuador":
      showHideContainers([containers[0]], "block");
      inputFields[0].required = true;
      if (action === "Activar actuador") {
        containers[1].style.display = "block";
        inputFields[1].required = true;
      }
      break;
    case "Prendre una fotografia":
      showHideContainers([containers[2]], "block");
      inputFields[2].required = true;
      break;
    case "Enviar un correu electrònic":
      showHideContainers([containers[3]], "block");
      inputFields[3].required = true;
      inputFields[4].required = true;
      break;  
  }
  
  handlePhotoChange();
}

function handlePhotoChange() {
  const actionSelect = document.getElementById("photoAction");
  const correlationOptions = document.getElementById("correlationOptions");
  const correlationActionSelect = document.getElementById("correlationAction");

  if (actionSelect.value === "Fer correlació de la mescla") {
    correlationOptions.style.display = "block";
    correlationActionSelect.required = true;  
  } else {
    correlationOptions.style.display = "none";
    correlationActionSelect.required = false;
    correlationActionSelect.selectedIndex = 0;
  }
}

function showTriggerOptions() {
  let triggerType = document.getElementById("triggerType");
  let periodContainer = document.getElementById("periodContainer");
  let conditionContainer = document.getElementById("conditionContainer");
  let addConditionButton = document.getElementById("addConditionButton");

  // Hide all condition elements
  const conditionElements = conditionContainer.querySelectorAll('.conditionDiv');
  conditionElements.forEach(conditionElement => {
    conditionElement.style.display = 'none';
  });

  
  // Remove required attribute for all condition divs
  conditionElements.forEach(conditionElement => {
    conditionElement.querySelector("#sensor").required = false;
    conditionElement.querySelector("#operation").required = false;
    conditionElement.querySelector("#threshold").required = false;
    conditionElement.querySelector("#numCycles").required = false;
  });
  document.getElementById("period").required = false;


  if (triggerType.value === "Alarma recurrent") {
    periodContainer.style.display = "block";
    addConditionButton.style.display = "none";
    // Set required attribute for period input
    while (conditionContainer.children.length > 1) {
      conditionContainer.removeChild(conditionContainer.lastChild);
    }
    // Reset the input values in the remaining condition element
    const firstConditionElement = conditionContainer.querySelector('.conditionDiv');
    firstConditionElement.querySelector("#sensor").value = "";
    firstConditionElement.querySelector("#operation").value = "";
    firstConditionElement.querySelector("#threshold").value = "";
    firstConditionElement.querySelector("#numCycles").value = "";
    document.getElementById("period").required = true;

  } else if (triggerType.value === "Quan es compleixi la condició") {
    periodContainer.style.display = "none";
    // Show all condition elements and add required attribute
    conditionElements.forEach(conditionElement => {
      conditionElement.style.display = 'block';
      conditionElement.querySelector("#sensor").required = true;
      conditionElement.querySelector("#operation").required = true;
      conditionElement.querySelector("#threshold").required = true;
      conditionElement.querySelector("#numCycles").required = true;
    });
    addConditionButton.style.display = "inline";
  } else {
    periodContainer.style.display = "none";
    addConditionButton.style.display = "none";
  }
}

function addCondition() {
  const conditionContainer = document.getElementById("conditionContainer");
  const condition = document.getElementById("condition");
  const conditions = document.getElementsByClassName("conditionWrapper");

  if (conditions.length >= 2) {
    showAlert("Ha arribat al límit de condicions simultànees.", "alert-warning");
    return;
  }
  let clonedCondition = condition.cloneNode(true);
  clonedCondition.style.display = "block";
  clonedCondition.classList.add("conditionWrapper");

  // Establece la opción del select clonado en el placeholder para el sensor
  const clonedSensorSelect = clonedCondition.querySelector("#sensor");
  clonedSensorSelect.value = "";

  const clonedThresholdInput = clonedCondition.querySelector("#threshold");
  clonedThresholdInput.placeholder = "Llindar";
  clonedThresholdInput.value = "";

  const clonedCyclesInput = clonedCondition.querySelector("#numCycles");
  clonedCyclesInput.placeholder = "Nº cicles";
  clonedCyclesInput.value = "";

  // Set the onchange event for the clonedSensorSelect to call updateThresholdPlaceholder with the clonedCondition
  clonedSensorSelect.onchange = function() {
    updateThresholdPlaceholder(clonedCondition);
  };

  const clonedButton = clonedCondition.querySelector("button");
  clonedButton.innerHTML = "&#10060;";
  clonedButton.onclick = function () {
    conditionContainer.removeChild(clonedCondition);
  };

  conditionContainer.appendChild(clonedCondition);
}

function removeCondition(button) {
  let conditions = document.getElementsByClassName("conditionDiv");
  if (conditions.length <= 1) {
      showAlert("És necessari definir com a mínim una condició.", "alert-warning");
      return;
  }
  let parentDiv = button.parentNode;
  parentDiv.remove();
}

function addActuator() {
  const actuatorContainer = document.getElementById("actuatorContainer");
  const actuatorOptions = document.getElementById("actuatorOptions");
  const actuators = document.getElementsByClassName("actuatorSelect");

  const actuatorsObject = dropdowns.find(dropdown => dropdown.id === "actuators");
  const numActuators = actuatorsObject.options.length;

  if (actuators.length >= numActuators) {
    showAlert("Ha arribat al límit d'actuadors definits al sistema.", "alert-warning");
    return;
  }

  let clonedActuator = actuatorOptions.cloneNode(true);
  clonedActuator.classList.add("actuatorWrapper");

  // Establece la opción del select clonado en el placeholder
  const clonedSelect = clonedActuator.querySelector(".actuatorSelect");
  clonedSelect.value = "";

  const clonedButton = clonedActuator.querySelector("button");
  clonedButton.innerHTML = "&#10060;";
  clonedButton.onclick = function () {
    removeActuator(clonedButton);
  };

  actuatorContainer.appendChild(clonedActuator);
  updateActuatorOptions();
}

function removeActuator(button) {
  let actuators = document.getElementsByClassName("actuatorSelect");
  if (actuators.length <= 1) {
      showAlert("És necessari configurar un actuador per dur a terme aquesta acció.", "alert-warning");
      return;
  }
  let parentDiv = button.parentNode;
  parentDiv.remove();
  updateActuatorOptions();
}
