const identifiers = Array.from({length: 4}, (_, i) => i + 1)
const sensorUnits = {
  "pH": ["pH"],
  "Conductivitat": ["μS/cm"],
  "ORP": ["mV"],
  "Oxigen dissolt": ["g/l"],
  "Temperatura": ["ºC"],
  "Humitat" : ["%HR"]
};

const intervals = [ "Cada 5 segons", "Cada 10 segons", "Cada 30 segons", "Cada minut"]

let adressesbyfunction = {
"Function 01 (Read Coil Status)": [00, 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18],
"Function 02 (Read Input Status)": [00, 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13],
"Function 03 (Read Holding Registers)": [00, 02, 04, 06, 08, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 
    36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72, 74, 76, 200, 202, 204, 206, 208, 
    210, 212, 214, 216, 218, 220, 222, 224, 226, 228, 230, 232, 234, 236, 238, 240, 242, 244, 246, 248, 250, 252, 
    254],
"Function 04 (Read Input Registers)": [00,  01, 02, 04, 06, 08, 10, 12, 14, 16, 18, 20, 22, 24, 26],
"Function 05 (Force Single Coil)": [00, 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15],
"Function 16 (Preset Multiple Registers)": [00, 02, 04, 06, 08, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34,
     36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72, 74, 76, 200, 202, 204, 206, 208, 
    210, 212, 214, 216, 218, 220, 222]
};

const dropdowns = [
  {
    id: "type",
    options: Object.keys(sensorUnits),
    disabled: false, 
  },
  {
    id: "Identificador",
    options: identifiers,
    disabled: false, 
  },
  {
    id: "unit",
    options: "",
    disabled: true, 
  },
  {
    id: "interval",
    options: intervals,
    disabled: false,
  },
  {
    id: "modbusfunc",
    options: Object.keys(adressesbyfunction),
    disabled: false,
  },
  {
    id: "address",
    options: "",
    disabled: true,
  },
];

function load_addresses(){
    const FuncioModbusTriada = document.querySelector("#modbusfunc").value;
    const Address = document.querySelector("#address");
    const num = document.querySelector("#number");
    Address.disabled = false;
    Address.length = 1;     
    Address.options[Address.options.length] = new Option("Direcció", " ", false, false);
    Address.options[1].hidden= true;
  
    const zeroPad = (num, places) => String(num).padStart(places, '0')
  
    for ( addr  of adressesbyfunction[FuncioModbusTriada]) {
        if(addr <= 9){
            addr = zeroPad(addr, 2);
        }
        Address.options[Address.options.length] = new Option(
        addr,
        addr
        );
    }
    num.value = '';
    num.disabled = false;
  }

function load_units() {
    const sensorType = document.querySelector("#type").value;
    const Unit = document.querySelector("#unit");
    Unit.disabled = false;
    Unit.length = 1;
    Unit.options[Unit.options.length] = new Option("Unitat", " ", false, false);
    Unit.options[1].hidden = true;
  
    const units = sensorUnits[sensorType];
  
    for (const unit of units) {
      Unit.options[Unit.options.length] = new Option(unit, unit);
    }
  }

