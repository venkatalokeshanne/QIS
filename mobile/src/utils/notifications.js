import * as Notifications from 'expo-notifications'
import * as Device from 'expo-device'
import Constants from 'expo-constants'
import { Platform } from 'react-native'

// Foreground notifications (app open, on the signal-alert Watches
// list) still show a system banner + sound -- otherwise a signal that
// fires while the user happens to be looking at the app would be
// silently swallowed.
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
})

// Push notifications still work in Expo Go on iOS (unlike Android,
// where remote push was removed from Expo Go in SDK 53) -- see
// https://docs.expo.dev/push-notifications/faq/. No `projectId` is
// needed here in Expo Go; it's only required for a standalone/EAS
// build, which this app doesn't have yet.
export async function registerForPushNotificationsAsync() {
  if (!Device.isDevice) {
    throw new Error('Push notifications require a physical device (not a simulator).')
  }

  const { status: existingStatus } = await Notifications.getPermissionsAsync()
  let finalStatus = existingStatus
  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync()
    finalStatus = status
  }
  if (finalStatus !== 'granted') {
    throw new Error('Push notification permission was not granted.')
  }

  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'default',
      importance: Notifications.AndroidImportance.MAX,
    })
  }

  const projectId = Constants.expoConfig?.extra?.eas?.projectId
  const { data: token } = await Notifications.getExpoPushTokenAsync(projectId ? { projectId } : undefined)
  return token
}
