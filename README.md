
============================================================================================================================
=== To setup ===
============================================================================================================================
1. npx @react-native-community/cli init FirestickStreamingApp

2. npm install @react-navigation/native @react-navigation/stack react-native-screens react-native-safe-area-context react-native-gesture-handler react-native-reanimated react-native-get-random-values react-native-tvos react-native-video axios lru-cache

3. Run the following command in your back end project folder (movie-backend):
npm install nodemon --save-dev
npm install ts-node --save-dev


============================================================================================================================
=== To RUN on Fire Stick ===
============================================================================================================================
see these  steps:
1.  enter command in in the backend's directory: "node server.js"

2.  Connecting Your Fire TV for Testing enabling Developer Options on Fire TV:
    Go to Settings > My Fire TV > Developer Options and enable ADB Debugging and Apps from Unknown Sources.

    Find Your Fire TV’s IP Address:
    (Under Settings > Network.)
    Connect via ADB in PowerShell:

3.  enter command: "adb connect <FIRE_TV_IP>:5555"

4.  verify devices:
    "adb devices"

    If the app fails to launch or connect, check your server logs (the terminal where node server.js is running).
    "adb logcat"

5.  Navigate to the Front-End Directory:
    "npx react-native run-android"


============================================================================================================================
Project Overview
============================================================================================================================
Fetch movie data from external sources (via web scraping or APIs).
Stream movies using video URLs.
Cache API responses using lru-cache to improve performance.
Use Axios for making HTTP requests.
Use a database to store user data, movie metadata, and session information.

Tech Stack
Front End: React Native (with react-native-tvos for Firestick support).
Back End: Node.js with Express.
Database: MongoDB (or any database of your choice).
Web Scraping: Cheerio or Puppeteer.
Caching: lru-cache.
HTTP Requests: Axios.

Video Streaming: react-native-video.

Without a navigation solution, your app becomes a single-screen application. For any non-trivial app like:
- A movie streaming app 📺
- A shopping app 🛒
- A messenger/chat app 💬
- A file browser 📁
…you need navigation to swap between different views and maintain a proper app state.


============================================================================================================================
Past Bug fixes
============================================================================================================================
C:\DevProjects\BlueHiveStreaming>npx react-native run-android
info Launching emulator...
info Successfully launched emulator.
info Installing the app...
> Task :gradle-plugin:settings-plugin:pluginDescriptors FAILED
2 actionable tasks: 2 executed

info 💡 Tip: Make sure that you have set up your development environment correctly, by running npx react-native doctor. To read more about doctor command visit: https://github.com/react-native-community/cli/blob/main/packages/cli-doctor/README.md#doctor


FAILURE: Build failed with an exception.

* What went wrong:
Execution failed for task ':gradle-plugin:settings-plugin:pluginDescriptors'.
> Unable to delete directory 'C:\DevProjects\BlueHiveStreaming\node_modules\@react-native\gradle-plugin\settings-plugin\build\pluginDescriptors'

* Try:
> Run with --stacktrace option to get the stack trace.
> Run with --info or --debug option to get more log output.
> Run with --scan to get full insights.
> Get more help at https://help.gradle.org.

BUILD FAILED in 7s
error Failed to install the app. Command failed with exit code 1: gradlew.bat app:installDebug -PreactNativeDevServerPort=8081 FAILURE: Build failed with an exception. * What went wrong: Execution failed for task ':gradle-plugin:settings-plugin:pluginDescriptors'. > Unable to delete directory 'C:\DevProjects\BlueHiveStreaming\node_modules\@react-native\gradle-plugin\settings-plugin\build\pluginDescriptors' * Try: > Run with --stacktrace option to get the stack trace. > Run with --info or --debug option to get more log output. > Run with --scan to get full insights. > Get more help at https://help.gradle.org. BUILD FAILED in 7s.
info Run CLI with --verbose flag for more details.

The error appeared because your project retained references to the old directory path (C:\Users\TheMo\OneDrive\...) in cached or generated Gradle and npm metadata after you moved the project. Deleting node_modules and package-lock.json cleared these stale references, and running npm install regenerated correct metadata reflecting your new directory (C:\DevProjects\BlueHiveStreaming). The gradlew clean then removed residual build artifacts, fully resetting your build environment. This sequence corrected all outdated paths, resolving the deprecation warning and build failure.

1)
cd C:\DevProjects\BlueHiveStreaming
rd /s /q node_modules

2)
del package-lock.json
npm install

3)
cd android
gradlew.bat clean
cd ..
npx react-native run-android



============================================================================================================================
=== maintenance ===
============================================================================================================================
( Clean developemnt environment )
1. npm uninstall -g react-native-cli
2. npm cache clean --force

( Clean android emulation environemnt )
1. naigate to C:\DevProjects\BlueHiveStreaming\android> 
2. run .\gradlew clean
3. navigate to C:\DevProjects\BlueHiveStreaming>  with "cd.."
4. run npx react-native run-android






web scrappers can roate their ip addresses via residential proxy networks making it look like  the traffic is from actual users

I will leave glob at version 7.2.3 as thats the version used by the react-native0tvos dependencies,
Any more code needed for glob's development on my part will make use of the latest version





Add this to your gradle.properties file in your project:

# Set Gradle cache location to shorter path
gradle.user.home=C:\\gradle_cache

# Enable long path support
org.gradle.internal.longliving.process=1
