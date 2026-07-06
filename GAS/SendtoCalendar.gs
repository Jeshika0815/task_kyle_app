function doPost(e) {
  try {

    const data = JSON.parse(e.postData.contents);

    const start = data.start;
    const end = data.end;
    const date = data.date;
    const time = data.time; // "09:00"

    Logger.log(date);
    Logger.log(typeof date);

    // 日付を分解
    const [year, month, day] =
      date.split("-").map(Number);

    // 時刻を分解
    const [hour, minute] =
      time.split(":").map(Number);

    // 開始時刻
    const eventStart = new Date(
      year,
      month - 1, // JavaScriptの月は0始まり
      day,
      hour,
      minute
    );

    Logger.log(eventStart);

    // 終了時刻（とりあえず1時間後）
    const eventEnd = new Date(
      eventStart.getTime() + 60 * 60 * 1000
    );

    const calendar = CalendarApp.getDefaultCalendar();

    const event = calendar.createEvent(
      "出勤",
      eventStart,
      eventEnd,
      {
        description:
          `出発地: ${start}\n` +
          `目的地: ${end}`
      }
    );

    return ContentService
      .createTextOutput(
        JSON.stringify({
          success: true,
          eventId: event.getId(),
          title: event.getTitle(),
          start: eventStart.toISOString(),
          end: eventEnd.toISOString()
        })
      )
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {

    return ContentService
      .createTextOutput(
        JSON.stringify({
          success: false,
          error: err.toString()
        })
      )
      .setMimeType(ContentService.MimeType.JSON);
  }
}