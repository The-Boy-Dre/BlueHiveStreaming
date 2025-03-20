This is a new [**React Native**](https://reactnative.dev) project, bootstrapped using [`@react-native-community/cli`](https://github.com/react-native-community/cli).

# Getting Started

> **Note**: Make sure you have completed the [Set Up Your Environment](https://reactnative.dev/docs/set-up-your-environment) guide before proceeding.

## Step 1: Start Metro

First, you will need to run **Metro**, the JavaScript build tool for React Native.

To start the Metro dev server, run the following command from the root of your React Native project:

```sh
# Using npm
npm start

# OR using Yarn
yarn start
```

## Step 2: Build and run your app

With Metro running, open a new terminal window/pane from the root of your React Native project, and use one of the following commands to build and run your Android or iOS app:

### Android

```sh
# Using npm
npm run android

# OR using Yarn
yarn android
```

### iOS

For iOS, remember to install CocoaPods dependencies (this only needs to be run on first clone or after updating native deps).

The first time you create a new project, run the Ruby bundler to install CocoaPods itself:

```sh
bundle install
```

Then, and every time you update your native dependencies, run:

```sh
bundle exec pod install
```

For more information, please visit [CocoaPods Getting Started guide](https://guides.cocoapods.org/using/getting-started.html).

```sh
# Using npm
npm run ios

# OR using Yarn
yarn ios
```

If everything is set up correctly, you should see your new app running in the Android Emulator, iOS Simulator, or your connected device.

This is one way to run your app — you can also build it directly from Android Studio or Xcode.

## Step 3: Modify your app

Now that you have successfully run the app, let's make changes!

Open `App.tsx` in your text editor of choice and make some changes. When you save, your app will automatically update and reflect these changes — this is powered by [Fast Refresh](https://reactnative.dev/docs/fast-refresh).

When you want to forcefully reload, for example to reset the state of your app, you can perform a full reload:

- **Android**: Press the <kbd>R</kbd> key twice or select **"Reload"** from the **Dev Menu**, accessed via <kbd>Ctrl</kbd> + <kbd>M</kbd> (Windows/Linux) or <kbd>Cmd ⌘</kbd> + <kbd>M</kbd> (macOS).
- **iOS**: Press <kbd>R</kbd> in iOS Simulator.

## Congratulations! :tada:

You've successfully run and modified your React Native App. :partying_face:

### Now what?

- If you want to add this new React Native code to an existing application, check out the [Integration guide](https://reactnative.dev/docs/integration-with-existing-apps).
- If you're curious to learn more about React Native, check out the [docs](https://reactnative.dev/docs/getting-started).

# Troubleshooting

If you're having issues getting the above steps to work, see the [Troubleshooting](https://reactnative.dev/docs/troubleshooting) page.

# Learn More

To learn more about React Native, take a look at the following resources:

- [React Native Website](https://reactnative.dev) - learn more about React Native.
- [Getting Started](https://reactnative.dev/docs/environment-setup) - an **overview** of React Native and how setup your environment.
- [Learn the Basics](https://reactnative.dev/docs/getting-started) - a **guided tour** of the React Native **basics**.
- [Blog](https://reactnative.dev/blog) - read the latest official React Native **Blog** posts.
- [`@facebook/react-native`](https://github.com/facebook/react-native) - the Open Source; GitHub **repository** for React Native.





============================================================================================================================
=== To setup ===
============================================================================================================================
1. npx @react-native-community/cli init FirestickStreamingApp

2. npm install @react-navigation/native @react-navigation/stack react-native-screens react-native-safe-area-context react-native-gesture-handler react-native-reanimated react-native-get-random-values react-native-tvos react-native-video axios lru-cache

3. Run the following command in your back end project folder (movie-backend):
npm install nodemon --save-dev
npm install ts-node --save-dev


============================================================================================================================
=== To RUN ===
============================================================================================================================
Run the Back End
1. npm run dev

Run the Seed Script
Ensure MongoDB is running:
1. mongod --dbpath=C:\data\db

Run the seed script:
1. npx ts-node seed.ts



Deploy the App to Fire TV - Enable Developer Options on Fire TV
5. Go to Settings > My Fire TV > About.
6. Click on Device Name 7 times until you see “You are now a developer.”

Enable ADB Debugging
7. Go to Settings > My Fire TV > Developer Options.
8. Turn on ADB Debugging.

Connect Fire TV to Your PC
9. Ensure your Fire TV and PC are on the same network.
10. Note the IP address of your Fire TV (found in Settings > My Fire TV > About > Network).

Connect via ADB:
11. run in console: adb connect <FireTV_IP>

 Run the App on Fire TV
12. npx react-native start
13. npx react-native run-android

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

============================================================================================================================
=== To Uninstall ClI ===
============================================================================================================================
1. npm uninstall -g react-native-cli
2. npm cache clean --force





web scrappers can roate their ip addresses via residential proxy networks making it look like  the traffic is from actual users

