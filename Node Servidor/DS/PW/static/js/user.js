function showForm(field) {
    var valueEl = document.getElementById(field);
    var value = valueEl.innerHTML;
    var form = document.getElementById('edit-form');
    var inputField = form.querySelector('#field');
    var inputValue = form.querySelector('#value');
    inputField.value = field;
    inputValue.value = value;
    form.style.display = 'block';
  }
  
  function hideForm() {
    var form = document.getElementById('edit-form');
    form.style.display = 'none';
  
    // Find all edit buttons and remove .edit-btn-active class
    var editBtns = document.querySelectorAll('.edit-btn');
    editBtns.forEach(function(btn) {
      btn.classList.remove('edit-btn-active');
    });
  }
  
  
  function toggleForm(field) {
    var form = document.getElementById('edit-form');
    var valueInput = form.querySelector('#value');
    var clickedBtn = event.target;
    
    // If the clicked button is already active, hide the form and remove the active class
    if (clickedBtn.classList.contains('edit-btn-active')) {
      hideForm();
    }
    // If a different button is clicked, update the form and change the active button
    else if (form.style.display === 'none' || field !== valueInput.value) {
      showForm(field);
      // Find all edit buttons and remove .edit-btn-active class
      var editBtns = document.querySelectorAll('.edit-btn');
      editBtns.forEach(function(btn) {
        btn.classList.remove('edit-btn-active');
      });
      clickedBtn.classList.add('edit-btn-active');
      
      // Find the previously active button and remove the active class

    }
  }
  
  
  