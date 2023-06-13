const identifiers = Array.from({length: 4}, (_, i) => i + 1)
const typeofactuators = [ "Bomba Peristàltica"]
let modelsbybrand = {
"Kamoer": ["KCM mini peristaltic pump 38~420ml/min"]
};

const dropdowns = [
  {
    id: "type",
    options: typeofactuators,
    disabled: false, 
  },
  {
    id: "Identificador",
    options: identifiers,
    disabled: false, 
  },
  {
    id: "marca",
    options: Object.keys(modelsbybrand),
    disabled: false,
  },
  {
    id: "model",
    options: "",
    disabled: true,
  },
];

function load_models(){
  const Marca = document.querySelector("#marca").value;
  const Model = document.querySelector("#model");
 
  Model.disabled = false;
  Model.length = 1;     
  Model.options[Model.options.length] = new Option("Model", " ", false, false);
  Model.options[1].hidden= true;


  for ( model  of modelsbybrand[Marca]) {

      Model.options[Model.options.length] = new Option(
      model,
      model
      );
  }
 
}
