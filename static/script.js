document.addEventListener("DOMContentLoaded",function(){
    let selectElement=document.getElementById("quiz_chap_name");
    let inputElement=document.getElementById("quiz_chap_id");
    selectElement.addEventListener("change",function(){
       let selectOption=selectElement.options[selectElement.selectedIndex];
       inputElement.value=selectOption.value;
    });
});