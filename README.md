# Sketching Tool

Так получилось, что на пути рисования я столкнулась с проблемой выбора. Что нарисовать? Где засекать время? Не хочу не буду, пошло оно к чёрту.
Поэтому я решила, что мне чертовски необходимо приложение, которое будет выбирать рандомную картинку и менять её через указанное время.
Так я пришла к обучению PyQt.

Изначально планировалось сделать приложение, подключающееся к Pinterest, но они изменяют сейчас своё api, и мою заявку на приложение пока что не апрувят.
Поэтому сейчас приложение умеет в следующее:
* Найти картинки в указанной папке на компьютере
* Получить от тебя таймер
* Поменять картинку по таймеру

Кроме того, приложение умеет читать картинки из Google Photos. [Авторизация](https://developers.google.com/identity/protocols/oauth2/native-app) реализована стандартной гугловской функцией: запускаем localhost, открывается браузер, авторизуешь приложение и даёшь ему разрешение на просмотр картинок ??? profit. Списано [отсюда](https://github.com/ido-ran/google-photos-api-python-quickstart/blob/master/quickstart.py).

Картинки из google photos выбираются либо по альбомам, либо по датам и категориям (можно и смешать). [Категории](https://developers.google.com/photos/library/guides/apply-filters#content-categories) жёстко заданы самим гуглом, но я правда не уверена, что они нужны все.

Больше никакой магии. Токен и разное запоминается в реестр. Тип, местоположение на экране, заданное время, последняя выбранная папка. Фильтры для gp только не сохраняются, я не решила, нужно ли это.

Внутри много шероховатостей, костылей и есть над чем рабкотать (например, я пока не разобралась, как прерывать flow подключения к гуглу, он блокирует приложение), но пока что работает -- значит работает >_<'

-----

Для сборки в запускаемый файл использовала [PyInstaller](https://habr.com/ru/post/325626/):
```
pip install pypiwin32
pip install pyinstaller

pyinstaller main.py --onefile --noconsole --icon==sketchingTool.ico
```
Это было ужасно. Когда я уже решила, что всё, готово, проблемы полезли со всех сторон.
- Во-первых, прояснилось, что нельзя просто взять и переименовать .png в .ico и всё заработает. И фотошоп сам в .ico не сохраняет. Спасибо, в интернете полно конвертеров.
- Во-вторых, нельзя просто так взять, и собрать приложение с google-api-python-client в один файл. Спасибо, что на [stackoverflow](https://stackoverflow.com/questions/29518495/pyinstaller-single-exe-of-program-which-uses-google-api-client-lib) уже потанцевали с бубном.
- В-третьих, креды из json'а тоже просто так не приклеиваются к сборке. Их нужно указывать [отдельно](https://stackoverflow.com/questions/57122622/how-to-include-json-in-executable-file-by-pyinstaller?noredirect=1&lq=1)
- И, наконец, несколько модулей в один файл собирать тоже никому не нравится. Лечится [так](https://stackoverflow.com/questions/47350078/importing-external-module-in-single-file-exe-created-with-pyinstaller)

В итоге код собирается вот так:
```
pyinstaller --additional-hooks-dir=. --hidden-import google-api-python-client --noconsole --onefile --icon="sketchingTool.ico" --add-data="secret.json;." main.py
```
Иконка в формате .png должна быть в папке с .exe.

Если что, формат secret.json:
```json
{"installed":{
  "client_id":"",
  "project_id":"",
  "auth_uri":"",
  "token_uri":"",
  "auth_provider_x509_cert_url":"",
  "client_secret":"",
  "redirect_uris":[]}}
  ```
Ещё один если что: файл .ui создаётся с помощью PyQt Designer, который выпилили из стандартной либы. Устанавливается с pyqt-tools.
Файл из .ui в .py конвертируется так:
```
pyuic5 sketchingTool.ui -o sketchingTool.py
```