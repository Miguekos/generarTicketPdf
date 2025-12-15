https://wkhtmltopdf.org/usage/wkhtmltopdf.txt

descargar_reporte(val) {
  const url = `https://api.apps.com.pe/actadeservicios/${val.opera}/1`;
  var element = document.createElement("a");
  element.setAttribute("href", url);
  element.setAttribute("download", url);

  element.style.display = "none";
  document.body.appendChild(element);

  element.click();
  document.body.removeChild(element);
},