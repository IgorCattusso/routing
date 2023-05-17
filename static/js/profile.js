const currentPasswordShow = document.getElementById("currentPasswordShow");
const currentPasswordHide = document.getElementById("currentPasswordHide");
const newPasswordShow = document.getElementById("newPasswordShow");
const newPasswordHide = document.getElementById("newPasswordHide");
const newPasswordConfirmationShow = document.getElementById("newPasswordConfirmationShow");
const newPasswordConfirmationHide = document.getElementById("newPasswordConfirmationHide");

const currentPasswordInput = document.getElementById("currentPassword");
const newPasswordInput = document.getElementById("newPassword");
const newPasswordConfirmationInput = document.getElementById("newPasswordConfirmation");

const differentPasswordAlerts = document.querySelectorAll(".different-password-alert");

const saveButton = document.getElementById("save");

currentPasswordShow.addEventListener("click", function () {
    if (currentPasswordInput.type === "password") {
        currentPasswordInput.type = "text";
        currentPasswordShow.style.display = "none";
        currentPasswordHide.style.display = "block";
    } else {
        currentPasswordInput.type = "password";
        currentPasswordShow.style.display = "block";
        currentPasswordHide.style.display = "none";
    }
});

currentPasswordHide.addEventListener("click", function () {
    if (currentPasswordInput.type === "text") {
        currentPasswordInput.type = "password";
        currentPasswordHide.style.display = "none";
        currentPasswordShow.style.display = "block";
    } else {
        currentPasswordInput.type = "text";
        currentPasswordHide.style.display = "block";
        currentPasswordShow.style.display = "none";
    }
});

newPasswordShow.addEventListener("click", function () {
    if (newPasswordInput.type === "password") {
        newPasswordInput.type = "text";
        newPasswordShow.style.display = "none";
        newPasswordHide.style.display = "block";
    } else {
        newPasswordInput.type = "password";
        newPasswordShow.style.display = "block";
        newPasswordHide.style.display = "none";
    }
});

newPasswordHide.addEventListener("click", function () {
    if (newPasswordInput.type === "text") {
        newPasswordInput.type = "password";
        newPasswordHide.style.display = "none";
        newPasswordShow.style.display = "block";
    } else {
        newPasswordInput.type = "text";
        newPasswordHide.style.display = "block";
        newPasswordShow.style.display = "none";
    }
});

newPasswordConfirmationShow.addEventListener("click", function () {
    if (newPasswordConfirmationInput.type === "password") {
        newPasswordConfirmationInput.type = "text";
        newPasswordConfirmationShow.style.display = "none";
        newPasswordConfirmationHide.style.display = "block";
    } else {
        newPasswordConfirmationInput.type = "password";
        newPasswordConfirmationShow.style.display = "block";
        newPasswordConfirmationHide.style.display = "none";
    }
});

newPasswordConfirmationHide.addEventListener("click", function () {
    if (newPasswordConfirmationInput.type === "text") {
        newPasswordConfirmationInput.type = "password";
        newPasswordConfirmationHide.style.display = "none";
        newPasswordConfirmationShow.style.display = "block";
    } else {
        newPasswordConfirmationInput.type = "text";
        newPasswordConfirmationHide.style.display = "block";
        newPasswordConfirmationShow.style.display = "none";
    }
});

function validateRequiredFields() {
    if (currentPasswordInput.value !== '' || newPasswordInput.value !== '' || newPasswordConfirmationInput.value !== '') {
        if (currentPasswordInput.value === '' || newPasswordInput.value === '' || newPasswordConfirmationInput.value === '') {
            currentPasswordInput.required = true;
            newPasswordInput.required = true;
            newPasswordConfirmationInput.required = true;
        }
    }
    if (currentPasswordInput.value === '' && newPasswordInput.value === '' && newPasswordConfirmationInput.value === '') {
        currentPasswordInput.required = false;
        newPasswordInput.required = false;
        newPasswordConfirmationInput.required = false;
    }
}

currentPasswordInput.addEventListener('input', validateRequiredFields);

function differentPasswords() {
    differentPasswordAlerts.forEach(function (differentPasswordAlert) {
        differentPasswordAlert.style.display = "inline";
    });

    newPasswordInput.style.border = "2px solid red";
    newPasswordConfirmationInput.style.border = "2px solid red";

    saveButton.disabled = true;
    saveButton.style.cursor = "not-allowed";
}

function equalPasswords() {
    differentPasswordAlerts.forEach(function (differentPasswordAlert) {
        differentPasswordAlert.style.display = "none";
    });

    newPasswordInput.style.border = "none";
    newPasswordConfirmationInput.style.border = "none";

    saveButton.disabled = false;
    saveButton.style.cursor = "pointer";
}

newPasswordInput.addEventListener('input', function () {
    validateRequiredFields();

    if (newPasswordInput.value !== newPasswordConfirmationInput.value) {
        differentPasswords();
    }
    if (newPasswordInput.value === newPasswordConfirmationInput.value) {
        equalPasswords();
    }
});

newPasswordConfirmationInput.addEventListener('input', function () {
    validateRequiredFields();

    if (newPasswordConfirmationInput.value !== newPasswordInput.value) {
        differentPasswords();
    }
    if (newPasswordConfirmationInput.value === newPasswordInput.value) {
        equalPasswords();
    }
});


$('form input[type="file"]').change(event => {
  let arquivos = event.target.files;
  console.log(arquivos)
  if (arquivos.length === 0) {
    console.log('sem imagem pra mostrar')
  } else {
      if(arquivos[0].type === 'image/jpeg') {
        $('.img-fluid').remove();
        let imagem = $('<img class="img-fluid" alt="Imagem de perfil" id="userPhoto">');
        imagem.attr('src', window.URL.createObjectURL(arquivos[0]));
        $('figure').prepend(imagem);
      } else {
        alert('Formato não suportado')
      }
  }
});


const message = document.getElementById('messages');
function hideMessage() {
    if (message) {
        message.style.display = 'none';
    }
}

const delayInMilliseconds = 3000;
setTimeout(hideMessage, delayInMilliseconds);
