function doGet(e) {
  return ContentService
    .createTextOutput("GAS is running");
}

function doPost(e) {
  const data = JSON.parse(e.postData.contents);

  return ContentService
    .createTextOutput(
      JSON.stringify({
        reply: data.message
      })
    )
    .setMimeType(ContentService.MimeType.JSON);
}