function addToList(number, name, denomination, rebate, cardNumber) {
  $.ajax({
    url: "/addToList/",
    data: {
      Number: number,
      Name: name,
      Denomination: denomination,
      Rebate: rebate,
      CNumber: cardNumber,
    },
    method: "post",
    success: (response) => {
      if (response.status) {
        alertify.success("Added Successfully");
      } else {
        alertify.error("Account already added");
      }
    },
  });
}
function rebateFunction(number, trigger) {
  let currentValue = parseInt(document.getElementById(number).innerHTML);
  $.ajax({
    url: "/rebateFunction",
    data: {
      number: number,
      currentValue: currentValue,
      trigger: trigger,
    },
    method: "POST",
    success: (response) => {
      if (response.rebate.successStatus) {
        document.getElementById(number).innerHTML = currentValue + trigger;
        document.getElementById("total").innerHTML = response.total;
      }
      if (response.rebate.falseAttempt) {
        alertify.alert("Cannot Set Rebate value to 0", function () {});
      }
    },
  });
}
function deleteFromList(number) {
  alertify.confirm(
    "Delete ",
    "Confirm Delete",
    function () {
      $.ajax({
        url: "/deleteFromList",
        data: {
          Number: number,
        },
        method: "post",
        success: (response) => {
          if (response.deleteStatus) {
            location.reload();
            alertify.success(Deleted);
          }
        },
      });
    },
    function () {}
  );
}
function genarateList() {
  let buttonState = document.getElementById("genarateBtn");
  buttonState.className = "btn btn-danger";
  buttonState.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...`;
  buttonState.disabled = true;
  $.ajax({
    url: "/genarateList",
    method: "get",
    success: (data) => {
      if (data) {
        alertify.alert(`List Number is : ${data}`, function () {
          window.location.href = "/final";
        });
      }
    },
  });
}
function showPassword(oldPass, newPass, cNewPass) {
  let oldPassword = document.getElementById(oldPass);
  let newPassword = document.getElementById(newPass);
  let confirmPassword = document.getElementById(cNewPass);
  if (
    oldPassword.type === "password" &&
    newPassword.type === "password" &&
    confirmPassword.type === "password"
  ) {
    oldPassword.type = "text";
    newPassword.type = "text";
    confirmPassword.type = "text";
  } else {
    oldPassword.type = "password";
    newPassword.type = "password";
    confirmPassword.type = "password";
  }
}
function passwordCheck(newPass, cNewPass, messageTag, buttonStatus) {
  let password = document.getElementById(newPass);
  let confirm = document.getElementById(cNewPass);
  let message = document.getElementById(messageTag);
  let buttonState = document.getElementById(buttonStatus);
  if (password.value == confirm.value) {
    confirm.style.backgroundColor = "#66cc66";
    message.style.color = "#66cc66";
    message.innerHTML = "Password Match";
    buttonState.disabled = false;
  } else {
    confirm.style.backgroundColor = "#ff6666";
    message.innerHTML = "Password Does Not Match";
    buttonState.disabled = true;
  }
}
function converter(fname) {
  fname = fname.substring(0, fname.length - 4);
  console.log(fname);

  $.ajax({
    url: "/convertxls",
    data: {
      FName: fname,
    },
    method: "post",
    success: () => {
      window.location.href = "/viewlist";
    },
  });
}
function formatXlsx(fname) {
  console.log(fname);
  alertify.prompt(
    "Date and List Data..",
    "",
    "",
    function (evt, value) {
      $.ajax({
        url: "/formatxlsx",
        data: {
          FName: fname,
          addData: value,
        },
        method: "post",
        success: (data) => {
          console.log(data);
          alertify.success(data);
        },
      });
    },
    function () {
      alertify.error("Cancel");
    }
  );
}
