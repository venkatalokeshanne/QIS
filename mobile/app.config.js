export default {
  expo: {
    name: 'mobile',
    // Must match the EAS project this app is linked to (see
    // extra.eas.projectId below) -- EAS resolves projects by
    // slug+projectId together and errors if they disagree.
    slug: 'qis',
    version: '1.0.0',
    orientation: 'default',
    icon: './assets/icon.png',
    userInterfaceStyle: 'dark',
    // Ties published EAS Update bundles to the app's own version field
    // rather than a separate manually-bumped number -- simplest policy
    // for a project that isn't juggling multiple native-code releases.
    runtimeVersion: {
      policy: 'appVersion',
    },
    updates: {
      // Lets Expo Go (or a future standalone build) fetch the JS bundle
      // from Expo's servers via `eas update`, instead of only being
      // reachable while this computer's own Metro dev server is running
      // on the same network -- see the "use it from anywhere" ask.
      url: 'https://u.expo.dev/463ac56d-87f5-4ae0-b17e-7e745b252b96',
    },
    ios: {
      supportsTablet: true,
    },
    android: {
      adaptiveIcon: {
        backgroundColor: '#0b0d10',
        foregroundImage: './assets/android-icon-foreground.png',
        backgroundImage: './assets/android-icon-background.png',
        monochromeImage: './assets/android-icon-monochrome.png',
      },
    },
    web: {
      favicon: './assets/favicon.png',
    },
    plugins: ['expo-font', '@react-native-community/datetimepicker', 'expo-notifications'],
    extra: {
      // Points directly at the deployed Render backend -- native RN
      // requests aren't subject to browser CORS/reverse-proxy tricks
      // like the web frontend's vercel.json rewrite, so this has to be
      // an absolute URL, not a relative '/api' path.
      apiBaseUrl: 'https://quant-platform-backend.onrender.com/api',
      eas: {
        // Required by getExpoPushTokenAsync() even inside Expo Go --
        // without a linked EAS project, push registration fails with
        // "No projectId found" and Alerts silently can't get a token.
        projectId: '463ac56d-87f5-4ae0-b17e-7e745b252b96',
      },
    },
  },
};
