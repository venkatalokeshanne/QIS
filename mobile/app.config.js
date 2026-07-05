export default {
  expo: {
    name: 'mobile',
    slug: 'mobile',
    version: '1.0.0',
    orientation: 'default',
    icon: './assets/icon.png',
    userInterfaceStyle: 'dark',
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
    },
  },
};
